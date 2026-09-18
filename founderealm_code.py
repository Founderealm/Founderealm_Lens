"""The Founderealm Lens product: the code that is copied into a germinated tree.

Nothing here is run by the seed. Every function in this module is read with
inspect.getsource and written into the tools the seed plants, so a change here is a
change to what a repository ends up holding. The seed writes; this is what gets written.

Declarations live in lens_dna.json and reach these functions as arguments or as the
DNA each generated file carries. This module reads no configuration of its own.
"""

from __future__ import annotations

import ast
import base64
import fnmatch
import hashlib
import importlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
from collections.abc import Iterator
from datetime import datetime, timezone
from importlib.machinery import PathFinder
from importlib.metadata import PackageNotFoundError, distributions, version
from pathlib import Path
from typing import Any
from urllib.request import urlopen

def _language_for_path(path: Path, detect: Any = None) -> str | None:
    """Identify a language, precisely when a detector is available and by extension otherwise."""
    if detect is not None:
        try:
            found = detect(str(path))
        except Exception:  # Grammar detection is an optional third-party boundary.
            found = None
        if found:
            return found
    if path.name.lower() == "dockerfile":
        return "dockerfile"
    return path.suffix.lower().lstrip(".") or None

def _fallback_walk_files(
    root: Path, output_dir: Path, dna: dict[str, Any]
) -> Iterator[Path]:
    excluded = set(dna["terrain"]["exclude_directories"])
    seed_path = Path(__file__).resolve()
    for current, directories, filenames in os.walk(root, followlinks=False):
        current_path = Path(current)
        directories[:] = sorted(
            name
            for name in directories
            if name not in excluded
            and not (current_path / name).is_symlink()
            and (current_path / name).resolve() != output_dir
        )
        for filename in sorted(filenames):
            path = current_path / filename
            if path.is_symlink() or path.resolve() == seed_path:
                continue
            yield path

def _candidate_files(
    root: Path, output_dir: Path, dna: dict[str, Any]
) -> tuple[list[Path], str]:
    seed_path = Path(__file__).resolve()
    excluded = set(dna["terrain"]["exclude_directories"])
    if (root / ".git").exists():
        try:
            completed = subprocess.run(
                [
                    "git",
                    "-C",
                    str(root),
                    "ls-files",
                    "-z",
                    "--cached",
                    "--others",
                    "--exclude-standard",
                ],
                check=False,
                capture_output=True,
            )
        except OSError:
            completed = None
        if completed is not None and completed.returncode == 0:
            files: list[Path] = []
            for raw_path in completed.stdout.split(b"\0"):
                if not raw_path:
                    continue
                relative_path = Path(os.fsdecode(raw_path))
                path = (root / relative_path).resolve()
                if (
                    not excluded.intersection(relative_path.parts)
                    and path.is_file()
                    and not path.is_symlink()
                    and path != seed_path
                    and path != output_dir
                    and output_dir not in path.parents
                    and (path == root or root in path.parents)
                ):
                    files.append(path)
            return sorted(files), "git"
    return list(_fallback_walk_files(root, output_dir, dna)), "fallback_no_gitignore"

def _normalized_package_name(name: str) -> str:
    return name.lower().replace("_", "-").replace(".", "-")

def _installed_distributions(dependencies_dir: Path) -> dict[str, Any]:
    return {
        _normalized_package_name(distribution.metadata["Name"]): distribution
        for distribution in distributions(path=[str(dependencies_dir)])
        if distribution.metadata["Name"]
    }

def _dependencies_match_lock(
    dependencies_dir: Path, lock: list[dict[str, str]]
) -> bool:
    dependencies_dir = dependencies_dir.resolve()
    if not dependencies_dir.exists():
        return False
    installed = _installed_distributions(dependencies_dir)
    for item in lock:
        distribution = installed.get(_normalized_package_name(item["name"]))
        if (
            distribution is None
            or distribution.version != item["version"]
            or distribution.files is None
        ):
            return False
        for package_path in distribution.files:
            recorded_hash = package_path.hash
            if recorded_hash is None:
                continue
            installed_path = Path(distribution.locate_file(package_path)).resolve()
            if (
                dependencies_dir != installed_path
                and dependencies_dir not in installed_path.parents
            ):
                return False
            try:
                digest = hashlib.new(
                    recorded_hash.mode, installed_path.read_bytes()
                ).digest()
            except (OSError, ValueError):
                return False
            encoded_digest = (
                base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")
            )
            if encoded_digest != recorded_hash.value:
                return False
    return True

def _pip_command() -> list[str]:
    """Return a usable pip command for minimal Python installations."""
    if importlib.util.find_spec("pip") is None:
        completed = subprocess.run(
            [sys.executable, "-m", "ensurepip", "--upgrade"], check=False
        )
        if completed.returncode != 0 or importlib.util.find_spec("pip") is None:
            raise RuntimeError(
                "Python pip is unavailable and ensurepip could not install it"
            )
    return [sys.executable, "-m", "pip"]

