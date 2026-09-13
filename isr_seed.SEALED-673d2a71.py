#!/usr/bin/env python3
"""Portable ISR field seed: observe a repository, then leave it intelligible.

It delegates parsing to verified Tree-sitter grammars and emits searchable,
evidence-linked intelligence: files, symbols, imports, calls, dependencies,
tests, changes, contracts, capability status, and a card catalogue. Activation
reads repository source, writes only declared seed artifacts and tool handoffs,
uses the network only for hash-verified parser dependencies, and never mutates
the source it observes. It is a reconnaissance bootstrapper, not an application
framework or a universal language implementation.
"""

from __future__ import annotations

import argparse
import base64
import fnmatch
import hashlib
import importlib
import importlib.util
import inspect
import json
import os
import re
import shutil
import subprocess
import sys
import textwrap
from collections.abc import Iterator
from importlib.machinery import PathFinder
from importlib.metadata import distributions
from pathlib import Path
from typing import Any
from urllib.request import urlopen

# DNA is data, not host-specific behavior. The engine below expresses only the
# language genes whose extensions are present in the repository.
DNA_JSON = r"""
{
  "identity": {
    "name": "ISR Portable Seed",
        "genome_version": "0.3.0",
        "map_schema_version": "1.2.0"
  },
  "activation": {
    "output_dir": ".isr",
        "max_file_bytes": 2097152,
        "history_runs": 5
  },
      "runtime_package": {
            "name": "shutter.py",
            "role": "non_destructive_repository_instrumentation_runtime",
            "entrypoints": {"capture": "refresh maps", "search": "query catalogue"},
            "authority": "generated from seed during first activation",
            "writes": [".isr artifacts", "five-run history"],
            "must_not": ["activate seed", "mutate source", "emit telemetry"],
            "expand_with": ["new delegated stages", "new grammar capability", "new catalogue views"],
            "compatibility_rule": "preserve capture, search, evidence, and provenance contracts"
      },
      "execution_contract": {
                "optional_requires": "soft inputs; absence must not block the stage",
                "external_inputs": "observed inputs not produced by another stage",
                "mutates": "paths changed by the stage",
                "invalidates": "outputs made stale by a changed input",
                "evidence": "how the stage establishes its claims",
                "failure_policy": "block_downstream, emit_unknown, or emit_partial",
                "scope": "population the stage is allowed to inspect",
                "trust_tier": "provenance tier for the executable lens recipe"
        },
    "execution_matrix": [
        {"id": "inventory", "requires": ["repository"], "produces": ["inventory.json"], "feeds": ["parsing", "changes", "tests"], "evidence": "direct_filesystem_inventory", "trust_tier": "seed_generated"},
        {"id": "capability", "requires": ["inventory.json"], "produces": ["capabilities.json"], "feeds": ["parsing"], "evidence": "tree_sitter_runtime_probe", "trust_tier": "seed_generated"},
        {"id": "parsing", "requires": ["inventory.json", "capabilities.json"], "produces": ["maps/files.json", "maps/symbols.json", "maps/imports.json", "maps/calls.json", "parse_summary.json"], "feeds": ["dependencies", "catalogue"], "evidence": "tree_sitter_syntax", "trust_tier": "seed_generated"},
        {"id": "dependencies", "requires": ["maps/files.json", "maps/imports.json"], "produces": ["dependencies.json"], "feeds": ["catalogue"], "evidence": "derived_import_token_resolution", "trust_tier": "seed_generated"},
        {"id": "tests", "requires": ["inventory.json"], "produces": ["tests.json"], "feeds": ["catalogue"], "evidence": "directory_and_filename_convention", "trust_tier": "seed_generated"},
        {"id": "changes", "requires": ["maps/files.json", "dependencies.json", "prior_runs"], "produces": ["changes.json"], "feeds": ["catalogue"], "evidence": "file_hash_and_derived_impact", "trust_tier": "seed_generated"},
        {"id": "contracts", "requires": ["dna", "maps/files.json", "maps/symbols.json", "maps/imports.json", "maps/calls.json"], "produces": ["contracts.json"], "feeds": ["catalogue"], "evidence": "structural_contract_validation", "trust_tier": "seed_generated"},
        {"id": "catalogue", "requires": ["all_previous_steps"], "produces": ["card_catalogue.json", "history/runs.json", "SYSTEM_FINDINGS.md"], "feeds": ["agent"], "evidence": "derived_artifact_index", "trust_tier": "seed_generated"}
    ],
    "dependencies": {
        "registry": "https://pypi.org/pypi/{name}/{version}/json",
        "packages": [
            {"name": "tree-sitter-language-pack", "version": "0.9.1"},
            {"name": "tree-sitter", "version": "0.23.2"},
            {"name": "tree-sitter-c-sharp", "version": "0.23.1"},
            {"name": "tree-sitter-embedded-template", "version": "0.23.2"},
            {"name": "tree-sitter-yaml", "version": "0.7.0"},
            {"name": "Pygments", "version": "2.20.0"}
        ]
    },
  "terrain": {
    "exclude_directories": [
      ".git", ".hg", ".svn", ".isr", ".venv", "venv", "node_modules",
      "vendor", "dist", "build", "target", "__pycache__", ".mypy_cache",
      ".pytest_cache", ".ruff_cache", "coverage", ".next"
    ],
    "non_source_extensions": [
      ".bmp", ".gif", ".ico", ".jpeg", ".jpg", ".lock", ".pdf", ".png",
      ".pyc", ".svg", ".webp", ".woff", ".woff2", ".zip"
        ],
        "test_directories": ["test", "tests", "__tests__", "spec", "specs"],
        "test_file_patterns": [
            "test_*.*", "*_test.*", "*.test.*", "*.spec.*"
        ]
  },
  "languages": {
    "python": {
      "extensions": [".py", ".pyi"],
      "symbols": {
        "class_definition": "class",
        "function_definition": "function"
      },
      "imports": ["import_statement", "import_from_statement"],
      "calls": ["call"]
    },
    "javascript": {
      "extensions": [".js", ".jsx", ".mjs", ".cjs"],
      "symbols": {
        "class_declaration": "class",
        "function_declaration": "function",
        "generator_function_declaration": "function",
        "method_definition": "method"
      },
            "imports": ["import_statement"],
      "calls": ["call_expression", "new_expression"]
    },
    "typescript": {
      "extensions": [".ts", ".mts", ".cts"],
      "symbols": {
        "abstract_class_declaration": "class",
        "class_declaration": "class",
        "function_declaration": "function",
        "interface_declaration": "interface",
        "method_definition": "method",
        "type_alias_declaration": "type"
      },
            "imports": ["import_statement"],
      "calls": ["call_expression", "new_expression"]
    },
    "tsx": {
      "extensions": [".tsx"],
      "symbols": {
        "abstract_class_declaration": "class",
        "class_declaration": "class",
        "function_declaration": "function",
        "interface_declaration": "interface",
        "method_definition": "method",
        "type_alias_declaration": "type"
      },
            "imports": ["import_statement"],
      "calls": ["call_expression", "new_expression"]
    },
    "css": {
      "extensions": [".css"],
      "symbols": {"rule_set": "selector"},
      "imports": ["import_statement"],
      "calls": []
    },
    "rust": {
      "extensions": [".rs"],
      "symbols": {
        "const_item": "constant",
        "enum_item": "enum",
        "function_item": "function",
        "function_signature_item": "function",
        "mod_item": "module",
        "struct_item": "struct",
        "trait_item": "trait",
        "type_item": "type"
      },
      "imports": ["use_declaration", "extern_crate_declaration"],
      "calls": ["call_expression", "macro_invocation"]
    }
    }
}
"""

