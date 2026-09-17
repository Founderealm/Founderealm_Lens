#!/usr/bin/env python3
"""Portable Founderealm field seed: observe a repository, then leave it intelligible.

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

# DNA is data, not host-specific behavior.
DNA_JSON = r"""
{"identity":{"name":"Founderealm Lens","genome_version":"0.3.0","map_schema_version":"1.2.0"},"activation":{"output_dir":"founderealm","history_runs":5},"runtime_package":{"name":"shutter.py","role":"non_destructive_repository_instrumentation_runtime","entrypoints":{"capture":"refresh maps","search":"query catalogue"},"authority":"generated from seed during first activation","writes":["founderealm artifacts","five-run history"],"must_not":["activate seed","mutate source","emit telemetry"],"expand_with":["new delegated stages","new grammar capability","new catalogue views"],"compatibility_rule":"preserve capture, search, evidence, and provenance contracts"},"execution_contract":{"optional_requires":"soft inputs; absence must not block the stage","external_inputs":"observed inputs not produced by another stage","mutates":"paths changed by the stage","invalidates":"outputs made stale by a changed input","evidence":"how the stage establishes its claims","failure_policy":"block_downstream, emit_unknown, or emit_partial","scope":"population the stage is allowed to inspect","trust_tier":"provenance tier for the executable lens recipe"},"execution_matrix":[{"id":"inventory","requires":["repository"],"produces":["inventory.json"],"feeds":["parsing","changes","tests"],"evidence":"direct_filesystem_inventory","trust_tier":"seed_generated"},{"id":"capability","requires":["inventory.json"],"produces":["capabilities.json"],"feeds":["parsing"],"evidence":"tree_sitter_runtime_probe","trust_tier":"seed_generated"},{"id":"parsing","requires":["inventory.json","capabilities.json"],"produces":["maps/files.json","maps/symbols.json","maps/imports.json","maps/calls.json","parse_summary.json"],"feeds":["dependencies","catalogue"],"evidence":"tree_sitter_syntax","trust_tier":"seed_generated"},{"id":"dependencies","requires":["maps/files.json","maps/imports.json"],"produces":["dependencies.json"],"feeds":["catalogue"],"evidence":"derived_import_token_resolution","trust_tier":"seed_generated"},{"id":"tests","requires":["inventory.json"],"produces":["tests.json"],"feeds":["catalogue"],"evidence":"directory_and_filename_convention","trust_tier":"seed_generated"},{"id":"changes","requires":["maps/files.json","dependencies.json","prior_runs"],"produces":["changes.json"],"feeds":["catalogue"],"evidence":"file_hash_and_derived_impact","trust_tier":"seed_generated"},{"id":"contracts","requires":["dna","maps/files.json","maps/symbols.json","maps/imports.json","maps/calls.json"],"produces":["contracts.json"],"feeds":["catalogue"],"evidence":"structural_contract_validation","trust_tier":"seed_generated"},{"id":"ledger","requires":["all_previous_steps"],"produces":["execution_matrix.json","history/runs.json"],"feeds":["agent"],"evidence":"derived_run_record","trust_tier":"seed_generated"}],"dependencies":{"registry":"https://pypi.org/pypi/{name}/{version}/json","grammar_cache":"inside the output directory, never the user's home","packages":[{"name":"tree-sitter-language-pack","version":"1.19.0"},{"name":"tree-sitter","version":"0.26.0"},{"name":"duckdb","version":"1.5.5"}]},"views":{"file":{"artifact":"maps/files.json","collection":"files","grain":"one row per parsed file","caveat":"capability=derived_node_type means symbols, imports and calls were read from node type names rather than a curated table. parse_status=ERRORS_PRESENT means the grammar recovered from a syntax error, so records from that file may be incomplete."},"symbol":{"artifact":"maps/symbols.json","collection":"symbols","grain":"one row per declaration","caveat":"kind is the grammar's own node type with its suffix removed, so it is the grammar's vocabulary and not a normalized one: class, struct, trait and interface all appear as the language spells them. A name of <anonymous> means the grammar declared no name field and no identifier child."},"import":{"artifact":"maps/imports.json","collection":"imports","grain":"one row per import, include or require","caveat":"syntax names the node type it came from, or call:<name> when a language spells an import as a function call, as Ruby and Lua do. A grouped import, as Go and Kotlin spell one, yields one row per package rather than one row for the group."},"call":{"artifact":"maps/calls.json","collection":"calls","grain":"one row per call site","caveat":"RESOLVED BY NAME, not by receiver type. Any object's method of that name lands here, so each row is a CANDIDATE call site and not a proven edge. target=<unresolved> means the grammar put the callee somewhere none of the declared callee fields reached."},"dependency":{"artifact":"dependencies.json","collection":"edges","grain":"one row per file-to-file edge","caveat":"resolution=resolved came from a quoted path, inferred came from matching a bare token against known file stems. An inferred edge can be wrong where two files share a stem."},"unresolved":{"artifact":"dependencies.json","collection":"unresolved_imports","grain":"one row per import that matched no file in this repository","caveat":"Usually a third-party or standard-library import, which is correct and not a defect. Absence from this table is not evidence an edge was found."},"test":{"artifact":"tests.json","collection":"tests","grain":"one row per file that looks like a test","caveat":"Discovery is by DIRECTORY AND FILENAME CONVENTION ONLY. Nothing here was executed and no outcome is recorded, so this says a test exists and never that it passes."},"impact":{"artifact":"changes.json","collection":"impact","grain":"one row per file reached by a change, with its distance","caveat":"Derived by walking dependency edges backwards from changed files, so it inherits the inferred-edge caveat. depth is hops, not severity. Empty on a first run, when there is no prior run to compare against."},"skipped":{"artifact":"parse_summary.json","collection":"skipped","grain":"one row per file that was not parsed, with the reason","caveat":"A non-empty table is the honest record of a gap, not a failure of the run. Read it before treating any count as complete."}},"terrain":{"exclude_directories":[".git",".hg",".svn","founderealm",".venv","venv","node_modules","vendor","dist","build","target","__pycache__",".mypy_cache",".pytest_cache",".ruff_cache","coverage",".next"],"non_source_extensions":[".bmp",".gif",".ico",".jpeg",".jpg",".lock",".pdf",".png",".pyc",".svg",".webp",".woff",".woff2",".zip"],"test_directories":["test","tests","__tests__","spec","specs"],"test_file_patterns":["test_*.*","*_test.*","*.test.*","*.spec.*"]},"syntax":{"skip_suffixes":["_list","_block","_body","_suffix"],"skip_contains":["parameter"],"import_contains":["import","use_declaration","using_","include","require","extern_crate"],"import_member_types":["import_specifier","named_imports","import_clause","namespace_import","import_alias","import_default_specifier","import_namespace_specifier"],"callee_fields":["function","macro","method","name"],"import_callees":["require","require_relative","import_module","load"],"call_contains":["call","invocation"],"call_exact":["new_expression","macro_invocation"],"symbol_suffixes":["_definition","_declaration","_item","_specifier","_specification","_set"],"symbol_exact":["class","method","module","singleton_method","rule_set"],"binding_types":["variable_declarator","assignment","assignment_statement","var_spec","pair","field_definition","public_field_definition"],"binding_name_fields":["name","left","key"],"binding_value_fields":["value","right"],"binding_unwrap":["expression_list","parenthesized_expression"],"value_function_contains":["arrow_function","function","lambda","func_literal","closure"],"value_class_contains":["class"],"binding_wrappers":["lexical_declaration","variable_declaration","var_declaration","expression_statement"],"name_fields":["name","declarator","function","alias","path"],"name_child_types":["identifier","type_identifier","field_identifier","simple_identifier","property_identifier","constant","constructor_name"]}}
"""

# Derived from the stages, so there is one declaration of this fact rather than two.
ARTIFACTS = tuple(
    output
    for step in json.loads(DNA_JSON)["execution_matrix"]
    for output in step["produces"]
)
OUT_NAME = json.loads(DNA_JSON)["activation"]["output_dir"]


def _dna() -> dict[str, Any]:
    return json.loads(DNA_JSON)


def _find_repo_root(start: Path) -> Path:
    current = start.resolve()
    for candidate in (current, *current.parents):
        if (candidate / ".git").exists():
            return candidate
    return current


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


def _bootstrap(output_dir: Path, dependency_gene: dict[str, Any]) -> dict[str, Any]:
    dependencies_dir = output_dir / "dependencies"
    cache_dir = output_dir / "cache"
    sys.path.insert(0, str(dependencies_dir))
    lock = dependency_gene["packages"]
    lock_path = output_dir / "dependency-lock.json"
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

    Some grammars wrap the named thing one level down: Go spells a type as
    type_declaration containing type_spec, and only the inner node carries the name.
    The fallback descends rather than naming the node type, which would report a
    grammar word as if it were the identifier the reader asked for.
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

    Go and Kotlin spell a grouped import as a container of one node per package.
    Recording the container loses every package inside it; recording both counts each
    one twice. The innermost node is the one that names a single dependency.
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
            capabilities[language] = {
                "status": "unavailable",
                "evidence": "tree_sitter_probe",
                "reason": f"{type(error).__name__}: {error}",
            }
    return capabilities


def _dependency_graph(
    files: list[dict[str, Any]], imports: list[dict[str, Any]]
) -> dict[str, Any]:
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
        tokens = {
            token.lower().replace("/", ".").lstrip(".") for token in quoted + words
        }
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


def _execution_plan(steps: list[dict[str, Any]]) -> dict[str, Any]:
    """Derive a deterministic stage order and report cycles in the matrix."""
    valid_steps = [
        step
        for step in steps
        if isinstance(step, dict) and isinstance(step.get("id"), str)
    ]
    ids = {step["id"] for step in valid_steps}
    producers = {
        output: step["id"]
        for step in valid_steps
        for output in step.get("produces", [])
    }
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
        ready = sorted(
            step_id for step_id, dependencies in remaining.items() if not dependencies
        )
        if not ready:
            break
        order.extend(ready)
        for step_id in ready:
            remaining.pop(step_id)
        for dependencies in remaining.values():
            dependencies.difference_update(ready)
    cycles = sorted(remaining)
    return {
        "status": "PASS" if not cycles else "FAIL",
        "order": order,
        "cycles": cycles,
    }


def _trust_report(
    root: Path, output_dir: Path, dependency_provenance: dict[str, Any]
) -> dict[str, Any]:
    """Describe the seed's authority, network use, and write boundary."""
    return {
        "source_read_scope": str(root),
        "write_scope": {
            "artifacts": str(output_dir),
            "tool_wrappers": [
                str(root / name) for name in ("capture", "search", "verify")
            ],
            "runtime": str(output_dir / "shutter.py"),
            "instructions": str(root / "FOUNDEREALM_INSTRUCTIONS.md"),
            "instructions_policy": "create_if_absent",
        },
        "host_source_mutated": False,
        "repository_root_files_created": [
            "capture",
            "search",
            "verify",
            "FOUNDEREALM_INSTRUCTIONS.md if absent",
        ],
        "network_used_for_dependencies": dependency_provenance.get("status")
        not in {"NOT_REQUIRED", "EXACT_VERSIONS_PRESENT"},
        "dependency_verification": dependency_provenance.get(
            "method", dependency_provenance.get("status")
        ),
        "telemetry": "none",
        "evidence": "declared_execution_boundary",
    }