def _download_verified_wheels(
    cache_dir: Path,
    registry_template: str,
    lock: list[dict[str, str]],
) -> tuple[list[Path], list[dict[str, str]]]:
    wheels: list[Path] = []
    provenance: list[dict[str, str]] = []
    wheels_dir = cache_dir / "verified_wheels"
    wheels_dir.mkdir(parents=True, exist_ok=True)

    for item in lock:
        name = item["name"]
        version = item["version"]
        package_dir = wheels_dir / f"{_normalized_package_name(name)}-{version}"
        shutil.rmtree(package_dir, ignore_errors=True)
        package_dir.mkdir(parents=True)
        registry_url = registry_template.format(name=name, version=version)
        with urlopen(registry_url, timeout=30) as response:  # noqa: S310
            release = json.loads(response.read().decode("utf-8"))
        allowed_hashes = {
            entry["filename"]: entry["digests"]["sha256"]
            for entry in release.get("urls", [])
            if entry.get("packagetype") == "bdist_wheel"
            and entry.get("digests", {}).get("sha256")
        }
        if not allowed_hashes:
            raise RuntimeError(
                f"no authenticated wheels published for {name}=={version}"
            )

        command = [
            *_pip_command(),
            "download",
            "--disable-pip-version-check",
            "--no-deps",
            "--only-binary=:all:",
            "--dest",
            str(package_dir),
            f"{name}=={version}",
        ]
        completed = subprocess.run(command, check=False)
        downloaded = list(package_dir.glob("*.whl"))
        if completed.returncode != 0 or len(downloaded) != 1:
            raise RuntimeError(
                f"could not download one compatible wheel for {name}=={version}"
            )
        wheel = downloaded[0]
        digest = hashlib.sha256(wheel.read_bytes()).hexdigest()
        if allowed_hashes.get(wheel.name) != digest:
            wheel.unlink(missing_ok=True)
            raise RuntimeError(f"SHA-256 verification failed for {wheel.name}")
        wheels.append(wheel)
        provenance.append(
            {
                "name": name,
                "version": version,
                "filename": wheel.name,
                "sha256": digest,
                "verified_against": registry_url,
            }
        )
    return wheels, provenance

def _environment_satisfies(lock: list[dict[str, str]]) -> bool:
    """True when the interpreter already imports every locked package at its version.

    Downloading them again into the repository would be a second copy of what is
    already importable.
    """
    for item in lock:
        try:
            present = version(item["name"])
        except PackageNotFoundError:
            return False
        if present != item["version"]:
            return False
    return True

def _bootstrap(output_dir: Path, dependency_gene: dict[str, Any]) -> dict[str, Any]:
    dependencies_dir = output_dir / "dependencies"
    cache_dir = output_dir / "cache"
    lock = dependency_gene["packages"]
    lock_path = output_dir / "dependency-lock.json"
    if _environment_satisfies(lock):
        return {"status": "PRESENT_IN_ENVIRONMENT", "packages": lock}
    sys.path.insert(0, str(dependencies_dir))
    if (
        _dependencies_match_lock(dependencies_dir, lock)
        and PathFinder.find_spec("tree_sitter_language_pack", [str(dependencies_dir)])
        is not None
    ):
        if lock_path.exists():
            return json.loads(lock_path.read_text(encoding="utf-8"))
        return {"status": "EXACT_VERSIONS_PRESENT", "packages": lock}

    print("[Founderealm] Downloading and verifying parser runtime inside", output_dir)
    wheels, packages = _download_verified_wheels(
        cache_dir,
        dependency_gene["registry"],
        lock,
    )
    staging_dir = output_dir / "dependencies.next"
    shutil.rmtree(staging_dir, ignore_errors=True)
    command = [
        *_pip_command(),
        "install",
        "--disable-pip-version-check",
        "--no-index",
        "--no-deps",
        "--target",
        str(staging_dir),
        *(str(wheel) for wheel in wheels),
    ]
    completed = subprocess.run(command, check=False)
    if completed.returncode != 0 or not _dependencies_match_lock(staging_dir, lock):
        shutil.rmtree(staging_dir, ignore_errors=True)
        raise RuntimeError(
            "verified parser dependencies installation failed; host source was not modified"
        )
    shutil.rmtree(dependencies_dir, ignore_errors=True)
    staging_dir.replace(dependencies_dir)
    shutil.rmtree(cache_dir, ignore_errors=True)
    importlib.invalidate_caches()
    if (
        PathFinder.find_spec("tree_sitter_language_pack", [str(dependencies_dir)])
        is None
    ):
        raise RuntimeError(
            "parser bootstrap completed but local dependencies are unavailable"
        )
    result = {
        "status": "VERIFIED",
        "method": "exact versions and PyPI release SHA-256 over TLS",
        "packages": packages,
    }
    _write_json(lock_path, result)
    return result

def _pack(out_dir: Path) -> Any:
    """Import the grammar pack with its cache pinned inside the output directory.

    Without this the pack caches compiled grammars under the user's home, outside the
    repository the seed declares as its only write scope.
    """
    pack = importlib.import_module("tree_sitter_language_pack")
    pack.configure(pack.PackConfig(cache_dir=str(out_dir / "grammars")))
    return pack

def _node_text(node: Any, source: bytes, limit: int = 240) -> str:
    text = source[node.start_byte : node.end_byte].decode("utf-8", errors="replace")
    return " ".join(text.split())[:limit]

def _node_name(node: Any, source: bytes, rules: dict[str, Any], depth: int = 2) -> str:
    """The declared name, from a field if the grammar uses one, else a child token.

    Some grammars wrap the named thing one level down and only the inner node carries
    the name, so the fallback descends. It returns <anonymous> rather than a node type,
    because a grammar word in the name column reads as an identifier and is not one.
    """
    for field in rules["name_fields"]:
        child = node.child_by_field_name(field)
        if child is not None:
            return _node_text(child, source, 160)
    for child in node.named_children:
        if child.type in rules["name_child_types"]:
            return _node_text(child, source, 160)
    if depth > 0:
        for child in node.named_children:
            found = _node_name(child, source, rules, depth - 1)
            if found != "<anonymous>":
                return found
    return "<anonymous>"

def _record(node: Any, relative_path: str, **values: Any) -> dict[str, Any]:
    return {
        "file": relative_path,
        "line": node.start_point[0] + 1,
        "column": node.start_point[1] + 1,
        "end_line": node.end_point[0] + 1,
        "end_column": node.end_point[1] + 1,
        "start_byte": node.start_byte,
        "end_byte": node.end_byte,
        "evidence": values.pop("evidence", "direct_syntax"),
        **values,
    }

def _symbol_kind(node_type: str, rules: dict[str, Any]) -> str | None:
    """The kind a grammar already announced in its own node type name."""
    if node_type in rules["symbol_exact"]:
        return node_type.removesuffix("_set")
    for suffix in rules["symbol_suffixes"]:
        if node_type.endswith(suffix):
            return node_type[: -len(suffix)] or node_type
    return None