ARTIFACTS = (
    "inventory.json",
    "maps/files.json",
    "maps/symbols.json",
    "maps/imports.json",
    "maps/calls.json",
    "parse_summary.json",
    "dependencies.json",
    "tests.json",
    "changes.json",
    "contracts.json",
    "execution_matrix.json",
    "capabilities.json",
    "card_catalogue.json",
)


def _dna() -> dict[str, Any]:
    return json.loads(DNA_JSON)


def _find_repo_root(start: Path) -> Path:
    current = start.resolve()
    for candidate in (current, *current.parents):
        if (candidate / ".git").exists():
            return candidate
    return current


def _language_by_extension(dna: dict[str, Any]) -> dict[str, str]:
    result: dict[str, str] = {}
    for language, gene in dna["languages"].items():
        for extension in gene["extensions"]:
            result[extension.lower()] = language
    return result


def _language_for_path(path: Path, explicit: dict[str, str]) -> str | None:
    """Use Pygments' portable lexer registry before seed-specific fallback genes."""
    try:
        from pygments.lexers import ClassNotFound, get_lexer_for_filename

        aliases = get_lexer_for_filename(path.name).aliases
        if aliases and aliases[0] != "text":
            return aliases[0]
    except (ImportError, ClassNotFound):
        pass
    if path.name.lower() == "dockerfile":
        return "dockerfile"
    return explicit.get(path.suffix.lower()) or path.suffix.lower().lstrip(".") or None


def _fallback_walk_files(root: Path, output_dir: Path, dna: dict[str, Any]) -> Iterator[Path]:
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


def _candidate_files(root: Path, output_dir: Path, dna: dict[str, Any]) -> tuple[list[Path], str]:
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


def _installed_distributions(runtime_dir: Path) -> dict[str, Any]:
    return {
        _normalized_package_name(distribution.metadata["Name"]): distribution
        for distribution in distributions(path=[str(runtime_dir)])
        if distribution.metadata["Name"]
    }


def _runtime_matches_lock(runtime_dir: Path, lock: list[dict[str, str]]) -> bool:
    runtime_dir = runtime_dir.resolve()
    if not runtime_dir.exists():
        return False
    installed = _installed_distributions(runtime_dir)
    for item in lock:
        distribution = installed.get(_normalized_package_name(item["name"]))
        if distribution is None or distribution.version != item["version"] or distribution.files is None:
            return False
        for package_path in distribution.files:
            recorded_hash = package_path.hash
            if recorded_hash is None:
                continue
            installed_path = Path(distribution.locate_file(package_path)).resolve()
            if runtime_dir != installed_path and runtime_dir not in installed_path.parents:
                return False
            try:
                digest = hashlib.new(recorded_hash.mode, installed_path.read_bytes()).digest()
            except (OSError, ValueError):
                return False
            encoded_digest = base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")
            if encoded_digest != recorded_hash.value:
                return False
    return True


def _pip_command() -> list[str]:
    """Return a usable pip command for minimal Python installations."""
    if importlib.util.find_spec("pip") is None:
        completed = subprocess.run([sys.executable, "-m", "ensurepip", "--upgrade"], check=False)
        if completed.returncode != 0 or importlib.util.find_spec("pip") is None:
            raise RuntimeError("Python pip is unavailable and ensurepip could not install it")
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
            if entry.get("packagetype") == "bdist_wheel" and entry.get("digests", {}).get("sha256")
        }
        if not allowed_hashes:
            raise RuntimeError(f"no authenticated wheels published for {name}=={version}")

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
            raise RuntimeError(f"could not download one compatible wheel for {name}=={version}")
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


def _bootstrap(output_dir: Path, dependency_gene: dict[str, Any]) -> dict[str, Any]:
    runtime_dir = output_dir / "runtime"
    cache_dir = output_dir / "cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    sys.path.insert(0, str(runtime_dir))
    lock = dependency_gene["packages"]
    lock_path = output_dir / "dependency-lock.json"
    if (
        _runtime_matches_lock(runtime_dir, lock)
        and PathFinder.find_spec("tree_sitter_language_pack", [str(runtime_dir)]) is not None
    ):
        if lock_path.exists():
            return json.loads(lock_path.read_text(encoding="utf-8"))
        return {"status": "EXACT_VERSIONS_PRESENT", "packages": lock}

    print("[ISR] Downloading and verifying parser runtime inside", output_dir)
    wheels, packages = _download_verified_wheels(
        cache_dir,
        dependency_gene["registry"],
        lock,
    )
    staging_dir = output_dir / "runtime.next"
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
    if completed.returncode != 0 or not _runtime_matches_lock(staging_dir, lock):
        shutil.rmtree(staging_dir, ignore_errors=True)
        raise RuntimeError("verified parser runtime installation failed; host source was not modified")
    shutil.rmtree(runtime_dir, ignore_errors=True)
    staging_dir.replace(runtime_dir)
    importlib.invalidate_caches()
    if PathFinder.find_spec("tree_sitter_language_pack", [str(runtime_dir)]) is None:
        raise RuntimeError("parser bootstrap completed but the local runtime is unavailable")
    result = {
        "status": "VERIFIED",
        "method": "exact versions and PyPI release SHA-256 over TLS",
        "packages": packages,
    }
    _write_json(lock_path, result)
    return result


def _node_text(node: Any, source: bytes, limit: int = 240) -> str:
    text = source[node.start_byte : node.end_byte].decode("utf-8", errors="replace")
    return " ".join(text.split())[:limit]


def _node_name(node: Any, source: bytes, kind: str) -> str:
    for field in ("name", "declarator", "function"):
        child = node.child_by_field_name(field)
        if child is not None:
            return _node_text(child, source, 160)
    if kind == "selector" and node.named_children:
        return _node_text(node.named_children[0], source, 160)
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


