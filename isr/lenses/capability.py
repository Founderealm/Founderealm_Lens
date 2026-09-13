#!/usr/bin/env python3
"""Expanded ISR lens recipe.

Question: capability
Inputs: inventory.json
Outputs: capabilities.json
This file is standalone after germination; its source was expanded from
the seed recipe so it can be inspected, changed, or replaced locally.
"""

from __future__ import annotations
import base64, fnmatch, hashlib, importlib, json, os, re, shutil, subprocess, sys
from collections.abc import Iterator
from datetime import datetime, timezone
from importlib.machinery import PathFinder
from importlib.metadata import distributions
from pathlib import Path
from typing import Any
from urllib.request import urlopen

DNA_JSON = '\n{\n  "identity": {\n    "name": "ISR Portable Seed",\n        "genome_version": "0.3.0",\n        "map_schema_version": "1.2.0"\n  },\n    "activation": {\n    "output_dir": "isr",\n        "history_runs": 5\n  },\n      "runtime_package": {\n            "name": "shutter.py",\n            "role": "non_destructive_repository_instrumentation_runtime",\n            "entrypoints": {"capture": "refresh maps", "search": "query catalogue"},\n            "authority": "generated from seed during first activation",\n            "writes": [".isr artifacts", "five-run history"],\n            "must_not": ["activate seed", "mutate source", "emit telemetry"],\n            "expand_with": ["new delegated stages", "new grammar capability", "new catalogue views"],\n            "compatibility_rule": "preserve capture, search, evidence, and provenance contracts"\n      },\n      "execution_contract": {\n                "optional_requires": "soft inputs; absence must not block the stage",\n                "external_inputs": "observed inputs not produced by another stage",\n                "mutates": "paths changed by the stage",\n                "invalidates": "outputs made stale by a changed input",\n                "evidence": "how the stage establishes its claims",\n                "failure_policy": "block_downstream, emit_unknown, or emit_partial",\n                "scope": "population the stage is allowed to inspect",\n                "trust_tier": "provenance tier for the executable lens recipe"\n        },\n    "execution_matrix": [\n        {"id": "inventory", "requires": ["repository"], "produces": ["inventory.json"], "feeds": ["parsing", "changes", "tests"], "evidence": "direct_filesystem_inventory", "trust_tier": "seed_generated"},\n        {"id": "capability", "requires": ["inventory.json"], "produces": ["capabilities.json"], "feeds": ["parsing"], "evidence": "tree_sitter_runtime_probe", "trust_tier": "seed_generated"},\n        {"id": "parsing", "requires": ["inventory.json", "capabilities.json"], "produces": ["maps/files.json", "maps/symbols.json", "maps/imports.json", "maps/calls.json", "parse_summary.json"], "feeds": ["dependencies", "catalogue"], "evidence": "tree_sitter_syntax", "trust_tier": "seed_generated"},\n        {"id": "dependencies", "requires": ["maps/files.json", "maps/imports.json"], "produces": ["dependencies.json"], "feeds": ["catalogue"], "evidence": "derived_import_token_resolution", "trust_tier": "seed_generated"},\n        {"id": "tests", "requires": ["inventory.json"], "produces": ["tests.json"], "feeds": ["catalogue"], "evidence": "directory_and_filename_convention", "trust_tier": "seed_generated"},\n        {"id": "changes", "requires": ["maps/files.json", "dependencies.json", "prior_runs"], "produces": ["changes.json"], "feeds": ["catalogue"], "evidence": "file_hash_and_derived_impact", "trust_tier": "seed_generated"},\n        {"id": "contracts", "requires": ["dna", "maps/files.json", "maps/symbols.json", "maps/imports.json", "maps/calls.json"], "produces": ["contracts.json"], "feeds": ["catalogue"], "evidence": "structural_contract_validation", "trust_tier": "seed_generated"},\n        {"id": "ledger", "requires": ["all_previous_steps"], "produces": ["execution_matrix.json", "history/runs.json"], "feeds": ["agent"], "evidence": "derived_run_record", "trust_tier": "seed_generated"}\n    ],\n    "dependencies": {\n        "registry": "https://pypi.org/pypi/{name}/{version}/json",\n        "_why": "Pack 0.9.1 pinned three standalone grammar wheels whose ABIs contradicted its own tree-sitter pin, so C# could not load at all. Pack 1.x needs none of them and covers 371 languages instead of 171. It also identifies languages itself, which retires Pygments. Grammars arrive as ONE archive whose sha256 is published in a manifest inside this verified wheel, so the chain of custody still bottoms out at a hash this seed checked.",\n        "grammar_cache": "inside the output directory, never the user\'s home",\n        "packages": [\n            {"name": "tree-sitter-language-pack", "version": "1.19.0"},\n            {"name": "tree-sitter", "version": "0.26.0"},\n            {"name": "duckdb", "version": "1.5.5"}\n        ]\n    },\n  "views": {\n    "_why": "A declared relational surface over the artifacts, with the caveat that changes what each answer means attached to the view rather than left for the reader to know. Every artifact is {key: [records]}, so one form reads them all: unnest(<collection>, recursive := true). Tables are materialized and then file access is switched off, because a view is lazy and would keep reading the disk.",\n    "file":        {"artifact": "maps/files.json", "collection": "files", "grain": "one row per parsed file", "caveat": "capability=derived_node_type means symbols, imports and calls were read from node type names rather than a curated table. parse_status=ERRORS_PRESENT means the grammar recovered from a syntax error, so records from that file may be incomplete."},\n    "symbol":      {"artifact": "maps/symbols.json", "collection": "symbols", "grain": "one row per declaration", "caveat": "kind is the grammar\'s own node type with its suffix removed, so it is the grammar\'s vocabulary and not a normalized one: class, struct, trait and interface all appear as the language spells them. A name of <anonymous> means the grammar declared no name field and no identifier child."},\n    "import":      {"artifact": "maps/imports.json", "collection": "imports", "grain": "one row per import, include or require", "caveat": "syntax names the node type it came from, or call:<name> when a language spells an import as a function call, as Ruby and Lua do. A nested container is counted once, at the outermost node."},\n    "call":        {"artifact": "maps/calls.json", "collection": "calls", "grain": "one row per call site", "caveat": "RESOLVED BY NAME, not by receiver type. Any object\'s method of that name lands here, so each row is a CANDIDATE call site and not a proven edge. target=<unresolved> means the grammar put the callee somewhere none of the declared callee fields reached."},\n    "dependency":  {"artifact": "dependencies.json", "collection": "edges", "grain": "one row per file-to-file edge", "caveat": "resolution=resolved came from a quoted path, inferred came from matching a bare token against known file stems. An inferred edge can be wrong where two files share a stem."},\n    "unresolved":  {"artifact": "dependencies.json", "collection": "unresolved_imports", "grain": "one row per import that matched no file in this repository", "caveat": "Usually a third-party or standard-library import, which is correct and not a defect. Absence from this table is not evidence an edge was found."},\n    "test":        {"artifact": "tests.json", "collection": "tests", "grain": "one row per file that looks like a test", "caveat": "Discovery is by DIRECTORY AND FILENAME CONVENTION ONLY. Nothing here was executed and no outcome is recorded, so this says a test exists and never that it passes."},\n    "impact":      {"artifact": "changes.json", "collection": "impact", "grain": "one row per file reached by a change, with its distance", "caveat": "Derived by walking dependency edges backwards from changed files, so it inherits the inferred-edge caveat. depth is hops, not severity. Empty on a first run, when there is no prior run to compare against."},\n    "skipped":     {"artifact": "parse_summary.json", "collection": "skipped", "grain": "one row per file that was not parsed, with the reason", "caveat": "A non-empty table is the honest record of a gap, not a failure of the run. Read it before treating any count as complete."}\n  },\n  "terrain": {\n    "exclude_directories": [\n      ".git", ".hg", ".svn", "isr", ".venv", "venv", "node_modules",\n      "vendor", "dist", "build", "target", "__pycache__", ".mypy_cache",\n      ".pytest_cache", ".ruff_cache", "coverage", ".next"\n    ],\n    "non_source_extensions": [\n      ".bmp", ".gif", ".ico", ".jpeg", ".jpg", ".lock", ".pdf", ".png",\n      ".pyc", ".svg", ".webp", ".woff", ".woff2", ".zip"\n        ],\n        "test_directories": ["test", "tests", "__tests__", "spec", "specs"],\n        "test_file_patterns": [\n            "test_*.*", "*_test.*", "*.test.*", "*.spec.*"\n        ]\n  },\n  "syntax": {\n    "_why": "Tree-sitter node types are named by convention across grammars, so one set of rules reads all 171 of them. Six hand-written language tables gave semantic depth to six languages and left the other 165 with symbols but ZERO imports and ZERO calls, measured. Kotlin was worse: its grammar carries no name fields at all, so the old name-field probe found nothing in a file whose node types are textbook conventional.",\n    "skip_suffixes": ["_list", "_block", "_body", "_suffix"],\n    "skip_contains": ["parameter"],\n    "import_contains": ["import", "use_declaration", "using_", "include", "require", "extern_crate"],\n    "callee_fields": ["function", "macro", "method", "name"],\n    "import_callees": ["require", "require_relative", "import_module", "load"],\n    "call_contains": ["call", "invocation"],\n    "call_exact": ["new_expression", "macro_invocation"],\n    "symbol_suffixes": ["_definition", "_declaration", "_item", "_specifier", "_specification", "_set"],\n    "symbol_exact": ["class", "method", "module", "singleton_method", "rule_set"],\n    "_binding_why": "Compiled languages declare with a keyword and the node type says so. Script languages bind a name to a value - const W = () => {}, handler = lambda x: x - and the wrapper node type says only lexical_declaration, which stripped to the kind \'lexical\' and named nothing useful. An arrow function inside an object literal was missed entirely. Half of modern code declares this way.",\n    "binding_types": ["variable_declarator", "assignment", "assignment_statement", "var_spec", "pair", "field_definition", "public_field_definition"],\n    "binding_name_fields": ["name", "left", "key"],\n    "binding_value_fields": ["value", "right"],\n    "binding_unwrap": ["expression_list", "parenthesized_expression"],\n    "value_function_contains": ["arrow_function", "function", "lambda", "func_literal", "closure"],\n    "value_class_contains": ["class"],\n    "binding_wrappers": ["lexical_declaration", "variable_declaration", "var_declaration", "expression_statement"],\n    "name_fields": ["name", "declarator", "function", "alias", "path"],\n    "name_child_types": ["identifier", "type_identifier", "field_identifier", "simple_identifier", "property_identifier", "constant", "constructor_name"]\n  }\n}\n'
ARTIFACTS = ('inventory.json', 'capabilities.json', 'maps/files.json', 'maps/symbols.json', 'maps/imports.json', 'maps/calls.json', 'parse_summary.json', 'dependencies.json', 'tests.json', 'changes.json', 'contracts.json', 'execution_matrix.json', 'history/runs.json')
ROOT = Path(os.environ['ISR_ROOT']).resolve()
OUT = ROOT / 'isr'