def _bound_kind(value: Any, rules: dict[str, Any]) -> tuple[str, Any] | None:
    """What a binding binds, when it binds something declarable.

    Returns (kind, bound node) or None. One level of expression list is unwrapped, and a
    value that is a call is not a declaration: the call is already a call site.
    """
    if value.type in rules["binding_unwrap"] and value.named_children:
        value = value.named_children[0]
    if any(token in value.type for token in rules["value_class_contains"]):
        return "class", value
    if any(token in value.type for token in rules["value_function_contains"]):
        return "function", value
    return None

def _is_import(node_type: str, rules: dict[str, Any]) -> bool:
    # A member type names a symbol taken FROM a module, not the module, so it is not an
    # import in its own right and must not out-rank the statement that names the source.
    if node_type in rules["import_member_types"]:
        return False
    return any(token in node_type for token in rules["import_contains"])

def _innermost_import(node: Any, rules: dict[str, Any]) -> bool:
    """True when no descendant of this import node is itself an import node.

    A grouped import is a container of one node per package, as Go and Kotlin spell it.
    The innermost node is the one that names a single dependency.
    """
    stack = list(node.named_children)
    while stack:
        child = stack.pop()
        if _is_import(child.type, rules) and not child.type.endswith(
            tuple(rules["skip_suffixes"])
        ):
            return False
        stack.extend(child.named_children)
    return True

def _is_call(node_type: str, rules: dict[str, Any]) -> bool:
    return node_type in rules["call_exact"] or any(
        token in node_type for token in rules["call_contains"]
    )

def _extract_tree(
    root_node: Any,
    source: bytes,
    relative_path: str,
    language: str,
    rules: dict[str, Any],
) -> tuple[
    list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], dict[str, int]
]:
    """Read symbols, imports, calls, and matched node types from one grammar."""
    symbols: list[dict[str, Any]] = []
    imports: list[dict[str, Any]] = []
    calls: list[dict[str, Any]] = []
    discovered: dict[str, int] = {}
    claimed: set = set()
    skip = tuple(rules["skip_suffixes"])
    # Import containers nest, so only the innermost import is recorded: it is the one
    # that names a single dependency. Calls are left to nest, because f(g(x)) is two.
    stack = list(reversed(root_node.named_children))

    while stack:
        node = stack.pop()
        node_type = node.type

        if not node_type.endswith(skip) and not any(
            token in node_type for token in rules["skip_contains"]
        ):
            if _is_import(node_type, rules):
                if _innermost_import(node, rules):
                    imports.append(
                        _record(
                            node,
                            relative_path,
                            language=language,
                            syntax=node_type,
                            statement=_node_text(node, source),
                        )
                    )
                    discovered[node_type] = discovered.get(node_type, 0) + 1
            elif _is_call(node_type, rules):
                target = next(
                    (
                        found
                        for field in rules["callee_fields"]
                        if (found := node.child_by_field_name(field)) is not None
                    ),
                    None,
                )
                target_text = (
                    _node_text(target, source, 160) if target else "<unresolved>"
                )
                if target_text.split(".")[-1] in rules["import_callees"]:
                    imports.append(
                        _record(
                            node,
                            relative_path,
                            language=language,
                            syntax=f"call:{target_text}",
                            statement=_node_text(node, source),
                        )
                    )
                    discovered[f"call:{target_text}"] = (
                        discovered.get(f"call:{target_text}", 0) + 1
                    )
                calls.append(
                    _record(node, relative_path, language=language, target=target_text)
                )
                discovered[node_type] = discovered.get(node_type, 0) + 1
            elif node_type in rules["binding_types"]:
                value = next(
                    (
                        found
                        for field in rules["binding_value_fields"]
                        if (found := node.child_by_field_name(field)) is not None
                    ),
                    None,
                )
                bound = _bound_kind(value, rules) if value is not None else None
                if bound is not None:
                    kind, value_node = bound
                    name = next(
                        (
                            _node_text(found, source, 160)
                            for field in rules["binding_name_fields"]
                            if (found := node.child_by_field_name(field)) is not None
                        ),
                        "<anonymous>",
                    )
                    symbols.append(
                        _record(
                            node,
                            relative_path,
                            language=language,
                            kind=kind,
                            name=name,
                            evidence="derived_binding",
                        )
                    )
                    discovered[f"bind:{node_type}"] = (
                        discovered.get(f"bind:{node_type}", 0) + 1
                    )
                    # Reported once, under the name it was given. The body is still
                    # walked, so declarations inside it are still found.
                    claimed.add(value_node.id)
            elif node_type not in rules["binding_wrappers"] and node.id not in claimed:
                kind = _symbol_kind(node_type, rules)
                if kind is not None:
                    symbols.append(
                        _record(
                            node,
                            relative_path,
                            language=language,
                            kind=kind,
                            name=_node_name(node, source, rules),
                            evidence="derived_node_type",
                        )
                    )
                    discovered[node_type] = discovered.get(node_type, 0) + 1

        stack.extend(reversed(node.named_children))
    return symbols, imports, calls, discovered

def _discover_tests(
    files: list[Path], root: Path, dna: dict[str, Any]
) -> list[dict[str, Any]]:
    directories = set(dna["terrain"]["test_directories"])
    patterns = tuple(dna["terrain"]["test_file_patterns"])
    discovered = []
    for path in files:
        relative = path.relative_to(root).as_posix()
        if any(
            part in directories for part in path.relative_to(root).parts[:-1]
        ) or any(fnmatch.fnmatch(path.name, pattern) for pattern in patterns):
            discovered.append(
                {
                    "file": relative,
                    "language": _language_for_path(path),
                    "discovery": "test_directory"
                    if any(
                        part in directories
                        for part in path.relative_to(root).parts[:-1]
                    )
                    else "test_filename",
                }
            )
    return discovered