def _extract_tree(
    root_node: Any,
    source: bytes,
    relative_path: str,
    language: str,
    gene: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    symbols: list[dict[str, Any]] = []
    imports: list[dict[str, Any]] = []
    calls: list[dict[str, Any]] = []
    symbol_types = gene.get("symbols", {})
    import_types = set(gene.get("imports", []))
    call_types = set(gene.get("calls", []))
    stack = [root_node]

    while stack:
        node = stack.pop()
        if node.type in symbol_types:
            kind = symbol_types[node.type]
            symbols.append(
                _record(
                    node,
                    relative_path,
                    language=language,
                    kind=kind,
                    name=_node_name(node, source, kind),
                )
            )
        elif not symbol_types and node.child_by_field_name("name") is not None:
            symbols.append(
                _record(
                    node,
                    relative_path,
                    language=language,
                    kind="declaration",
                    name=_node_name(node, source, "declaration"),
                    evidence="generic_syntax",
                    capability="generic_tree_sitter",
                )
            )
        if node.type in import_types:
            imports.append(
                _record(
                    node,
                    relative_path,
                    language=language,
                    syntax="native",
                    statement=_node_text(node, source),
                )
            )
        if node.type in call_types:
            target = node.child_by_field_name("function") or node.child_by_field_name("macro")
            target_text = _node_text(target, source, 160) if target else "<unresolved>"
            if language in {"javascript", "typescript", "tsx"} and target_text == "require":
                imports.append(
                    _record(
                        node,
                        relative_path,
                        language=language,
                        syntax="commonjs_require",
                        statement=_node_text(node, source),
                    )
                )
            calls.append(
                _record(
                    node,
                    relative_path,
                    language=language,
                    target=target_text,
                )
            )
        stack.extend(reversed(node.named_children))
    return symbols, imports, calls


def _discover_tests(files: list[Path], root: Path, dna: dict[str, Any]) -> list[dict[str, Any]]:
    directories = set(dna["terrain"]["test_directories"])
    patterns = tuple(dna["terrain"]["test_file_patterns"])
    language_map = _language_by_extension(dna)
    discovered = []
    for path in files:
        relative = path.relative_to(root).as_posix()
        if any(part in directories for part in path.relative_to(root).parts[:-1]) or any(
            fnmatch.fnmatch(path.name, pattern) for pattern in patterns
        ):
            discovered.append(
                {
                    "file": relative,
                    "language": _language_for_path(path, language_map),
                    "discovery": "test_directory"
                    if any(part in directories for part in path.relative_to(root).parts[:-1])
                    else "test_filename",
                }
            )
    return discovered


def _parse_file(
    path: Path,
    root: Path,
    language: str,
    gene: dict[str, Any],
    get_parser: Any,
    parsers: dict[str, Any],
    max_bytes: int,
) -> tuple[dict[str, Any] | None, list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], str | None]:
    relative_path = path.relative_to(root).as_posix()
    try:
        if get_parser is None:
            raise RuntimeError("parser runtime is unavailable")
        size = path.stat().st_size
        if size > max_bytes:
            return None, [], [], [], f"larger than {max_bytes} bytes"
        source = path.read_bytes()
        parser = parsers.get(language)
        if parser is None:
            parser = get_parser(language)
            parsers[language] = parser
        tree = parser.parse(source)
        symbols, imports, calls = _extract_tree(tree.root_node, source, relative_path, language, gene)
        record = {
            "file": relative_path,
            "language": language,
            "bytes": size,
            "sha256": hashlib.sha256(source).hexdigest(),
            "parse_status": "ERRORS_PRESENT" if tree.root_node.has_error else "PARSED",
            "evidence": "direct_hash_and_parse",
            "capability": "semantic" if gene.get("symbols") else "generic",
        }
        return record, symbols, imports, calls, None
    except Exception as error:
        return None, [], [], [], f"{type(error).__name__}: {error}"


def _negotiate_capabilities(languages: set[str], dna: dict[str, Any], get_parser: Any) -> dict[str, dict[str, str]]:
    """Probe runtime grammars once and classify the depth of each capability."""
    capabilities = {}
    for language in sorted(languages):
        profile = dna["languages"].get(language, {})
        try:
            get_parser(language)
            capabilities[language] = {
                "status": "available",
                "level": "semantic" if profile.get("symbols") else "generic",
            }
        except Exception as error:
            capabilities[language] = {
                "status": "unavailable",
                "level": "unknown",
                "reason": f"{type(error).__name__}: {error}",
            }
    return capabilities


def _lens_briefs(capabilities: dict[str, dict[str, str]], dna: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Turn observed grammar capability into the parsing lens's local instructions."""
    briefs: dict[str, dict[str, Any]] = {}
    for language, capability in capabilities.items():
        profile = dna["languages"].get(language, {})
        semantic = capability["status"] == "available" and capability["level"] == "semantic"
        briefs[language] = {
            "grammar": language,
            "status": capability["status"],
            "evidence": "tree_sitter_probe",
            "extract": {
                "symbols": profile.get("symbols", {}) if semantic else {},
                "imports": profile.get("imports", []) if semantic else [],
                "calls": profile.get("calls", []) if semantic else [],
            },
            "next_lens_question": (
                None if semantic else f"What {language} declarations, imports, and calls matter in this repository?"
            ),
        }
    return briefs


def _dependency_graph(files: list[dict[str, Any]], imports: list[dict[str, Any]]) -> dict[str, Any]:
    known_files = {item["file"] for item in files}
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
        matches: set[str] = set()
        quoted = re.findall(r"['\"]([^'\"]+)['\"]", statement)
        words = re.findall(r"[A-Za-z_][\w.-]*(?:/[\w.-]+)*", statement)
        tokens = {token.lower().replace("/", ".").lstrip(".") for token in quoted + words}
        for token in tokens:
            matches.update(lookup.get(token, ()))
        matches.discard(source)
        if matches:
            resolution = "resolved" if quoted else "inferred"
            for target in matches:
                edge = (source, target)
                edges.add(edge)
                if resolutions.get(edge) != "resolved":
                    resolutions[edge] = resolution
        else:
            unresolved.append({"file": source, "statement": statement, "evidence": "unknown"})

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
        "imports_by_file": {key: sorted(value) for key, value in sorted(imports_by_file.items())},
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
    current_files: list[dict[str, Any]], history: list[dict[str, Any]], dependencies: dict[str, Any] | None = None
) -> dict[str, Any]:
    current = {item["file"]: item["sha256"] for item in current_files}
    previous = history[-1].get("files", {}) if history else {}
    added = sorted(set(current) - set(previous))
    removed = sorted(set(previous) - set(current))
    changed = sorted(path for path in set(current) & set(previous) if current[path] != previous[path])
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


def _change_impact(changed: set[str], dependencies: dict[str, Any]) -> list[dict[str, Any]]:
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
    payload = "\n".join(f"{item['file']}\0{item['sha256']}" for item in sorted(files, key=lambda item: item["file"]))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _execution_plan(steps: list[dict[str, Any]]) -> dict[str, Any]:
    """Derive a deterministic stage order and report cycles in the matrix."""
    valid_steps = [step for step in steps if isinstance(step, dict) and isinstance(step.get("id"), str)]
    ids = {step["id"] for step in valid_steps}
    producers = {output: step["id"] for step in valid_steps for output in step.get("produces", [])}
    graph = {step_id: set() for step_id in ids}
    for step in valid_steps:
        for requirement in step.get("requires", []):
            if requirement == "all_previous_steps":
                graph[step["id"]].update(ids - {step["id"]})
                continue
            producer = producers.get(requirement)
            if producer in graph and producer != step["id"]:
                graph[step["id"]].add(producer)
    remaining = {step_id: set(dependencies) for step_id, dependencies in graph.items()}
    order: list[str] = []
    while remaining:
        ready = sorted(step_id for step_id, dependencies in remaining.items() if not dependencies)
        if not ready:
            break
        order.extend(ready)
        for step_id in ready:
            remaining.pop(step_id)
        for dependencies in remaining.values():
            dependencies.difference_update(ready)
    cycles = sorted(remaining)
    return {"status": "PASS" if not cycles else "FAIL", "order": order, "cycles": cycles}