def _dna() -> dict[str, Any]:
    return json.loads(DNA_JSON)


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)


def _pack(out_dir: Path) -> Any:
    """Import the grammar pack with its cache pinned inside the output directory.

    Left alone it caches compiled grammars under the user's home. The seed declares that
    it writes only inside the repository, and a declaration the code does not keep is
    worse than no declaration, so the cache is redirected before the first grammar is
    ever requested.
    """
    import importlib

    pack = importlib.import_module("tree_sitter_language_pack")
    pack.configure(pack.PackConfig(cache_dir=str(out_dir / "grammars")))
    return pack


def _normalized_package_name(name: str) -> str:
    return name.lower().replace("_", "-").replace(".", "-")


def _installed_distributions(dependencies_dir: Path) -> dict[str, Any]:
    return {
        _normalized_package_name(distribution.metadata["Name"]): distribution
        for distribution in distributions(path=[str(dependencies_dir)])
        if distribution.metadata["Name"]
    }


def _dependencies_match_lock(dependencies_dir: Path, lock: list[dict[str, str]]) -> bool:
    dependencies_dir = dependencies_dir.resolve()
    if not dependencies_dir.exists():
        return False
    installed = _installed_distributions(dependencies_dir)
    for item in lock:
        distribution = installed.get(_normalized_package_name(item["name"]))
        if distribution is None or distribution.version != item["version"] or distribution.files is None:
            return False
        for package_path in distribution.files:
            recorded_hash = package_path.hash
            if recorded_hash is None:
                continue
            installed_path = Path(distribution.locate_file(package_path)).resolve()
            if dependencies_dir != installed_path and dependencies_dir not in installed_path.parents:
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
    dependencies_dir = output_dir / "dependencies"
    cache_dir = output_dir / "cache"
    sys.path.insert(0, str(dependencies_dir))
    lock = dependency_gene["packages"]
    lock_path = output_dir / "dependency-lock.json"
    if (
        _dependencies_match_lock(dependencies_dir, lock)
        and PathFinder.find_spec("tree_sitter_language_pack", [str(dependencies_dir)]) is not None
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
        raise RuntimeError("verified parser dependencies installation failed; host source was not modified")
    shutil.rmtree(dependencies_dir, ignore_errors=True)
    staging_dir.replace(dependencies_dir)
    # The wheels are installed and the runtime has been verified file by file against
    # their recorded hashes, with the provenance kept in dependency-lock.json. Nothing
    # reads these again: a later bootstrap either finds the runtime already matching the
    # lock, or re-downloads from scratch. 47 MB of write-only cache on a sixteen-file
    # repository, held for no reader.
    shutil.rmtree(cache_dir, ignore_errors=True)
    importlib.invalidate_caches()
    if PathFinder.find_spec("tree_sitter_language_pack", [str(dependencies_dir)]) is None:
        raise RuntimeError("parser bootstrap completed but local dependencies are unavailable")
    result = {
        "status": "VERIFIED",
        "method": "exact versions and PyPI release SHA-256 over TLS",
        "packages": packages,
    }
    _write_json(lock_path, result)
    return result


def _negotiate_capabilities(languages: set[str], get_parser: Any) -> dict[str, dict[str, str]]:
    """Probe each grammar once and record whether it loaded, with the reason if not.

    There is no depth tier to report any more. Every grammar that loads is read by the
    same rules, so the only question left is whether the grammar is there.
    """
    capabilities = {}
    for language in sorted(languages):
        try:
            get_parser(language)
            capabilities[language] = {"status": "available", "evidence": "tree_sitter_probe"}
        except Exception as error:
            capabilities[language] = {
                "status": "unavailable",
                "evidence": "tree_sitter_probe",
                "reason": f"{type(error).__name__}: {error}",
            }
    return capabilities


LENS = {'id': 'capability', 'requires': ['inventory.json'], 'produces': ['capabilities.json'], 'feeds': ['parsing'], 'evidence': 'tree_sitter_runtime_probe', 'trust_tier': 'seed_generated'}

def main():
    dna = _dna(); inventory = json.loads((OUT / 'inventory.json').read_text()); dependency_provenance = _bootstrap(OUT, dna['dependencies']) if inventory['supported'] else {'status': 'NOT_REQUIRED', 'packages': []}; pack = _pack(OUT) if inventory['supported'] else None; languages = _negotiate_capabilities({item['language'] for item in inventory['supported']}, pack.get_parser) if pack else {}
    _write_json(OUT / 'capabilities.json', {'dependency_provenance': dependency_provenance, 'languages': languages, 'syntax_rules': dna['syntax']})

if __name__ == '__main__':
    main()