def _parse_file(
    path: Path,
    root: Path,
    language: str,
    rules: dict[str, Any],
    get_parser: Any,
    parsers: dict[str, Any],
) -> tuple[dict[str, Any] | None, list, list, list, dict[str, int], str | None]:
    relative_path = path.relative_to(root).as_posix()
    try:
        if get_parser is None:
            raise RuntimeError("parser runtime is unavailable")
        size = path.stat().st_size
        source = path.read_bytes()
        parser = parsers.get(language)
        if parser is None:
            parser = get_parser(language)
            parsers[language] = parser
        tree = parser.parse(source)
        symbols, imports, calls, discovered = _extract_tree(
            tree.root_node, source, relative_path, language, rules
        )
        record = {
            "file": relative_path,
            "language": language,
            "bytes": size,
            "sha256": hashlib.sha256(source).hexdigest(),
            "parse_status": "ERRORS_PRESENT" if tree.root_node.has_error else "PARSED",
            "evidence": "direct_hash_and_parse",
            "capability": "derived_node_type",
        }
        return record, symbols, imports, calls, discovered, None
    except Exception as error:
        return None, [], [], [], {}, f"{type(error).__name__}: {error}"

def _negotiate_capabilities(
    languages: set[str], get_parser: Any
) -> dict[str, dict[str, str]]:
    """Probe each grammar once and record whether it loaded, with the reason if not."""
    capabilities = {}
    for language in sorted(languages):
        try:
            get_parser(language)
            capabilities[language] = {
                "status": "available",
                "evidence": "tree_sitter_probe",
            }
        except Exception as error:
            # A missing grammar is a fact about the format, not a failure of the run.
            text = str(error)
            reason = (
                f"not parsed: no grammar exists for {language}"
                if "not in the download manifest" in text
                else f"not parsed: grammar for {language} did not load, {type(error).__name__}: {text}"
            )
            capabilities[language] = {
                "status": "unavailable",
                "evidence": "tree_sitter_probe",
                "reason": reason,
            }
    return capabilities

def _resolve_relative(
    source: str, target: str, known: set[str], index_names: list[str]
) -> str | None:
    """Walk a written path from the file that wrote it, the way every language does.

    A quoted path beginning with a dot is an instruction from one file to another and
    can be followed exactly, which is the difference between knowing an edge and guessing
    one. Tried in order: the path, the path with any extension this repository uses, then
    the path as a directory represented by an index file.
    """
    try:
        base = (Path(source).parent / target).as_posix()
    except (ValueError, OSError):
        return None
    parts: list[str] = []
    for piece in base.split("/"):
        if piece in ("", "."):
            continue
        if piece == "..":
            if not parts:
                return None
            parts.pop()
            continue
        parts.append(piece)
    candidate = "/".join(parts)
    if candidate in known:
        return candidate
    def with_extension(stem: str) -> list[str]:
        # A bare extension only: a.ts and a.test.ts must not both answer to "a.".
        return sorted(
            found
            for found in known
            if found.startswith(stem)
            and found[len(stem) :]
            and "/" not in found[len(stem) :]
            and "." not in found[len(stem) :]
        )

    extended = with_extension(candidate + ".")
    if len(extended) == 1:
        return extended[0]
    for name in index_names:
        inside = with_extension(f"{candidate}/{name}.")
        if len(inside) == 1:
            return inside[0]
    return None


def _dependency_graph(
    files: list[dict[str, Any]],
    imports: list[dict[str, Any]],
    dna: dict[str, Any] | None = None,
) -> dict[str, Any]:
    known_files = {item["file"] for item in files}
    index_names = list(
        (dna or {}).get("terrain", {}).get("directory_index_names", ["index"])
    )
    lookup: dict[str, set[str]] = {}
    for relative in known_files:
        path = Path(relative)
        module = path.with_suffix("").as_posix()
        lookup.setdefault(path.stem.lower(), set()).add(relative)
        lookup.setdefault(module.lower().replace("/", "."), set()).add(relative)

    edges: set[tuple[str, str]] = set()
    resolutions: dict[tuple[str, str], str] = {}
    unresolved: list[dict[str, str]] = []
    imports_by_file: dict[str, list[str]] = {}
    for item in imports:
        source = item["file"]
        statement = item.get("statement", "")
        imports_by_file.setdefault(source, []).append(statement)
        quoted = re.findall(r"['\"]([^'\"]+)['\"]", statement)

        # A path written relative to this file is followed, not searched for.
        walked = {
            found
            for text in quoted
            if text.startswith(".")
            for found in [_resolve_relative(source, text, known_files, index_names)]
            if found is not None
        }
        walked.discard(source)
        if walked:
            for target in walked:
                edges.add((source, target))
                resolutions[(source, target)] = "resolved"
            continue

        # Nothing was written that could be followed, so any match is a name collision
        # until proven otherwise and is reported as the guess it is.
        matches: set[str] = set()
        words = re.findall(r"[A-Za-z_][\w.-]*(?:/[\w.-]+)*", statement)
        tokens = {
            token.lower().replace("/", ".").lstrip(".") for token in quoted + words
        }
        for token in tokens:
            matches.update(lookup.get(token, ()))
        matches.discard(source)
        if matches:
            for target in matches:
                edge = (source, target)
                edges.add(edge)
                resolutions.setdefault(edge, "inferred")
        else:
            unresolved.append(
                {"file": source, "statement": statement, "evidence": "unknown"}
            )

    adjacency = {relative: [] for relative in sorted(known_files)}
    for source, target in sorted(edges):
        adjacency[source].append(target)
    return {
        "nodes": sorted(known_files),
        "edges": [
            {
                "from": source,
                "to": target,
                "resolution": resolutions[(source, target)],
                "evidence": "derived_graph",
            }
            for source, target in sorted(edges)
        ],
        "adjacency": adjacency,
        "imports_by_file": {
            key: sorted(value) for key, value in sorted(imports_by_file.items())
        },
        "unresolved_imports": unresolved,
        "summary": {
            "nodes": len(known_files),
            "edges": len(edges),
            "unresolved_imports": len(unresolved),
        },
    }