def _trust_report(root: Path, output_dir: Path, dependency_provenance: dict[str, Any]) -> dict[str, Any]:
    """Describe the seed's authority, network use, and write boundary."""
    return {
        "source_read_scope": str(root),
        "write_scope": {
            "artifacts": str(output_dir),
            "tool_wrappers": [str(root / "capture"), str(root / "search")],
            "runtime": str(output_dir / "shutter.py"),
            "agent_instructions": str(root / "AGENTS.md"),
            "agent_instructions_policy": "create_if_absent",
        },
        "host_source_mutated": False,
        "repository_root_files_created": ["capture", "search", "AGENTS.md if absent"],
        "network_used_for_dependencies": dependency_provenance.get("status")
        not in {"NOT_REQUIRED", "EXACT_VERSIONS_PRESENT"},
        "dependency_verification": dependency_provenance.get("method", dependency_provenance.get("status")),
        "telemetry": "none",
        "evidence": "declared_execution_boundary",
    }


def _stable_fingerprint(value: Any) -> str:
    """Hash deterministic intelligence while ignoring run timestamps."""
    text = json.dumps(value, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _validate_contracts(
    dna: dict[str, Any],
    files: list[dict[str, Any]],
    artifacts: list[str],
) -> dict[str, Any]:
    steps = dna.get("execution_matrix", [])
    plan = _execution_plan(steps)
    contract_fields = set(dna.get("execution_contract", {}))
    runtime_package = dna.get("runtime_package", {})
    step_ids = {step.get("id") for step in steps if isinstance(step, dict)}
    produced = {output for step in steps if isinstance(step, dict) for output in step.get("produces", [])}
    vocabulary = (
        {
            "repository",
            "language_genes",
            "prior_runs",
            "test_patterns",
            "dna",
            "artifacts",
            "agent",
            "all_previous_steps",
        }
        | produced
        | step_ids
    )
    checks = {
        "dna_identity": bool(dna.get("identity", {}).get("genome_version")),
        "dna_execution_matrix": bool(steps),
        "execution_plan_valid": plan["status"] == "PASS",
        "execution_steps_well_formed": all(
            isinstance(step, dict)
            and step.get("id")
            and isinstance(step.get("requires"), list)
            and isinstance(step.get("produces"), list)
            and isinstance(step.get("feeds"), list)
            and isinstance(step.get("evidence"), str)
            and step.get("trust_tier") in {"seed_generated", "local_extension", "reviewed_local"}
            for step in steps
        ),
        "execution_contract_defined": contract_fields
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
        "runtime_package_defined": {
            "name",
            "role",
            "entrypoints",
            "authority",
            "writes",
            "must_not",
            "expand_with",
            "compatibility_rule",
        }
        <= set(runtime_package),
        "execution_ids_unique": len(step_ids) == len(steps),
        "execution_references_known": all(
            reference in vocabulary
            for step in steps
            if isinstance(step, dict)
            for field in ("requires", "feeds")
            for reference in step.get(field, [])
        ),
        "unique_files": len({item["file"] for item in files}) == len(files),
        "file_records_have_hashes": all(item.get("sha256") for item in files),
        "artifact_names_unique": len(set(artifacts)) == len(artifacts),
    }
    return {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "execution_plan": plan,
        "artifacts": sorted(artifacts),
        "failure_count": sum(not value for value in checks.values()),
    }


def _write_tool_installer(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    shell_installer = output_dir / "Install_tools.sh"
    shell_installer.write_text(
        "#!/bin/sh\n"
        "set -eu\n"
        'ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)\n'
        "PYTHON=${PYTHON:-python3}\n"
        "cat > \"$ROOT/capture\" <<'EOF_CAPTURE'\n"
        "#!/bin/sh\n"
        'ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)\n'
        'exec "${PYTHON:-python3}" "$ROOT/.isr/shutter.py" capture "$@"\n'
        "EOF_CAPTURE\n"
        "cat > \"$ROOT/search\" <<'EOF_SEARCH'\n"
        "#!/bin/sh\n"
        'ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)\n'
        'exec "${PYTHON:-python3}" "$ROOT/.isr/search.py" "$@"\n'
        "EOF_SEARCH\n"
        "cat > \"$ROOT/verify\" <<'EOF_VERIFY'\n"
        "#!/bin/sh\n"
        'ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)\n'
        'exec "${PYTHON:-python3}" "$ROOT/.isr/verify.py" "$@"\n'
        "EOF_VERIFY\n"
        'chmod +x "$ROOT/capture" "$ROOT/search" "$ROOT/verify"\n'
        "printf '%s\\n' 'Installed ./capture, ./search, and ./verify'\n",
        encoding="utf-8",
    )
    shell_installer.chmod(0o755)
    (output_dir / "install_tools.ps1").write_text(
        "$root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path\n"
        "$python = if ($env:PYTHON) { $env:PYTHON } else { 'python' }\n"
        '$capture = "@echo off`r`n`"$python`" `"%~dp0.isr\\shutter.py`" capture %*`r`n"\n'
        '$search = "@echo off`r`n`"$python`" `"%~dp0.isr\\search.py`" %*`r`n"\n'
        '$verify = "@echo off`r`n`"$python`" `"%~dp0.isr\\verify.py`" %*`r`n"\n'
        "Set-Content -Path (Join-Path $root 'capture.cmd') -Value $capture -NoNewline\n"
        "Set-Content -Path (Join-Path $root 'search.cmd') -Value $search -NoNewline\n"
        "Set-Content -Path (Join-Path $root 'verify.cmd') -Value $verify -NoNewline\n"
        "Write-Output 'Installed capture.cmd, search.cmd, and verify.cmd'\n",
        encoding="utf-8",
    )
    (output_dir / "install_tools.py").write_text(
        "#!/usr/bin/env python3\n"
        '"""Install ISR capture and search launchers for the current platform."""\n'
        "import os\nfrom pathlib import Path\nimport subprocess\nimport sys\n\n"
        "ROOT = Path(__file__).resolve().parents[1]\n"
        "if os.name == 'nt':\n"
        "    raise SystemExit(subprocess.run(['powershell', '-ExecutionPolicy', 'Bypass', '-File', str(Path(__file__).with_name('install_tools.ps1'))], cwd=ROOT).returncode)\n"
        "raise SystemExit(subprocess.run(['sh', str(Path(__file__).with_name('Install_tools.sh'))], cwd=ROOT).returncode)\n",
        encoding="utf-8",
    )
    (output_dir / "install_tools.py").chmod(0o755)


def _write_runtime(output_dir: Path) -> None:
    """Write a parent-style shutter: discover contracts and run lens scripts."""
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "shutter.py").write_text(
        "#!/usr/bin/env python3\n"
        '"""Non-destructive ISR instrumentation shutter grown by isr_seed.py."""\n'
        "import ast\n"
        "from pathlib import Path\n"
        "import os\n"
        "import subprocess\n"
        "import sys\n"
        "ROOT = Path(__file__).resolve().parents[1]\n"
        "if sys.argv[1:] != ['capture']:\n"
        "    raise SystemExit('shutter accepts only capture')\n"
        "lenses = []\n"
        "for path in sorted((ROOT / '.isr' / 'lenses').glob('*.py')):\n"
        "    tree = ast.parse(path.read_text(encoding='utf-8'))\n"
        "    assignment = next(node for node in tree.body if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == 'LENS' for target in node.targets))\n"
        "    lenses.append((ast.literal_eval(assignment.value), path))\n"
        "produced = {artifact: lens['id'] for lens, _ in lenses for artifact in lens['produces']}\n"
        "pending = {lens['id']: {produced[item] for item in lens['requires'] if item in produced} for lens, _ in lenses}\n"
        "identifiers = set(pending)\n"
        "for lens, _ in lenses:\n"
        "    if 'all_previous_steps' in lens['requires']: pending[lens['id']].update(identifiers - {lens['id']})\n"
        "order = []\n"
        "while pending:\n"
        "    ready = sorted(identifier for identifier, needs in pending.items() if not needs)\n"
        "    if not ready: raise SystemExit(f'lens dependency cycle: {sorted(pending)}')\n"
        "    order.extend(ready)\n"
        "    for identifier in ready: pending.pop(identifier)\n"
        "    for needs in pending.values(): needs.difference_update(ready)\n"
        "by_id = {lens['id']: path for lens, path in lenses}\n"
        "environment = os.environ | {'ISR_ROOT': str(ROOT)}\n"
        "for identifier in order:\n"
        "    result = subprocess.run([sys.executable, str(by_id[identifier])], cwd=ROOT, env=environment, check=False)\n"
        "    if result.returncode: raise SystemExit(result.returncode)\n"
        "raise SystemExit(0)\n",
        encoding="utf-8",
    )
    (output_dir / "shutter.py").chmod(0o755)


def _write_search_recipe(output_dir: Path) -> None:
    """Write the independent catalogue-query recipe used by ./search."""
    output_dir.mkdir(parents=True, exist_ok=True)
    helpers = inspect.getsource(_search_cards) + "\n\n" + inspect.getsource(_matches_expression)
    (output_dir / "search.py").write_text(
        "#!/usr/bin/env python3\n"
        '"""ISR catalogue query recipe."""\n'
        "from pathlib import Path\nimport json\nimport re\nimport sys\nfrom typing import Any\n\n"
        "ROOT = Path(__file__).resolve().parents[1]\n" + helpers + "\n\n"
        "catalogue = ROOT / '.isr' / 'card_catalogue.json'\n"
        "if not catalogue.exists(): raise SystemExit('no catalogue; run capture first')\n"
        "value = json.loads(catalogue.read_text(encoding='utf-8'))\n"
        "terms = sys.argv[1:]\n"
        "mode = terms[0].lower() if terms and terms[0].lower() in {'file', 'symbol', 'test', 'import', 'call', 'dependency', 'stats'} else 'all'\n"
        "query = ' '.join(terms[1:] if mode != 'all' else terms).lower()\n"
        "if mode == 'stats': print(json.dumps({'summary': value.get('summary', {}), 'card_counts': value.get('card_counts', {})}, indent=2)); raise SystemExit(0)\n"
        "try: print(json.dumps({'query': query, 'matches': _search_cards(value, mode, query)}, indent=2))\n"
        "except ValueError as error: print(f'[ISR] Invalid query: {error}', file=sys.stderr); raise SystemExit(2)\n",
        encoding="utf-8",
    )
    (output_dir / "search.py").chmod(0o755)


def _write_verifier(output_dir: Path) -> None:
    """Write an independent proof command for the generated camera."""
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "verify.py").write_text(
        "#!/usr/bin/env python3\n"
        '"""Verify ISR contracts, generated code, artifacts, and provenance."""\n'
        "import ast\nimport hashlib\nimport json\nfrom pathlib import Path\nimport py_compile\nimport sys\n\n"
        "ROOT = Path(__file__).resolve().parents[1]\nOUT = ROOT / '.isr'\n"
        "REQUIRED = ('shutter.py', 'search.py', 'install_tools.py', 'Install_tools.sh', 'install_tools.ps1')\n"
        "EXTERNAL = {'repository', 'prior_runs', 'dna', 'all_previous_steps'}\n"
        "TRUST_TIERS = {'seed_generated', 'local_extension', 'reviewed_local'}\n"
        "checks, failures, lenses = {}, [], []\n"
        "def check(name, condition, detail=''):\n    checks[name] = bool(condition)\n    if not condition: failures.append({'check': name, 'detail': detail})\n"
        "for name in REQUIRED:\n    check(f'core:{name}', (OUT / name).is_file(), 'missing generated core file')\n"
        "for path in sorted((OUT / 'lenses').glob('*.py')):\n"
        "    try:\n"
        "        py_compile.compile(str(path), doraise=True)\n"
        "        tree = ast.parse(path.read_text(encoding='utf-8'))\n"
        "        node = next(item for item in tree.body if isinstance(item, ast.Assign) and any(isinstance(target, ast.Name) and target.id == 'LENS' for target in item.targets))\n"
        "        lens = ast.literal_eval(node.value)\n"
        "        valid = isinstance(lens, dict) and isinstance(lens.get('id'), str) and all(isinstance(lens.get(key), list) for key in ('requires', 'produces', 'feeds')) and isinstance(lens.get('evidence'), str) and lens.get('trust_tier') in TRUST_TIERS\n"
        "        check(f'lens:{path.name}:contract', valid, 'LENS must declare id, requires, produces, feeds, evidence, and trust_tier')\n"
        "        if valid: lenses.append((path, lens))\n"
        "    except Exception as error:\n        check(f'lens:{path.name}:compile', False, f'{type(error).__name__}: {error}')\n"
        "ids = [lens['id'] for _, lens in lenses]\noutputs = [output for _, lens in lenses for output in lens['produces']]\n"
        "check('lens_ids_unique', len(ids) == len(set(ids)), 'duplicate lens id')\n"
        "check('artifact_producers_unique', len(outputs) == len(set(outputs)), 'multiple lenses declare one output')\n"
        "produced = {output: lens['id'] for _, lens in lenses for output in lens['produces']}\n"
        "pending = {lens['id']: {produced[need] for need in lens['requires'] if need in produced} for _, lens in lenses}\n"
        "for _, lens in lenses:\n    if 'all_previous_steps' in lens['requires']: pending[lens['id']].update(set(pending) - {lens['id']})\n"
        "while pending:\n"
        "    ready = [identifier for identifier, needs in pending.items() if not needs]\n"
        "    if not ready: break\n"
        "    for identifier in ready: pending.pop(identifier)\n"
        "    for needs in pending.values(): needs.difference_update(ready)\n"
        "check('lens_dag_acyclic', not pending, f'cycle: {sorted(pending)}')\n"
        "for path, lens in lenses:\n"
        "    for need in lens['requires']:\n"
        "        check(f'lens:{lens[\"id\"]}:input:{need}', need in produced or need in EXTERNAL, 'undeclared input')\n"
        "    for output in lens['produces']:\n"
        "        artifact = OUT / output\n"
        "        check(f'lens:{lens[\"id\"]}:output:{output}', artifact.is_file(), 'declared output missing; run capture')\n"
        "        if artifact.is_file() and artifact.suffix == '.json':\n"
        "            try: json.loads(artifact.read_text(encoding='utf-8'))\n"
        "            except (OSError, json.JSONDecodeError) as error: check(f'artifact:{output}:json', False, str(error))\n"
        "        if artifact.is_file() and artifact.suffix == '.md':\n"
        "            check(f'artifact:{output}:text', bool(artifact.read_text(encoding='utf-8').strip()), 'empty Markdown artifact')\n"
        "report = {'status': 'PASS' if not failures else 'FAIL', 'scope': 'structural contracts and artifact integrity; not semantic claim correctness', 'root': str(ROOT), 'lens_count': len(lenses), 'lens_evidence': {lens['id']: {'evidence': lens['evidence'], 'trust_tier': lens['trust_tier']} for _, lens in lenses}, 'checks': checks, 'failures': failures, 'generated_files': {path.relative_to(OUT).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest() for path in sorted(OUT.rglob('*.py'))}}\n"
        "(OUT / 'verification.json').write_text(json.dumps(report, indent=2, sort_keys=True) + '\\n', encoding='utf-8')\n"
        "print(json.dumps(report, indent=2))\nraise SystemExit(0 if report['status'] == 'PASS' else 1)\n",
        encoding="utf-8",
    )
    (output_dir / "verify.py").chmod(0o755)