def _stable_fingerprint(value: Any) -> str:
    """Hash deterministic intelligence while ignoring run timestamps."""
    text = json.dumps(value, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


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


def _write_wrappers(root: Path, output_dir: Path) -> list[str]:
    """Create wrappers bound to the interpreter that germinated the runtime."""
    created = []
    for name, script, verb in (
        ("capture", "shutter.py", " capture"),
        ("search", "search.py", ""),
        ("verify", "verify.py", ""),
    ):
        path = root / name
        path.write_text(
            "#!/bin/sh\n"
            "# Written by founderealm_seed during activation. The interpreter is pinned to the\n"
            "# one that germinated this tree, because the parser runtime is compiled\n"
            "# for it. Override with FOUNDEREALM_PYTHON if you move the tree to another.\n"
            'ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)\n'
            f'exec "${{FOUNDEREALM_PYTHON:-{sys.executable}}}"'
            f' "$ROOT/{output_dir.name}/{script}"{verb} "$@"\n',
            encoding="utf-8",
        )
        path.chmod(0o755)
        created.append(name)
    return created


def _run_capture(root: Path) -> int:
    """Discover lens contracts, order runnable stages, and report blocked outputs."""
    import ast

    out = root / OUT_NAME
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
    external = {"repository", "prior_runs", "dna", "all_previous_steps"}

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
    seed_owned = {"dependency-lock.json", "verification.json"}
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

    by_id = {lens["id"]: path for lens, path in lenses}
    environment = os.environ | {"FOUNDEREALM_ROOT": str(root)}
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


def _write_runtime(output_dir: Path) -> None:
    """Write the shutter: one call into the capture routine expanded above."""
    output_dir.mkdir(parents=True, exist_ok=True)
    out_name = output_dir.name
    (output_dir / "shutter.py").write_text(
        "#!/usr/bin/env python3\n"
        '"""Non-destructive Founderealm instrumentation shutter, grown by founderealm_seed.py."""\n'
        "import os\nimport subprocess\nimport sys\nfrom pathlib import Path\n\n"
        f"ROOT = Path(__file__).resolve().parents[1]\nOUT_NAME = {out_name!r}\n\n"
        + inspect.getsource(_run_capture)
        + "\n\nif __name__ == '__main__':\n"
        "    if sys.argv[1:] != ['capture']:\n"
        "        raise SystemExit('shutter accepts only capture')\n"
        "    raise SystemExit(_run_capture(ROOT))\n",
        encoding="utf-8",
    )
    (output_dir / "shutter.py").chmod(0o755)


def _connect_tables(out_dir: Path, views: dict) -> tuple[Any, list]:
    """Materialize every present artifact as a table, then switch file access off.

    Tables and not views, because a view stays lazy and would keep reading the disk
    after the lock. An absent artifact leaves its table uncreated rather than empty.
    """
    import duckdb

    connection = duckdb.connect()
    absent = []
    empty_columns = {
        "file": '"file" VARCHAR, "language" VARCHAR, "bytes" BIGINT, "sha256" VARCHAR, "parse_status" VARCHAR, "evidence" VARCHAR, "capability" VARCHAR',
        "symbol": '"file" VARCHAR, "line" INTEGER, "column" INTEGER, "end_line" INTEGER, "end_column" INTEGER, "start_byte" BIGINT, "end_byte" BIGINT, "evidence" VARCHAR, "language" VARCHAR, "kind" VARCHAR, "name" VARCHAR',
        "import": '"file" VARCHAR, "line" INTEGER, "column" INTEGER, "end_line" INTEGER, "end_column" INTEGER, "start_byte" BIGINT, "end_byte" BIGINT, "evidence" VARCHAR, "language" VARCHAR, "syntax" VARCHAR, "statement" VARCHAR',
        "call": '"file" VARCHAR, "line" INTEGER, "column" INTEGER, "end_line" INTEGER, "end_column" INTEGER, "start_byte" BIGINT, "end_byte" BIGINT, "evidence" VARCHAR, "language" VARCHAR, "target" VARCHAR',
        "dependency": '"from" VARCHAR, "to" VARCHAR, "resolution" VARCHAR, "evidence" VARCHAR',
        "unresolved": '"file" VARCHAR, "statement" VARCHAR, "evidence" VARCHAR',
        "test": '"file" VARCHAR, "language" VARCHAR, "discovery" VARCHAR',
        "impact": '"file" VARCHAR, "depth" INTEGER, "evidence" VARCHAR',
        "skipped": '"file" VARCHAR, "reason" VARCHAR',
    }
    for name, spec in views.items():
        path = out_dir / spec["artifact"]
        if not path.is_file():
            absent.append(name)
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            if not payload.get(spec["collection"]):
                connection.execute(f'CREATE TABLE "{name}" ({empty_columns[name]})')
                continue
            connection.execute(
                f'CREATE TABLE "{name}" AS SELECT unnest({spec["collection"]}, '
                f"recursive := true) FROM read_json_auto('{path}')"
            )
        except (OSError, ValueError, duckdb.Error) as error:
            absent.append(f"{name} ({type(error).__name__})")
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


def _write_search_recipe(output_dir: Path, dna: dict[str, Any]) -> None:
    """Write the generated query recipe and its declared tables."""
    output_dir.mkdir(parents=True, exist_ok=True)
    out_name = output_dir.name
    views = {
        name: spec for name, spec in dna["views"].items() if not name.startswith("_")
    }
    helpers = inspect.getsource(_connect_tables) + "\n\n" + inspect.getsource(_query)
    (output_dir / "search.py").write_text(
        "#!/usr/bin/env python3\n"
        '"""Founderealm query recipe: a read-only relational surface over the artifacts."""\n'
        "import json\nimport re\nimport sys\nfrom pathlib import Path\nfrom typing import Any\n\n"
        "ROOT = Path(__file__).resolve().parents[1]\n"
        f"OUT = ROOT / {out_name!r}\n"
        "sys.path.insert(0, str(OUT / 'dependencies'))\n\n"
        f"VIEWS = {views!r}\n\n" + helpers + "\n\n"
        "if __name__ == '__main__':\n"
        "    connection, missing = _connect_tables(OUT, VIEWS)\n"
        "    raise SystemExit(_query(connection, VIEWS, missing, sys.argv[1:]))\n",
        encoding="utf-8",
    )
    (output_dir / "search.py").chmod(0o755)


def _verify_instrument(out_dir: Path, dna: dict[str, Any]) -> dict[str, Any]:
    """Check generated code, lens contracts, stage structure, and artifact integrity."""
    import ast as ast_module
    import py_compile

    external = {"repository", "prior_runs", "dna", "all_previous_steps"}
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


def _write_verifier(output_dir: Path, dna_for_verify: dict[str, Any]) -> None:
    """Write ./verify as one call into the check routine expanded above."""
    output_dir.mkdir(parents=True, exist_ok=True)
    out_name = output_dir.name
    (output_dir / "verify.py").write_text(
        "#!/usr/bin/env python3\n"
        '"""Prove Founderealm contracts, generated code, and artifact integrity."""\n'
        "import hashlib\nimport json\nimport sys\nfrom pathlib import Path\n"
        "from typing import Any\n\n"
        f"ROOT = Path(__file__).resolve().parents[1]\nOUT = ROOT / {out_name!r}\n"
        f"DNA = {dna_for_verify!r}\n\n"
        + inspect.getsource(_verify_instrument)
        + "\n\nif __name__ == '__main__':\n"
        "    report = _verify_instrument(OUT, DNA)\n"
        "    (OUT / 'verification.json').write_text(\n"
        "        json.dumps(report, indent=2, sort_keys=True) + chr(10), encoding='utf-8')\n"
        "    print(json.dumps(report, indent=2))\n"
        "    raise SystemExit(0 if report['status'] == 'PASS' else 1)\n",
        encoding="utf-8",
    )
    (output_dir / "verify.py").chmod(0o755)


def _write_lens_package(output_dir: Path, dna: dict[str, Any]) -> None:
    """Materialize standalone lens scripts; each owns its analysis and outputs."""
    out_name = output_dir.name
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
        "ROOT = Path(os.environ['FOUNDEREALM_ROOT']).resolve()\n"
        f"OUT = ROOT / {out_name!r}\n\n"
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
        f"DNA_JSON = {DNA_JSON!r}\nARTIFACTS = {ARTIFACTS!r}\nROOT = Path(os.environ['FOUNDEREALM_ROOT']).resolve()\nOUT = ROOT / {out_name!r}\n\n"
    )
    shared_primitives = (_dna, _write_json)
    recipe_helpers = {
        "inventory": shared_primitives
        + (
            _pack,
            _language_for_path,
            _fallback_walk_files,
            _candidate_files,
            _classify_files,
            _normalized_package_name,
            _installed_distributions,
            _dependencies_match_lock,
            _pip_command,
            _download_verified_wheels,
            _bootstrap,
        ),
        "capability": shared_primitives
        + (
            _pack,
            _normalized_package_name,
            _installed_distributions,
            _dependencies_match_lock,
            _pip_command,
            _download_verified_wheels,
            _bootstrap,
            _negotiate_capabilities,
        ),
        "parsing": shared_primitives
        + (
            _pack,
            _node_text,
            _node_name,
            _record,
            _symbol_kind,
            _bound_kind,
            _is_import,
            _innermost_import,
            _is_call,
            _extract_tree,
            _parse_file,
        ),
        "dependencies": shared_primitives + (_dependency_graph,),
        "tests": shared_primitives + (_language_for_path, _discover_tests),
        "changes": shared_primitives + (_load_history, _change_graph, _change_impact),
        "contracts": shared_primitives + (_validate_data,),
        "ledger": shared_primitives
        + (
            _load_history,
            _repository_fingerprint,
            _stable_fingerprint,
            _trust_report,
            _execution_plan,
        ),
    }
    lens_recipes = {
        "inventory": "dna = _dna(); _bootstrap(OUT, dna['dependencies']); sys.path.insert(0, str(OUT / 'dependencies')); importlib.invalidate_caches(); files, mode = _candidate_files(ROOT, OUT, dna); supported, unsupported = _classify_files(files, dna, _pack(OUT).detect_language_from_path)\n_write_json(OUT / 'inventory.json', {'files': [path.relative_to(ROOT).as_posix() for path in files], 'mode': mode, 'supported': [{'file': path.relative_to(ROOT).as_posix(), 'language': language} for path, language in supported], 'unsupported': unsupported})",
        "capability": "dna = _dna(); inventory = json.loads((OUT / 'inventory.json').read_text()); dependency_provenance = _bootstrap(OUT, dna['dependencies']) if inventory['supported'] else {'status': 'NOT_REQUIRED', 'packages': []}; pack = _pack(OUT) if inventory['supported'] else None; languages = _negotiate_capabilities({item['language'] for item in inventory['supported']}, pack.get_parser) if pack else {}\n_write_json(OUT / 'capabilities.json', {'dependency_provenance': dependency_provenance, 'languages': languages, 'syntax_rules': dna['syntax']})",
        "parsing": "dna = _dna(); rules = dna['syntax']; inventory = json.loads((OUT / 'inventory.json').read_text()); capabilities = json.loads((OUT / 'capabilities.json').read_text())['languages']; sys.path.insert(0, str(OUT / 'dependencies')); importlib.invalidate_caches(); parser = _pack(OUT).get_parser; records, parsers = {'files': [], 'symbols': [], 'imports': [], 'calls': [], 'skipped': [], 'language_counts': {}, 'discovered_node_types': {}}, {}\nfor item in inventory['supported']:\n    path, language = ROOT / item['file'], item['language']\n    capability = capabilities.get(language, {})\n    if capability.get('status') != 'available': records['skipped'].append({'file': item['file'], 'reason': capability.get('reason', 'grammar was not probed')}); continue\n    record, symbols, imports, calls, discovered, error = _parse_file(path, ROOT, language, rules, parser, parsers)\n    if error or record is None: records['skipped'].append({'file': item['file'], 'reason': error or 'parser returned no file record'}); continue\n    records['files'].append(record); records['symbols'].extend(symbols); records['imports'].extend(imports); records['calls'].extend(calls); records['language_counts'][language] = records['language_counts'].get(language, 0) + 1\n    seen = records['discovered_node_types'].setdefault(language, {})\n    for node_type, count in discovered.items(): seen[node_type] = seen.get(node_type, 0) + count\nfor name in ('files', 'symbols', 'imports', 'calls'): _write_json(OUT / 'maps' / f'{name}.json', {name: records[name]})\n_write_json(OUT / 'parse_summary.json', {key: records[key] for key in ('skipped', 'language_counts', 'discovered_node_types')})",
        "dependencies": "files = json.loads((OUT / 'maps' / 'files.json').read_text())['files']; imports = json.loads((OUT / 'maps' / 'imports.json').read_text())['imports']\n_write_json(OUT / 'dependencies.json', _dependency_graph(files, imports))",
        "tests": "dna = _dna(); files = [ROOT / item for item in json.loads((OUT / 'inventory.json').read_text())['files']]\n_write_json(OUT / 'tests.json', {'tests': _discover_tests(files, ROOT, dna)})",
        "changes": "files = json.loads((OUT / 'maps' / 'files.json').read_text())['files']; dependencies = json.loads((OUT / 'dependencies.json').read_text()); history = _load_history(OUT / 'history' / 'runs.json')\n_write_json(OUT / 'changes.json', _change_graph(files, history, dependencies))",
        "contracts": "files = json.loads((OUT / 'maps' / 'files.json').read_text())['files']\n_write_json(OUT / 'contracts.json', _validate_data(files))",
        "ledger": "files = json.loads((OUT / 'maps' / 'files.json').read_text())['files']; matrix = {'provenance': {'generator': 'ledger_lens'}, 'steps': _dna()['execution_matrix'], 'plan': _execution_plan(_dna()['execution_matrix'])}; _write_json(OUT / 'execution_matrix.json', matrix); summary = {'files_parsed': len(files), 'symbols': len(json.loads((OUT / 'maps' / 'symbols.json').read_text())['symbols']), 'imports': len(json.loads((OUT / 'maps' / 'imports.json').read_text())['imports']), 'calls': len(json.loads((OUT / 'maps' / 'calls.json').read_text())['calls']), 'skipped_files': len(json.loads((OUT / 'parse_summary.json').read_text())['skipped'])}; fingerprint = _repository_fingerprint(files); history = _load_history(OUT / 'history' / 'runs.json'); history.append({'run_id': datetime.now(timezone.utc).isoformat(), 'fingerprint': fingerprint, 'files': {item['file']: item['sha256'] for item in files}, 'summary': summary}); _write_json(OUT / 'history' / 'runs.json', history[-_dna()['activation']['history_runs']:])",
    }
    for step in dna["execution_matrix"]:
        helper_source = "\n\n".join(
            inspect.getsource(helper) for helper in recipe_helpers[step["id"]]
        )
        source = (
            '#!/usr/bin/env python3\n"""Expanded Founderealm lens recipe.\n\n'
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


def _write_instructions(root: Path) -> bool:
    """Write the root handoff document only when it does not already exist."""
    path = root / "FOUNDEREALM_INSTRUCTIONS.md"
    if path.exists():
        return False
    path.write_text(
        "# Founderealm Lens\n\n"
        "This repository carries a map of itself. Read the map before reading source\n"
        "broadly. Source is the final authority; the map is how you find the right\n"
        "source fast.\n\n"
        "    ./capture    rebuild the map. Run it when the code changed.\n"
        "    ./search     ask it something. Start with `./search views`.\n"
        "    ./verify     check the instrument itself, not your code.\n\n"
        "## Reading an answer\n\n"
        "Every table carries a CAVEAT and it prints with the rows. Read it. Call sites\n"
        "resolve by NAME, so they are candidates and not proven edges. A null means\n"
        "never measured, not zero.\n\n"
        "ABSENT, BLOCKED and ORPHANED are answers, not errors. They mean nobody\n"
        "surveyed that ground. Report them as unknown. Do not fill them in.\n\n"
        "Use grep when the map says it does not know. That is what the map is for.\n\n"
        "## The lenses are examples\n\n"
        "`founderealm/lenses/` holds eight small scripts. They are a demonstration of what is\n"
        "possible, not a fixed set and not a framework.\n\n"
        "Write your own. Copy `NEW_LENS.py.example`, declare its `LENS` contract, write\n"
        "the JSON it promises. `./capture` finds it by reading that declaration. There\n"
        "is no registry to edit.\n\n"
        "Delete the ones you do not want. `./capture` notices: it names the artifacts\n"
        "nothing produces any more, and it blocks and names any lens whose input is\n"
        "gone rather than failing on it.\n\n"
        "Never hand-edit an artifact. Fix the lens, then capture again.\n",
        encoding="utf-8",
    )
    return True


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    temporary.replace(path)


def _write_gitignore(root: Path, output_dir: Path) -> bool:
    path = root / ".gitignore"
    # Derived from the output directory, which --output can change.
    name = output_dir.name
    entries = ("**/.DS_Store",) + tuple(
        f"/{name}/{leaf}"
        for leaf in ("dependencies/", "dependencies.next/", "cache/", "grammars/")
    )
    existing = path.read_text(encoding="utf-8") if path.exists() else ""
    missing = [entry for entry in entries if entry not in existing.splitlines()]
    if not missing:
        return False
    separator = "\n" if existing and not existing.endswith("\n") else ""
    addition = (
        separator
        + "\n# Seed-owned metadata, dependencies, and transient bootstrap state.\n"
    )
    addition += "\n".join(missing) + "\n"
    path.write_text(existing + addition, encoding="utf-8")
    return True


def _classify_files(
    candidate_files: list[Path], dna: dict[str, Any], detect: Any = None
) -> tuple[list[tuple[Path, str]], dict[str, int]]:
    """Assign parser capabilities and count source extensions without parsing."""
    ignored = set(dna["terrain"]["non_source_extensions"])
    supported: list[tuple[Path, str]] = []
    unsupported: dict[str, int] = {}
    for path in candidate_files:
        language = _language_for_path(path, detect)
        if language:
            supported.append((path, language))
        elif path.suffix and path.suffix.lower() not in ignored:
            extension = path.suffix.lower()
            unsupported[extension] = unsupported.get(extension, 0) + 1
    return supported, unsupported


def _survey(root: Path, output_dir: Path, dna: dict[str, Any]) -> dict[str, Any]:
    """Name the ground from the file list alone: no parsing, no grammar, no network."""
    files, mode = _candidate_files(root, output_dir, dna)
    supported, unsupported = _classify_files(files, dna)
    languages: dict[str, int] = {}
    for _, language in supported:
        languages[language] = languages.get(language, 0) + 1
    return {
        "root": str(root),
        "files": len(files),
        "inventory_mode": mode,
        "languages": dict(
            sorted(languages.items(), key=lambda item: (-item[1], item[0]))
        ),
        "unsupported_extensions": dict(sorted(unsupported.items())),
        "output_dir": str(output_dir),
        "identified_by": "file_extension",
    }


def _germination_report(terrain: dict[str, Any], output_dir: Path) -> str:
    """What was found, what was planted, and the one command to run next."""
    languages = terrain["languages"]
    shown = ", ".join(f"{name} {count}" for name, count in list(languages.items())[:8])
    if len(languages) > 8:
        shown += f", and {len(languages) - 8} more"
    inventory = (
        "git's own file list, so .gitignore is authoritative"
        if terrain["inventory_mode"] == "git"
        else "a directory walk - NO git here, so .gitignore is NOT enforced"
    )
    unsupported = terrain["unsupported_extensions"]
    lines = [
        "",
        "Founderealm Lens planted. Nothing has been mapped yet.",
        "",
        "TERRAIN",
        f"  root        {terrain['root']}",
        f"  files       {terrain['files']} via {inventory}",
        f"  languages   {shown or 'none identified'}"
        + "   (by extension; capture identifies them with the grammar pack)",
    ]
    if unsupported:
        lines.append(
            "  unclaimed   "
            + ", ".join(
                f"{ext} {count}" for ext, count in list(unsupported.items())[:6]
            )
        )
    lines += [
        "",
        "PLANTED",
        f"  {output_dir.name}/lenses/    8 example lenses. Add your own, delete what you do not want.",
        "  ./capture        build the map",
        "  ./search         ask it something",
        "  ./verify         check the instrument, not your code",
        "",
        "The seed is finished and can be deleted. It read the file list and nothing else,",
        "and it downloaded nothing. The first capture installs a hash-verified parser",
        "runtime and then builds the map, which is a separate thing to agree to.",
        "",
        "  ./capture",
        "",
    ]
    return "\n".join(lines)


def _germinate(root: Path, output_dir: Path, dna: dict[str, Any]) -> None:
    """Materialize the shutter, lenses, and small user handoff once."""
    _write_runtime(output_dir)
    _write_search_recipe(output_dir, dna)
    _write_verifier(output_dir, dna)
    _write_lens_package(output_dir, dna)
    for obsolete in (
        "runtime.py",
        "lens_manifest.json",
        "lens_profile.json",
        "lenses/_support.py",
        "lenses/__init__.py",
    ):
        (output_dir / obsolete).unlink(missing_ok=True)
    _write_wrappers(root, output_dir)
    _write_instructions(root)
    _write_gitignore(root, output_dir)


def _activation_notice(root: Path, output_dir: Path) -> str:
    return "\n".join(
        (
            "Founderealm Lens: Informed Activation",
            "",
            "This creates a repository-local intelligence camera for evidence-led navigation.",
            f"Read scope:  {root}",
            f"Write scope: {output_dir}",
            "",
            "It will create shutter, search, verification, installer, lens, JSON, Markdown, cache, and local parser-runtime files.",
            "It may create FOUNDEREALM_INSTRUCTIONS.md only when that file is absent.",
            "It will not modify observed source files or send telemetry.",
            "It reads the FILE LIST only, to name the terrain. It parses nothing and",
            "downloads nothing. The first ./capture installs a hash-verified parser",
            "runtime and builds the map, which you run yourself when you choose to.",
        )
    )


def activate(root: Path, output_name: str, *, authorized: bool = False) -> int:
    """Survey the repository, write local tooling, and stop before capture."""
    dna = _dna()
    root = _find_repo_root(root)
    output_dir = (root / output_name).resolve()
    if output_dir == root or root not in output_dir.parents:
        raise ValueError(
            "output directory must be a dedicated directory inside the repository"
        )
    if not authorized:
        raise PermissionError("activation requires explicit authorization")
    terrain = _survey(root, output_dir, dna)
    _germinate(root, output_dir, dna)
    print(_germination_report(terrain, output_dir))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Dormant Founderealm Lens seed. No files or dependencies are created without activate."
    )
    subparsers = parser.add_subparsers(dest="command")
    activate_parser = subparsers.add_parser(
        "activate", help="germinate Founderealm Lens in a repository"
    )
    activate_parser.add_argument("--root", type=Path, default=Path.cwd())
    activate_parser.add_argument("--output", default=_dna()["activation"]["output_dir"])
    args = parser.parse_args(argv)
    if args.command != "activate":
        parser.print_help()
        print(
            "\n[Founderealm] Dormant. Run the activate command to create any files or install dependencies."
        )
        return 0
    try:
        root = _find_repo_root(args.root)
        output_dir = (root / args.output).resolve()
        print(_activation_notice(root, output_dir))
        try:
            answer = input("Authorize these writes? [y/N] ").strip().lower()
        except EOFError:
            # No one is there to authorize, so the answer is no. A traceback here would
            # read as a crash rather than as the refusal it actually is.
            print("\n[Founderealm] No authorization possible without a terminal; nothing was written.")
            return 1
        if answer not in {"y", "yes"}:
            print("[Founderealm] Activation cancelled; no files were written.")
            return 0
        return activate(root, args.output, authorized=True)
    except (OSError, PermissionError, RuntimeError, ValueError) as error:
        print(f"[Founderealm] Activation failed honestly: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