def _load_history(history_path: Path) -> list[dict[str, Any]]:
    if not history_path.exists():
        return []
    try:
        value = json.loads(history_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    return value if isinstance(value, list) else []

def _change_graph(
    current_files: list[dict[str, Any]],
    history: list[dict[str, Any]],
    dependencies: dict[str, Any] | None = None,
) -> dict[str, Any]:
    current = {item["file"]: item["sha256"] for item in current_files}
    previous = history[-1].get("files", {}) if history else {}
    added = sorted(set(current) - set(previous))
    removed = sorted(set(previous) - set(current))
    changed = sorted(
        path for path in set(current) & set(previous) if current[path] != previous[path]
    )
    unchanged = sorted(set(current) & set(previous) - set(changed))
    impact = _change_impact(set(added) | set(changed), dependencies or {})
    return {
        "baseline_run": history[-1].get("run_id") if history else None,
        "added": added,
        "changed": changed,
        "removed": removed,
        "unchanged": unchanged,
        "impact": impact,
        "summary": {
            "added": len(added),
            "changed": len(changed),
            "removed": len(removed),
            "unchanged": len(unchanged),
        },
    }

def _change_impact(
    changed: set[str], dependencies: dict[str, Any]
) -> list[dict[str, Any]]:
    """Propagate changed files through reverse dependency edges."""
    reverse: dict[str, set[str]] = {}
    for edge in dependencies.get("edges", []):
        reverse.setdefault(edge["to"], set()).add(edge["from"])
    queue = [(path, 0) for path in sorted(changed)]
    seen = set(changed)
    impact = []
    while queue:
        path, depth = queue.pop(0)
        if depth:
            impact.append({"file": path, "depth": depth, "evidence": "derived_impact"})
        for dependent in sorted(reverse.get(path, ())):
            if dependent not in seen:
                seen.add(dependent)
                queue.append((dependent, depth + 1))
    return impact

def _repository_fingerprint(files: list[dict[str, Any]]) -> str:
    """Return a stable Merkle-like root for the ordered file/hash set."""
    payload = "\n".join(
        f"{item['file']}\0{item['sha256']}"
        for item in sorted(files, key=lambda item: item["file"])
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()

def _validate_data(files: list[dict[str, Any]]) -> dict[str, Any]:
    """Check uniqueness and hashes in the records produced by the current run."""
    duplicates = len(files) - len({item["file"] for item in files})
    unhashed = [item["file"] for item in files if not item.get("sha256")]
    checks = {
        "file_records_unique": duplicates == 0,
        "file_records_have_hashes": not unhashed,
    }
    return {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "scope": "the records produced by this run; the instrument is checked by ./verify",
        "checks": checks,
        "duplicate_file_records": duplicates,
        "records_without_a_hash": unhashed[:20],
        "failure_count": sum(not value for value in checks.values()),
    }

def _run_capture(root: Path, out_name: str) -> int:
    """Discover lens contracts, order runnable stages, and report blocked outputs."""
    import ast

    out = root / out_name
    lenses = []
    for path in sorted((out / "lenses").glob("*.py")):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
            node = next(
                item
                for item in tree.body
                if isinstance(item, ast.Assign)
                and any(
                    isinstance(target, ast.Name) and target.id == "LENS"
                    for target in item.targets
                )
            )
            lenses.append((ast.literal_eval(node.value), path))
        except (OSError, SyntaxError, StopIteration, ValueError) as error:
            print(
                f"[Founderealm] {path.name} carries no readable LENS contract, not run: {error}"
            )

    produced = {
        artifact: lens["id"] for lens, _ in lenses for artifact in lens["produces"]
    }
    external = {
        "repository",
        "prior_runs",
        "dna",
        "lens_plan.json",
        "all_previous_steps",
    }

    blocked: dict[str, list] = {}
    for lens, _ in lenses:
        optional = set(lens.get("optional_requires", []))
        unmet = [
            need
            for need in lens["requires"]
            if need not in produced and need not in external and need not in optional
        ]
        if unmet:
            blocked[lens["id"]] = [f"no present lens produces {need}" for need in unmet]
    # Blocking is transitive: a lens reading a blocked lens's output cannot run.
    spreading = True
    while spreading:
        spreading = False
        for lens, _ in lenses:
            if lens["id"] in blocked:
                continue
            upstream = [
                produced[need]
                for need in lens["requires"]
                if need in produced and produced[need] in blocked
            ]
            if upstream:
                blocked[lens["id"]] = [
                    f"upstream {name} is blocked" for name in sorted(set(upstream))
                ]
                spreading = True

    pending = {
        lens["id"]: {produced[need] for need in lens["requires"] if need in produced}
        for lens, _ in lenses
        if lens["id"] not in blocked
    }
    for lens, _ in lenses:
        if lens["id"] in pending and "all_previous_steps" in lens["requires"]:
            pending[lens["id"]].update(set(pending) - {lens["id"]})
    for needs in pending.values():
        needs.difference_update(blocked)

    order: list = []
    while pending:
        ready = sorted(name for name, needs in pending.items() if not needs)
        if not ready:
            print(f"[Founderealm] lens dependency cycle, nothing ran: {sorted(pending)}")
            return 1
        order.extend(ready)
        for name in ready:
            pending.pop(name)
        for needs in pending.values():
            needs.difference_update(ready)

    # Written by the seed or the bootstrap, not by a lens, so absence from any
    # `produces` list is correct and not a finding.
    seed_owned = {
        "lens_plan.json",
        "dependency-lock.json",
        "verification.json",
    }
    orphans = sorted(
        relative
        for relative in (
            path.relative_to(out).as_posix() for path in out.rglob("*.json")
        )
        if relative not in produced
        and not relative.startswith(
            ("dependencies/", "dependencies.next/", "cache/", "grammars/")
        )
        and relative not in seed_owned
    )

    (out / "lens_plan.json").write_text(
        json.dumps(
            {
                "provenance": {"generator": "capture", "evidence": "discovered_lens_contracts"},
                "steps": [lens for lens, _ in lenses],
                "order": order,
                "blocked": blocked,
                "orphans": orphans,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    by_id = {lens["id"]: path for lens, path in lenses}
    environment = os.environ | {
        "FOUNDEREALM_ROOT": str(root),
        "PYTHONDONTWRITEBYTECODE": "1",
    }
    for identifier in order:
        result = subprocess.run(
            [sys.executable, str(by_id[identifier])],
            cwd=root,
            env=environment,
            check=False,
        )
        if result.returncode:
            print(
                f"[Founderealm] {identifier} exited {result.returncode}; stages after it did not run"
            )
            return result.returncode

    print(f"[Founderealm] {len(order)} lens(es) ran: {', '.join(order)}")
    for identifier, reasons in sorted(blocked.items()):
        print(f"[Founderealm] BLOCKED {identifier}: {'; '.join(reasons)}")
    if orphans:
        print(f"[Founderealm] ORPHANED, produced by no present lens: {', '.join(orphans)}")
    return 0

def _connect_tables(out_dir: Path, views: dict) -> tuple[Any, list]:
    """Materialize every present artifact as a table, then switch file access off.

    Tables and not views, because a view stays lazy and would keep reading the disk
    after the lock. An absent artifact leaves its table uncreated rather than empty.
    """
    import duckdb

    connection = duckdb.connect()
    absent = []
    for name, spec in views.items():
        path = out_dir / spec["artifact"]
        if not path.is_file():
            absent.append(name)
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(payload, dict):
                raise TypeError(f"{spec['artifact']} is not an object of collections")
            if not payload.get(spec["collection"]):
                connection.execute(f'CREATE TABLE "{name}" ({spec["columns"]})')
                continue
            connection.execute(
                f'CREATE TABLE "{name}" AS SELECT unnest({spec["collection"]}, '
                f"recursive := true) FROM read_json_auto('{path}')"
            )
        # Any failure of one view, including a malformed declaration, leaves that table
        # absent and named. The declarations are editable, so a mistake in one must not
        # take down every other answer.
        except Exception as error:  # noqa: BLE001
            absent.append(f"{name} ({type(error).__name__}: {error})")
    connection.execute("SET enable_external_access=false")
    return connection, absent

def _query(connection: Any, views: dict, absent: list, argv: list) -> int:
    """One SELECT, a plain term, or the table list. A caveat travels with the answer."""
    import duckdb

    if not argv or argv[0] in ("-h", "--help", "views"):
        print('./search "SELECT ..."   one SELECT across the tables below')
        print(
            "./search <term>         that term across files, symbols, imports and calls"
        )
        print("./search views          this list\n")
        for name, spec in views.items():
            if any(entry.split(" ")[0] == name for entry in absent):
                print(f"  {name:11} ABSENT - run ./capture")
                continue
            rows = connection.execute(f'SELECT count(*) FROM "{name}"').fetchone()[0]
            columns = [
                d[0]
                for d in connection.execute(
                    f'SELECT * FROM "{name}" LIMIT 0'
                ).description
            ]
            print(f"  {name:11} {rows:>6} rows   {spec['grain']}")
            print(f"              columns: {', '.join(columns)}")
            print(f"              CAVEAT: {spec['caveat']}\n")
        return 0

    request = " ".join(argv)
    term = None
    # The engine classifies the statement; a prefix test cannot.
    try:
        statements = duckdb.extract_statements(request)
    except duckdb.Error:
        statements = []
    if statements:
        if len(statements) != 1 or statements[0].type.name != "SELECT":
            kind = " then ".join(statement.type.name for statement in statements)
            print(
                f"[Founderealm] One SELECT only; the engine read this as {kind}.",
                file=sys.stderr,
            )
            return 2
        sql = request
    else:
        term = request.replace("'", "")
        sql = (
            "SELECT 'symbol' AS found_in, file, line, name AS detail FROM symbol "
            f"WHERE name ILIKE '%{term}%' UNION ALL "
            "SELECT 'import', file, line, statement FROM import "
            f"WHERE statement ILIKE '%{term}%' UNION ALL "
            "SELECT 'call', file, line, target FROM call "
            f"WHERE target ILIKE '%{term}%' UNION ALL "
            "SELECT 'file', file, NULL, language FROM file "
            f"WHERE file ILIKE '%{term}%' ORDER BY 1, 2, 3"
        )

    try:
        cursor = connection.execute(sql)
    except duckdb.Error as error:
        print(f"[Founderealm] {type(error).__name__}: {error}", file=sys.stderr)
        if absent:
            print(f"[Founderealm] absent tables: {absent}", file=sys.stderr)
        return 2

    names = [description[0] for description in cursor.description]
    rows = cursor.fetchall()
    print(" | ".join(names))
    print("-" * 70)
    for row in rows:
        print(" | ".join("" if value is None else str(value) for value in row))
    print(f"\n{len(rows)} row(s)" + (f" for {term!r}" if term else ""))
    # Matched on FROM and JOIN, so a caveat belongs to a table the query actually read.
    read_from = set(
        re.findall(r'(?:from|join)\s+"?([a-z_]+)"?', sql, flags=re.IGNORECASE)
    )
    for name, spec in views.items():
        if name in read_from:
            print(f"CAVEAT {name}: {spec['caveat']}")
    if absent:
        print(f"ABSENT tables, so this answer is partial (run ./capture): {absent}")
    return 0

def _verify_instrument(out_dir: Path, dna: dict[str, Any]) -> dict[str, Any]:
    """Check generated code, lens contracts, stage structure, and artifact integrity."""
    import ast as ast_module
    import py_compile

    external = {
        "repository",
        "prior_runs",
        "dna",
        "lens_plan.json",
        "all_previous_steps",
    }
    tiers = {"seed_generated", "local_extension", "reviewed_local"}
    checks: dict[str, bool] = {}
    failures: list = []

    def record(name: str, condition: Any, detail: str = "") -> None:
        checks[name] = bool(condition)
        if not condition:
            failures.append({"check": name, "detail": detail})

    for required in ("shutter.py", "search.py", "verify.py"):
        record(
            f"core:{required}",
            (out_dir / required).is_file(),
            "generated core file missing",
        )

    # the DNA itself, and the stage graph it declares
    steps = dna.get("execution_matrix", [])
    record(
        "dna:identity",
        bool(dna.get("identity", {}).get("genome_version")),
        "no genome version",
    )
    record("dna:stages_declared", bool(steps), "execution_matrix is empty")
    record(
        "dna:contract_vocabulary",
        set(dna.get("execution_contract", {}))
        >= {
            "optional_requires",
            "external_inputs",
            "mutates",
            "invalidates",
            "evidence",
            "failure_policy",
            "scope",
            "trust_tier",
        },
        "execution_contract is missing fields",
    )
    record(
        "dna:views_declared",
        bool({k for k in dna.get("views", {}) if not k.startswith("_")}),
        "no views declared, so nothing is queryable",
    )
    for name, spec in dna.get("views", {}).items():
        if name.startswith("_"):
            continue
        record(
            f"view:{name}:caveat",
            bool(spec.get("caveat")),
            "a view without a caveat hands over rows with their conditions removed",
        )

    lenses = []
    for path in sorted((out_dir / "lenses").glob("*.py")):
        try:
            py_compile.compile(str(path), doraise=True)
            node = next(
                item
                for item in ast_module.parse(path.read_text(encoding="utf-8")).body
                if isinstance(item, ast_module.Assign)
                and any(getattr(t, "id", None) == "LENS" for t in item.targets)
            )
            lens = ast_module.literal_eval(node.value)
            valid = (
                isinstance(lens, dict)
                and isinstance(lens.get("id"), str)
                and all(
                    isinstance(lens.get(key), list)
                    for key in ("requires", "produces", "feeds")
                )
                and isinstance(lens.get("evidence"), str)
                and lens.get("trust_tier") in tiers
            )
            record(
                f"lens:{path.name}:contract",
                valid,
                "LENS must declare id, requires, produces, feeds, evidence and trust_tier",
            )
            if valid:
                lenses.append((lens, path))
        except Exception as error:
            record(
                f"lens:{path.name}:compiles", False, f"{type(error).__name__}: {error}"
            )

    identifiers = [lens["id"] for lens, _ in lenses]
    outputs = [output for lens, _ in lenses for output in lens["produces"]]
    record(
        "lens_ids_unique",
        len(identifiers) == len(set(identifiers)),
        "duplicate lens id",
    )
    record(
        "artifact_producers_unique",
        len(outputs) == len(set(outputs)),
        "two lenses declare the same output",
    )

    produced = {output: lens["id"] for lens, _ in lenses for output in lens["produces"]}
    pending = {
        lens["id"]: {produced[need] for need in lens["requires"] if need in produced}
        for lens, _ in lenses
    }
    for lens, _ in lenses:
        if "all_previous_steps" in lens["requires"]:
            pending[lens["id"]].update(set(pending) - {lens["id"]})
    while pending:
        ready = [name for name, needs in pending.items() if not needs]
        if not ready:
            break
        for name in ready:
            pending.pop(name)
        for needs in pending.values():
            needs.difference_update(ready)
    record("lens_graph_acyclic", not pending, f"cycle among {sorted(pending)}")

    for lens, _ in lenses:
        optional = set(lens.get("optional_requires", []))
        for need in lens["requires"]:
            record(
                f"lens:{lens['id']}:input:{need}",
                need in produced or need in external or need in optional,
                "no lens produces this and it is not declared external or optional",
            )
        for output in lens["produces"]:
            artifact = out_dir / output
            record(
                f"lens:{lens['id']}:output:{output}",
                artifact.is_file(),
                "declared output missing; run ./capture",
            )
            if artifact.is_file() and artifact.suffix == ".json":
                try:
                    json.loads(artifact.read_text(encoding="utf-8"))
                except (OSError, ValueError) as error:
                    record(f"artifact:{output}:parses", False, str(error))
            elif artifact.is_file() and artifact.suffix == ".md":
                record(
                    f"artifact:{output}:not_empty",
                    bool(artifact.read_text(encoding="utf-8").strip()),
                    "empty document",
                )

    return {
        "status": "PASS" if not failures else "FAIL",
        "genome": dna.get("identity", {}).get("genome_version"),
        "scope": "structural contracts and artifact integrity; not semantic claim correctness",
        "lens_count": len(lenses),
        "lens_evidence": {
            lens["id"]: {"evidence": lens["evidence"], "trust_tier": lens["trust_tier"]}
            for lens, _ in lenses
        },
        "checks": checks,
        "failures": failures,
        "generated_files": {
            path.relative_to(out_dir).as_posix(): hashlib.sha256(
                path.read_bytes()
            ).hexdigest()
            for path in sorted(out_dir.rglob("*.py"))
        },
    }

def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    temporary.replace(path)

def _classify_files(
    candidate_files: list[Path], dna: dict[str, Any], detect: Any = None
) -> tuple[list[tuple[Path, str]], dict[str, int], list[dict[str, str]]]:
    """Assign parser capabilities and count source extensions without parsing.

    Files declared non-source are not parsed, which is the intent, and are returned
    named so that not parsing them is a reported decision rather than a silent one.
    """
    ignored = set(dna["terrain"]["non_source_extensions"])
    supported: list[tuple[Path, str]] = []
    unsupported: dict[str, int] = {}
    not_source: list[dict[str, str]] = []
    for path in candidate_files:
        # Extension first: a detector will name a language for any file, code or not.
        extension = path.suffix.lower()
        if extension in ignored:
            not_source.append(
                {
                    "path": path,
                    "reason": f"not parsed: {extension} is declared a non-source extension",
                }
            )
            continue
        language = _language_for_path(path, detect)
        if language:
            supported.append((path, language))
        elif path.suffix:
            unsupported[extension] = unsupported.get(extension, 0) + 1
    return supported, unsupported, not_source


# The eight starter lenses. Each is written into founderealm/lenses/<id>.py with the
# helpers its code reaches, and runs there as a standalone program. ROOT, OUT, _dna and
# _write_json are provided by the file the seed writes around it.


def lens_inventory() -> None:
    dna = _dna()
    _bootstrap(OUT, dna['dependencies'])
    sys.path.insert(0, str(OUT / 'dependencies'))
    importlib.invalidate_caches()
    files, mode = _candidate_files(ROOT, OUT, dna)
    supported, unsupported, not_source = _classify_files(files, dna, _pack(OUT).detect_language_from_path)
    _write_json(OUT / 'inventory.json', {'files': [path.relative_to(ROOT).as_posix() for path in files], 'mode': mode, 'supported': [{'file': path.relative_to(ROOT).as_posix(), 'language': language} for path, language in supported], 'unsupported': unsupported, 'not_source': [{'file': item['path'].relative_to(ROOT).as_posix(), 'reason': item['reason']} for item in not_source]})


def lens_capability() -> None:
    dna = _dna()
    inventory = json.loads((OUT / 'inventory.json').read_text())
    dependency_provenance = _bootstrap(OUT, dna['dependencies']) if inventory['supported'] else {'status': 'NOT_REQUIRED', 'packages': []}
    pack = _pack(OUT) if inventory['supported'] else None
    languages = _negotiate_capabilities({item['language'] for item in inventory['supported']}, pack.get_parser) if pack else {}
    _write_json(OUT / 'capabilities.json', {'dependency_provenance': dependency_provenance, 'languages': languages, 'syntax_rules': dna['syntax']})


def lens_parsing() -> None:
    dna = _dna()
    rules = dna['syntax']
    inventory = json.loads((OUT / 'inventory.json').read_text())
    capabilities = json.loads((OUT / 'capabilities.json').read_text())['languages']
    sys.path.insert(0, str(OUT / 'dependencies'))
    importlib.invalidate_caches()
    parser = _pack(OUT).get_parser
    records, parsers = ({'files': [], 'symbols': [], 'imports': [], 'calls': [], 'skipped': list(inventory.get('not_source', [])), 'language_counts': {}, 'discovered_node_types': {}}, {})
    for item in inventory['supported']:
        path, language = (ROOT / item['file'], item['language'])
        capability = capabilities.get(language, {})
        if capability.get('status') != 'available':
            records['skipped'].append({'file': item['file'], 'reason': capability.get('reason', 'grammar was not probed')})
            continue
        record, symbols, imports, calls, discovered, error = _parse_file(path, ROOT, language, rules, parser, parsers)
        if error or record is None:
            records['skipped'].append({'file': item['file'], 'reason': error or 'parser returned no file record'})
            continue
        records['files'].append(record)
        records['symbols'].extend(symbols)
        records['imports'].extend(imports)
        records['calls'].extend(calls)
        records['language_counts'][language] = records['language_counts'].get(language, 0) + 1
        seen = records['discovered_node_types'].setdefault(language, {})
        for node_type, count in discovered.items():
            seen[node_type] = seen.get(node_type, 0) + count
    for name in ('files', 'symbols', 'imports', 'calls'):
        _write_json(OUT / 'maps' / f'{name}.json', {name: records[name]})
    _write_json(OUT / 'parse_summary.json', {key: records[key] for key in ('skipped', 'language_counts', 'discovered_node_types')})


def lens_dependencies() -> None:
    files = json.loads((OUT / 'maps' / 'files.json').read_text())['files']
    imports = json.loads((OUT / 'maps' / 'imports.json').read_text())['imports']
    _write_json(OUT / 'dependencies.json', _dependency_graph(files, imports, _dna()))


def lens_tests() -> None:
    dna = _dna()
    files = [ROOT / item for item in json.loads((OUT / 'inventory.json').read_text())['files']]
    _write_json(OUT / 'tests.json', {'tests': _discover_tests(files, ROOT, dna)})


def lens_changes() -> None:
    files = json.loads((OUT / 'maps' / 'files.json').read_text())['files']
    dependencies = json.loads((OUT / 'dependencies.json').read_text())
    history = _load_history(OUT / 'history' / 'runs.json')
    _write_json(OUT / 'changes.json', _change_graph(files, history, dependencies))


def lens_contracts() -> None:
    files = json.loads((OUT / 'maps' / 'files.json').read_text())['files']
    _write_json(OUT / 'contracts.json', _validate_data(files))


def lens_ledger() -> None:
    files = json.loads((OUT / 'maps' / 'files.json').read_text())['files']
    plan = json.loads((OUT / 'lens_plan.json').read_text())
    matrix = {'provenance': {'generator': 'ledger_lens', 'genome': _dna()['identity']['genome_version']}, 'steps': plan['steps'], 'plan': plan['order'], 'blocked': plan['blocked'], 'orphans': plan['orphans']}
    _write_json(OUT / 'execution_matrix.json', matrix)
    summary = {'files_parsed': len(files), 'symbols': len(json.loads((OUT / 'maps' / 'symbols.json').read_text())['symbols']), 'imports': len(json.loads((OUT / 'maps' / 'imports.json').read_text())['imports']), 'calls': len(json.loads((OUT / 'maps' / 'calls.json').read_text())['calls']), 'skipped_files': len(json.loads((OUT / 'parse_summary.json').read_text())['skipped'])}
    fingerprint = _repository_fingerprint(files)
    history = _load_history(OUT / 'history' / 'runs.json')
    history.append({'run_id': datetime.now(timezone.utc).isoformat(), 'fingerprint': fingerprint, 'files': {item['file']: item['sha256'] for item in files}, 'summary': summary})
    _write_json(OUT / 'history' / 'runs.json', history[-_dna()['activation']['history_runs']:])