def _write_lens_package(output_dir: Path, dna: dict[str, Any]) -> None:
    """Materialize standalone lens scripts; each owns its analysis and outputs."""
    lenses_dir = output_dir / "lenses"
    lenses_dir.mkdir(parents=True, exist_ok=True)
    (lenses_dir / "NEW_LENS.py.example").write_text(
        "#!/usr/bin/env python3\n"
        '"""Copy to a .py file; shutter discovers this contract automatically."""\n'
        "import json\nimport os\nfrom pathlib import Path\n\n"
        "LENS = {\n"
        "    'id': 'your_question',\n"
        "    'requires': ['inventory.json'],\n"
        "    'produces': ['your_answer.json'],\n"
        "    'feeds': [],\n"
        "    'evidence': 'describe the direct or derived evidence used',\n"
        "    'trust_tier': 'local_extension',\n"
        "}\n\n"
        "ROOT = Path(os.environ['ISR_ROOT']).resolve()\n"
        "OUT = ROOT / '.isr'\n\n"
        "def main():\n"
        "    inventory = json.loads((OUT / 'inventory.json').read_text(encoding='utf-8'))\n"
        "    (OUT / 'your_answer.json').write_text(json.dumps({'files_seen': len(inventory['files'])}) + '\\n', encoding='utf-8')\n\n"
        "if __name__ == '__main__':\n"
        "    main()\n",
        encoding="utf-8",
    )
    lens_prelude = (
        "from __future__ import annotations\n"
        "import base64, fnmatch, hashlib, importlib, json, os, re, shutil, subprocess, sys\n"
        "from collections.abc import Iterator\nfrom datetime import datetime, timezone\n"
        "from importlib.machinery import PathFinder\nfrom importlib.metadata import distributions\n"
        "from pathlib import Path\nfrom typing import Any\nfrom urllib.request import urlopen\n\n"
        f"DNA_JSON = {DNA_JSON!r}\nARTIFACTS = {ARTIFACTS!r}\nROOT = Path(os.environ['ISR_ROOT']).resolve()\nOUT = ROOT / '.isr'\n\n"
    )
    shared_primitives = (_dna, _write_json)
    recipe_helpers = {
        "inventory": shared_primitives
        + (
            _language_by_extension,
            _language_for_path,
            _fallback_walk_files,
            _candidate_files,
            _classify_files,
            _normalized_package_name,
            _installed_distributions,
            _runtime_matches_lock,
            _pip_command,
            _download_verified_wheels,
            _bootstrap,
        ),
        "capability": shared_primitives
        + (
            _normalized_package_name,
            _installed_distributions,
            _runtime_matches_lock,
            _pip_command,
            _download_verified_wheels,
            _bootstrap,
            _negotiate_capabilities,
            _lens_briefs,
        ),
        "parsing": shared_primitives + (_node_text, _node_name, _record, _extract_tree, _parse_file),
        "dependencies": shared_primitives + (_dependency_graph,),
        "tests": shared_primitives + (_language_by_extension, _language_for_path, _discover_tests),
        "changes": shared_primitives + (_load_history, _change_graph, _change_impact),
        "contracts": shared_primitives + (_execution_plan, _validate_contracts),
        "catalogue": shared_primitives
        + (
            _load_history,
            _repository_fingerprint,
            _stable_fingerprint,
            _trust_report,
            _execution_plan,
            _write_findings,
        ),
    }
    lens_recipes = {
        "inventory": "dna = _dna(); _bootstrap(OUT, dna['dependencies']); sys.path.insert(0, str(OUT / 'runtime')); importlib.invalidate_caches(); files, mode = _candidate_files(ROOT, OUT, dna); supported, unsupported = _classify_files(files, dna)\n_write_json(OUT / 'inventory.json', {'files': [path.relative_to(ROOT).as_posix() for path in files], 'mode': mode, 'supported': [{'file': path.relative_to(ROOT).as_posix(), 'language': language} for path, language in supported], 'unsupported': unsupported})",
        "capability": "dna = _dna(); inventory = json.loads((OUT / 'inventory.json').read_text()); runtime = _bootstrap(OUT, dna['dependencies']) if inventory['supported'] else {'status': 'NOT_REQUIRED', 'packages': []}; parser = importlib.import_module('tree_sitter_language_pack').get_parser if inventory['supported'] else None; languages = _negotiate_capabilities({item['language'] for item in inventory['supported']}, dna, parser) if parser else {}\n_write_json(OUT / 'capabilities.json', {'dependency_provenance': runtime, 'languages': languages, 'lens_briefs': _lens_briefs(languages, dna)})",
        "parsing": "dna = _dna(); inventory = json.loads((OUT / 'inventory.json').read_text()); capabilities = json.loads((OUT / 'capabilities.json').read_text()); briefs = capabilities['lens_briefs']; sys.path.insert(0, str(OUT / 'runtime')); importlib.invalidate_caches(); parser = importlib.import_module('tree_sitter_language_pack').get_parser; records, parsers = {'files': [], 'symbols': [], 'imports': [], 'calls': [], 'skipped': [], 'language_counts': {}}, {}\nfor item in inventory['supported']:\n    path, language, brief = ROOT / item['file'], item['language'], briefs[item['language']]\n    if brief['status'] != 'available': records['skipped'].append({'file': item['file'], 'reason': capabilities['languages'][language]['reason']}); continue\n    record, symbols, imports, calls, error = _parse_file(path, ROOT, language, brief['extract'], parser, parsers, dna['activation']['max_file_bytes'])\n    if error or record is None: records['skipped'].append({'file': item['file'], 'reason': error or 'parser returned no file record'}); continue\n    records['files'].append(record); records['symbols'].extend(symbols); records['imports'].extend(imports); records['calls'].extend(calls); records['language_counts'][language] = records['language_counts'].get(language, 0) + 1\nfor name in ('files', 'symbols', 'imports', 'calls'): _write_json(OUT / 'maps' / f'{name}.json', {name: records[name]})\n_write_json(OUT / 'parse_summary.json', {key: records[key] for key in ('skipped', 'language_counts')})",
        "dependencies": "files = json.loads((OUT / 'maps' / 'files.json').read_text())['files']; imports = json.loads((OUT / 'maps' / 'imports.json').read_text())['imports']\n_write_json(OUT / 'dependencies.json', _dependency_graph(files, imports))",
        "tests": "dna = _dna(); files = [ROOT / item for item in json.loads((OUT / 'inventory.json').read_text())['files']]\n_write_json(OUT / 'tests.json', {'tests': _discover_tests(files, ROOT, dna)})",
        "changes": "files = json.loads((OUT / 'maps' / 'files.json').read_text())['files']; dependencies = json.loads((OUT / 'dependencies.json').read_text()); history = _load_history(OUT / 'history' / 'runs.json')\n_write_json(OUT / 'changes.json', _change_graph(files, history, dependencies))",
        "contracts": "dna = _dna(); files = json.loads((OUT / 'maps' / 'files.json').read_text())['files']\n_write_json(OUT / 'contracts.json', _validate_contracts(dna, files, list(ARTIFACTS)))",
        "catalogue": "files = json.loads((OUT / 'maps' / 'files.json').read_text())['files']; symbols = json.loads((OUT / 'maps' / 'symbols.json').read_text())['symbols']; imports = json.loads((OUT / 'maps' / 'imports.json').read_text())['imports']; calls = json.loads((OUT / 'maps' / 'calls.json').read_text())['calls']; tests = json.loads((OUT / 'tests.json').read_text())['tests']; dependencies = json.loads((OUT / 'dependencies.json').read_text()); changes = json.loads((OUT / 'changes.json').read_text()); contracts = json.loads((OUT / 'contracts.json').read_text()); capabilities = json.loads((OUT / 'capabilities.json').read_text()); matrix = {'provenance': {'generator': 'catalogue_lens'}, 'steps': _dna()['execution_matrix'], 'plan': _execution_plan(_dna()['execution_matrix'])}; _write_json(OUT / 'execution_matrix.json', matrix); cards = [{'kind': kind, 'data': {key: record[key] for key in ('file', 'line', 'name', 'target', 'statement', 'language', 'evidence') if key in record} | {'source': source, 'index': index}} for kind, records, source in (('file', files, 'maps/files.json'), ('symbol', symbols, 'maps/symbols.json'), ('import', imports, 'maps/imports.json'), ('call', calls, 'maps/calls.json'), ('test', tests, 'tests.json'), ('dependency', dependencies['edges'], 'dependencies.json')) for index, record in enumerate(records)]; summary = {'files_parsed': len(files), 'symbols': len(symbols), 'imports': len(imports), 'calls': len(calls), 'skipped_files': len(json.loads((OUT / 'parse_summary.json').read_text())['skipped'])}; catalogue = {'repository': {'name': ROOT.name, 'fingerprint': _repository_fingerprint(files)}, 'summary': summary, 'changes': changes, 'contracts': contracts, 'capabilities': capabilities, 'cards': cards, 'card_counts': {kind: sum(card['kind'] == kind for card in cards) for kind in {card['kind'] for card in cards}}, 'views': {Path(name).stem: name for name in ARTIFACTS}}\n_write_json(OUT / 'card_catalogue.json', catalogue); history = _load_history(OUT / 'history' / 'runs.json'); history.append({'run_id': datetime.now(timezone.utc).isoformat(), 'fingerprint': catalogue['repository']['fingerprint'], 'files': {item['file']: item['sha256'] for item in files}, 'summary': summary}); _write_json(OUT / 'history' / 'runs.json', history[-5:])",
    }
    lens_recipes["catalogue"] += "\n_write_findings(OUT)"
    for step in dna["execution_matrix"]:
        helper_source = "\n\n".join(inspect.getsource(helper) for helper in recipe_helpers[step["id"]])
        source = (
            '#!/usr/bin/env python3\n"""Expanded ISR lens recipe.\n\n'
            f"Question: {step['id']}\n"
            f"Inputs: {', '.join(step['requires']) or 'repository filesystem'}\n"
            f"Outputs: {', '.join(step['produces'])}\n"
            "This file is standalone after germination; its source was expanded from\n"
            'the seed recipe so it can be inspected, changed, or replaced locally.\n"""\n\n'
            + lens_prelude
            + helper_source
            + f"\n\nLENS = {step!r}\n\n"
            + "def main():\n"
            + textwrap.indent(lens_recipes[step["id"]], "    ")
            + "\n\nif __name__ == '__main__':\n    main()\n"
        )
        (lenses_dir / f"{step['id']}.py").write_text(source, encoding="utf-8")


