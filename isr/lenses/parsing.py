#!/usr/bin/env python3
"""Expanded ISR lens recipe.

Question: parsing
Inputs: inventory.json, capabilities.json
Outputs: maps/files.json, maps/symbols.json, maps/imports.json, maps/calls.json, parse_summary.json
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
    temporary.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
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


def _node_text(node: Any, source: bytes, limit: int = 240) -> str:
    text = source[node.start_byte : node.end_byte].decode("utf-8", errors="replace")
    return " ".join(text.split())[:limit]


def _node_name(node: Any, source: bytes, rules: dict[str, Any]) -> str:
    """The declared name, from a field if the grammar uses one, else a child token.

    Kotlin declares class_declaration and function_declaration and carries NO name
    field on either, so probing fields alone returned nothing for an entire language
    whose node types are textbook conventional. Fields first, then the first
    identifier-shaped child, then an honest <anonymous>.
    """
    for field in rules["name_fields"]:
        child = node.child_by_field_name(field)
        if child is not None:
            return _node_text(child, source, 160)
    for child in node.named_children:
        if child.type in rules["name_child_types"]:
            return _node_text(child, source, 160)
    return node.named_children[0].type if node.named_children else "<anonymous>"


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
    """The kind a grammar already announced in its own node type name.

    class_declaration -> class, function_item -> function, trait_item -> trait,
    rule_set -> rule. The grammar authors named these; nothing needs declaring.
    """
    if node_type in rules["symbol_exact"]:
        return node_type.removesuffix("_set")
    for suffix in rules["symbol_suffixes"]:
        if node_type.endswith(suffix):
            return node_type[: -len(suffix)] or node_type
    return None


def _bound_kind(value: Any, rules: dict[str, Any]) -> tuple[str, Any] | None:
    """What a binding binds, when it binds something declarable.

    Returns (kind, the node that was bound) or None. Go and Lua wrap the bound value in
    an expression list, so one level of that is unwrapped before asking. A value that is
    a call - Python's Alpha = type(...) - binds something built at runtime and is
    deliberately not reported as a declaration: the call itself is already a call site.
    """
    if value.type in rules["binding_unwrap"] and value.named_children:
        value = value.named_children[0]
    if any(token in value.type for token in rules["value_class_contains"]):
        return "class", value
    if any(token in value.type for token in rules["value_function_contains"]):
        return "function", value
    return None


def _is_import(node_type: str, rules: dict[str, Any]) -> bool:
    return any(token in node_type for token in rules["import_contains"])


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
    """Read symbols, imports and calls from any grammar, by node type name.

    One rule set for every grammar instead of a table per language. Measured before
    this existed: ten of sixteen languages yielded zero imports and zero calls,
    because the table supplied the node types to look for and there was no table.

    The fourth return value is the set of node types that actually matched, counted
    per type. That is a DISCOVERED gene: the seed stops declaring what it expects to
    find and starts reporting what it found, which a reader can audit.
    """
    symbols: list[dict[str, Any]] = []
    imports: list[dict[str, Any]] = []
    calls: list[dict[str, Any]] = []
    discovered: dict[str, int] = {}
    claimed: set = set()
    skip = tuple(rules["skip_suffixes"])
    # (node, an ancestor already counted as an import). Containers nest: Go declares
    # import_declaration > import_spec and Kotlin import_list > import_header, and
    # both levels match on the word. Counting both doubles every import. Calls are
    # left to nest, because f(g(x)) genuinely is two call sites.
    #
    # Seeded with the root's CHILDREN, not the root. A file's root node is not a
    # declaration in it, and Python names that root `module` - the same string Ruby
    # uses for its module keyword - so every Python file was reporting a phantom
    # symbol for itself. Measured: a 3-declaration file returned 4.
    stack = [(child, False) for child in reversed(root_node.named_children)]

    while stack:
        node, inside_import = stack.pop()
        node_type = node.type
        node_claimed = False

        if not node_type.endswith(skip) and not any(
            token in node_type for token in rules["skip_contains"]
        ):
            if _is_import(node_type, rules):
                if not inside_import:
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
                node_claimed = True
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
                # A call is how several languages spell an import: Ruby require,
                # Lua require, CommonJS require. The old code special-cased this for
                # JavaScript only, by name.
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
                    # The bound value is reported once, under the name it was given. Left
                    # unclaimed, `let T = class {}` emitted both the binding and the
                    # anonymous class inside it. Its body is still walked, so methods
                    # within it are still found.
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

        stack.extend(
            (child, inside_import or node_claimed)
            for child in reversed(node.named_children)
        )
    return symbols, imports, calls, discovered


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
            # One tier now, and it is named for how it was reached rather than for a
            # table that no longer exists.
            "capability": "derived_node_type",
        }
        return record, symbols, imports, calls, discovered, None
    except Exception as error:
        return None, [], [], [], {}, f"{type(error).__name__}: {error}"


LENS = {'id': 'parsing', 'requires': ['inventory.json', 'capabilities.json'], 'produces': ['maps/files.json', 'maps/symbols.json', 'maps/imports.json', 'maps/calls.json', 'parse_summary.json'], 'feeds': ['dependencies', 'catalogue'], 'evidence': 'tree_sitter_syntax', 'trust_tier': 'seed_generated'}

def main():
    dna = _dna(); rules = dna['syntax']; inventory = json.loads((OUT / 'inventory.json').read_text()); capabilities = json.loads((OUT / 'capabilities.json').read_text())['languages']; sys.path.insert(0, str(OUT / 'dependencies')); importlib.invalidate_caches(); parser = _pack(OUT).get_parser; records, parsers = {'files': [], 'symbols': [], 'imports': [], 'calls': [], 'skipped': [], 'language_counts': {}, 'discovered_node_types': {}}, {}
    for item in inventory['supported']:
        path, language = ROOT / item['file'], item['language']
        capability = capabilities.get(language, {})
        if capability.get('status') != 'available': records['skipped'].append({'file': item['file'], 'reason': capability.get('reason', 'grammar was not probed')}); continue
        record, symbols, imports, calls, discovered, error = _parse_file(path, ROOT, language, rules, parser, parsers)
        if error or record is None: records['skipped'].append({'file': item['file'], 'reason': error or 'parser returned no file record'}); continue
        records['files'].append(record); records['symbols'].extend(symbols); records['imports'].extend(imports); records['calls'].extend(calls); records['language_counts'][language] = records['language_counts'].get(language, 0) + 1
        seen = records['discovered_node_types'].setdefault(language, {})
        for node_type, count in discovered.items(): seen[node_type] = seen.get(node_type, 0) + count
    for name in ('files', 'symbols', 'imports', 'calls'): _write_json(OUT / 'maps' / f'{name}.json', {name: records[name]})
    _write_json(OUT / 'parse_summary.json', {key: records[key] for key in ('skipped', 'language_counts', 'discovered_node_types')})

if __name__ == '__main__':
    main()