def _write_agent_instructions(root: Path, output_dir: Path) -> None:
    instructions = (
        "# ISR Intelligence Protocol\n\n"
        "This repository carries a local evidence index. Consult it before broad source exploration; use source as the final authority.\n\n"
        "## Operating Loop\n\n"
        "1. Run `./capture` when repository intelligence may be stale.\n"
        "2. Run `./search file <term>`, `./search symbol <term>`, or `./search stats`.\n"
        "3. Follow returned paths and evidence to source.\n"
        "4. Use grep when the index explicitly reports unknown or unsupported terrain.\n\n"
        "## Trust Boundary\n\n"
        "Derived cards carry provenance and evidence status. They are navigation intelligence, not source truth.\n"
        "The seed runs once; the generated camera performs recurring non-destructive repository instrumentation.\n\n"
        "## Extension\n\n"
        "Copy `.isr/lenses/NEW_LENS.py.example` to a `.py` file, declare its `LENS` contract, evidence, and trust tier, then write its declared JSON outputs. Shutter discovers it without a registry edit.\n"
    )
    (output_dir / "AGENT_INSTRUCTIONS.md").write_text(instructions, encoding="utf-8")
    root_instructions = root / "AGENTS.md"
    if not root_instructions.exists():
        root_instructions.write_text(instructions, encoding="utf-8")


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)


def _write_findings(output_dir: Path) -> None:
    """Summarize every generated JSON artifact without assuming its schema."""
    lines = [
        "# ISR System Findings",
        "",
        "A current, schema-agnostic field report for generated repository intelligence.",
        "",
        "Each entry describes the artifact's observed shape. It is a navigation aid; source and artifact evidence remain authoritative.",
        "",
        "## Artifact Index",
        "",
    ]
    for path in sorted(output_dir.rglob("*.json")):
        relative = path.relative_to(output_dir).as_posix()
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            lines.extend((f"## `{relative}`", "", f"Unreadable JSON: `{type(error).__name__}`", ""))
            continue
        if isinstance(value, dict):
            details = [f"keys: {', '.join(sorted(value)[:12]) or 'none'}"]
            if "status" in value:
                details.append(f"status: `{value['status']}`")
            if isinstance(value.get("summary"), dict):
                details.append("summary: " + ", ".join(f"{key}={item}" for key, item in value["summary"].items()))
        elif isinstance(value, list):
            details = [f"records: {len(value)}"]
        else:
            details = [f"value type: {type(value).__name__}"]
        lines.extend((f"## `{relative}`", "", *[f"- {detail}" for detail in details], ""))
    (output_dir / "SYSTEM_FINDINGS.md").write_text("\n".join(lines), encoding="utf-8")


def _classify_files(candidate_files: list[Path], dna: dict[str, Any]) -> tuple[list[tuple[Path, str]], dict[str, int]]:
    """Assign parser capabilities and count source extensions without parsing."""
    explicit = _language_by_extension(dna)
    ignored = set(dna["terrain"]["non_source_extensions"])
    supported: list[tuple[Path, str]] = []
    unsupported: dict[str, int] = {}
    for path in candidate_files:
        language = _language_for_path(path, explicit)
        if language:
            supported.append((path, language))
        elif path.suffix and path.suffix.lower() not in ignored:
            extension = path.suffix.lower()
            unsupported[extension] = unsupported.get(extension, 0) + 1
    return supported, unsupported


def _germinate(root: Path, output_dir: Path, dna: dict[str, Any]) -> None:
    """Materialize the shutter, lenses, and small user handoff once."""
    _write_runtime(output_dir)
    _write_search_recipe(output_dir)
    _write_verifier(output_dir)
    _write_lens_package(output_dir, dna)
    for obsolete in (
        "runtime.py",
        "lens_manifest.json",
        "lens_profile.json",
        "lenses/_support.py",
        "lenses/__init__.py",
    ):
        (output_dir / obsolete).unlink(missing_ok=True)
    _write_tool_installer(output_dir)
    _write_agent_instructions(root, output_dir)


def _activation_notice(root: Path, output_dir: Path) -> str:
    return "\n".join(
        (
            "ISR Portable Seed: Informed Activation",
            "",
            "This creates a repository-local intelligence camera for evidence-led navigation.",
            f"Read scope:  {root}",
            f"Write scope: {output_dir}",
            "",
            "It will create shutter, search, verification, installer, lens, JSON, Markdown, cache, and local parser-runtime files.",
            "It may create AGENTS.md only when that file is absent.",
            "It will not modify observed source files or send telemetry.",
            "It may download exact-version Tree-sitter and Pygments wheels from PyPI over TLS, then verify published SHA-256 hashes.",
            "It will then run one non-destructive capture to create the initial intelligence artifacts.",
        )
    )


def activate(root: Path, output_name: str, *, authorized: bool = False) -> int:
    dna = _dna()
    root = _find_repo_root(root)
    output_dir = (root / output_name).resolve()
    if output_dir == root or root not in output_dir.parents:
        raise ValueError("output directory must be a dedicated directory inside the repository")
    if not authorized:
        raise PermissionError("activation requires explicit authorization")
    _germinate(root, output_dir, dna)
    result = subprocess.run(
        [sys.executable, str(output_dir / "shutter.py"), "capture"],
        cwd=root,
        check=False,
    )
    return result.returncode


def capture_run(root: Path, output_name: str = ".isr") -> int:
    """Run an existing runtime through shutter; the seed never captures directly."""
    root = _find_repo_root(root)
    runtime = root / output_name / "shutter.py"
    if not runtime.exists():
        raise RuntimeError("shutter is not germinated; run the seed with activate first")
    return subprocess.run([sys.executable, str(runtime), "capture"], cwd=root, check=False).returncode


def _search_cards(catalogue: dict[str, Any], mode: str, query: str) -> list[dict[str, Any]]:
    kinds = {
        "file": "file",
        "symbol": "symbol",
        "test": "test",
        "import": "import",
        "call": "call",
        "dependency": "dependency",
    }
    if any(operator in query.upper().split() for operator in ("AND", "OR", "NOT")) or "(" in query or ")" in query:
        return [card for card in catalogue.get("cards", []) if _matches_expression(card, query)]
    return [
        card
        for card in catalogue.get("cards", [])
        if (mode not in kinds or card["kind"] == kinds[mode])
        and query in json.dumps(card["data"], sort_keys=True).lower()
    ]


def _matches_expression(card: dict[str, Any], expression: str) -> bool:
    """Evaluate a small boolean query language over one card."""
    tokens = re.findall(r"\(|\)|\bAND\b|\bOR\b|\bNOT\b|[^\s()]+", expression, flags=re.IGNORECASE)
    if not tokens:
        raise ValueError("query is empty")
    position = 0
    data = card["data"]

    def value(token: str) -> bool:
        if ":" in token:
            field, expected = token.split(":", 1)
            actual = card.get("kind") if field.lower() == "kind" else data.get(field)
            return expected.lower() == str(actual).lower()
        return token.lower() in json.dumps(data, sort_keys=True).lower()

    def primary() -> bool:
        nonlocal position
        if position >= len(tokens):
            raise ValueError("query ends before an operand")
        token = tokens[position]
        if token == "(":
            position += 1
            result = disjunction()
            if position >= len(tokens) or tokens[position] != ")":
                raise ValueError("unclosed parenthesis")
            position += 1
            return result
        if token == ")":
            raise ValueError("unexpected closing parenthesis")
        position += 1
        return value(token)

    def negation() -> bool:
        nonlocal position
        if position < len(tokens) and tokens[position].upper() == "NOT":
            position += 1
            return not negation()
        return primary()

    def conjunction() -> bool:
        nonlocal position
        result = negation()
        while position < len(tokens) and tokens[position].upper() == "AND":
            position += 1
            right = negation()
            result = result and right
        return result

    def disjunction() -> bool:
        nonlocal position
        result = conjunction()
        while position < len(tokens) and tokens[position].upper() == "OR":
            position += 1
            right = conjunction()
            result = result or right
        return result

    result = disjunction()
    if position != len(tokens):
        raise ValueError(f"unexpected token: {tokens[position]}")
    return result


def search_catalogue(root: Path, terms: list[str]) -> int:
    """Search the regenerated card catalogue without requiring external tools."""
    output_dir = (_find_repo_root(root) / _dna()["activation"]["output_dir"]).resolve()
    catalogue_path = output_dir / "card_catalogue.json"
    if not catalogue_path.exists():
        print("[ISR] No card catalogue found. Run ./capture first.", file=sys.stderr)
        return 1
    catalogue = json.loads(catalogue_path.read_text(encoding="utf-8"))
    mode = (
        terms[0].lower()
        if terms[0].lower() in {"file", "symbol", "test", "import", "call", "dependency", "stats"}
        else "all"
    )
    query = " ".join(terms[1:] if mode != "all" else terms).lower()
    if mode == "stats":
        print(
            json.dumps(
                {"summary": catalogue.get("summary", {}), "card_counts": catalogue.get("card_counts", {})}, indent=2
            )
        )
        return 0
    try:
        matches = _search_cards(catalogue, mode, query)
    except ValueError as error:
        print(f"[ISR] Invalid query: {error}", file=sys.stderr)
        return 2
    print(json.dumps({"query": query, "matches": matches}, indent=2))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Dormant ISR seed. No files or dependencies are created without activate."
    )
    subparsers = parser.add_subparsers(dest="command")
    activate_parser = subparsers.add_parser("activate", help="germinate ISR in a repository")
    activate_parser.add_argument("--root", type=Path, default=Path.cwd())
    activate_parser.add_argument("--output", default=_dna()["activation"]["output_dir"])
    activate_parser.add_argument(
        "--yes", action="store_true", help="authorize the declared activation writes without prompting"
    )
    capture_parser = subparsers.add_parser("capture", help="refresh a germinated runtime")
    capture_parser.add_argument("--root", type=Path, default=Path.cwd())
    capture_parser.add_argument("--output", default=_dna()["activation"]["output_dir"])
    search_parser = subparsers.add_parser("search", help="search the card catalogue")
    search_parser.add_argument("terms", nargs="+")
    args = parser.parse_args(argv)
    if args.command == "search":
        return search_catalogue(Path.cwd(), args.terms)
    if args.command == "capture":
        try:
            return capture_run(args.root, args.output)
        except (OSError, RuntimeError, ValueError) as error:
            print(f"[ISR] Capture failed honestly: {error}", file=sys.stderr)
            return 1
    if args.command != "activate":
        parser.print_help()
        print("\n[ISR] Dormant. Run the activate command to create any files or install dependencies.")
        return 0
    try:
        root = _find_repo_root(args.root)
        output_dir = (root / args.output).resolve()
        if not args.yes:
            print(_activation_notice(root, output_dir))
            if input("Authorize these writes? [y/N] ").strip().lower() not in {"y", "yes"}:
                print("[ISR] Activation cancelled; no files were written.")
                return 0
        return activate(root, args.output, authorized=True)
    except (OSError, PermissionError, RuntimeError, ValueError) as error:
        print(f"[ISR] Activation failed honestly: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
