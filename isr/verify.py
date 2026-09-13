#!/usr/bin/env python3
"""Prove ISR contracts, generated code, and artifact integrity."""
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'isr'
DNA = {'identity': {'name': 'ISR Portable Seed', 'genome_version': '0.3.0', 'map_schema_version': '1.2.0'}, 'activation': {'output_dir': 'isr', 'history_runs': 5}, 'runtime_package': {'name': 'shutter.py', 'role': 'non_destructive_repository_instrumentation_runtime', 'entrypoints': {'capture': 'refresh maps', 'search': 'query catalogue'}, 'authority': 'generated from seed during first activation', 'writes': ['.isr artifacts', 'five-run history'], 'must_not': ['activate seed', 'mutate source', 'emit telemetry'], 'expand_with': ['new delegated stages', 'new grammar capability', 'new catalogue views'], 'compatibility_rule': 'preserve capture, search, evidence, and provenance contracts'}, 'execution_contract': {'optional_requires': 'soft inputs; absence must not block the stage', 'external_inputs': 'observed inputs not produced by another stage', 'mutates': 'paths changed by the stage', 'invalidates': 'outputs made stale by a changed input', 'evidence': 'how the stage establishes its claims', 'failure_policy': 'block_downstream, emit_unknown, or emit_partial', 'scope': 'population the stage is allowed to inspect', 'trust_tier': 'provenance tier for the executable lens recipe'}, 'execution_matrix': [{'id': 'inventory', 'requires': ['repository'], 'produces': ['inventory.json'], 'feeds': ['parsing', 'changes', 'tests'], 'evidence': 'direct_filesystem_inventory', 'trust_tier': 'seed_generated'}, {'id': 'capability', 'requires': ['inventory.json'], 'produces': ['capabilities.json'], 'feeds': ['parsing'], 'evidence': 'tree_sitter_runtime_probe', 'trust_tier': 'seed_generated'}, {'id': 'parsing', 'requires': ['inventory.json', 'capabilities.json'], 'produces': ['maps/files.json', 'maps/symbols.json', 'maps/imports.json', 'maps/calls.json', 'parse_summary.json'], 'feeds': ['dependencies', 'catalogue'], 'evidence': 'tree_sitter_syntax', 'trust_tier': 'seed_generated'}, {'id': 'dependencies', 'requires': ['maps/files.json', 'maps/imports.json'], 'produces': ['dependencies.json'], 'feeds': ['catalogue'], 'evidence': 'derived_import_token_resolution', 'trust_tier': 'seed_generated'}, {'id': 'tests', 'requires': ['inventory.json'], 'produces': ['tests.json'], 'feeds': ['catalogue'], 'evidence': 'directory_and_filename_convention', 'trust_tier': 'seed_generated'}, {'id': 'changes', 'requires': ['maps/files.json', 'dependencies.json', 'prior_runs'], 'produces': ['changes.json'], 'feeds': ['catalogue'], 'evidence': 'file_hash_and_derived_impact', 'trust_tier': 'seed_generated'}, {'id': 'contracts', 'requires': ['dna', 'maps/files.json', 'maps/symbols.json', 'maps/imports.json', 'maps/calls.json'], 'produces': ['contracts.json'], 'feeds': ['catalogue'], 'evidence': 'structural_contract_validation', 'trust_tier': 'seed_generated'}, {'id': 'ledger', 'requires': ['all_previous_steps'], 'produces': ['execution_matrix.json', 'history/runs.json'], 'feeds': ['agent'], 'evidence': 'derived_run_record', 'trust_tier': 'seed_generated'}], 'dependencies': {'registry': 'https://pypi.org/pypi/{name}/{version}/json', '_why': 'Pack 0.9.1 pinned three standalone grammar wheels whose ABIs contradicted its own tree-sitter pin, so C# could not load at all. Pack 1.x needs none of them and covers 371 languages instead of 171. It also identifies languages itself, which retires Pygments. Grammars arrive as ONE archive whose sha256 is published in a manifest inside this verified wheel, so the chain of custody still bottoms out at a hash this seed checked.', 'grammar_cache': "inside the output directory, never the user's home", 'packages': [{'name': 'tree-sitter-language-pack', 'version': '1.19.0'}, {'name': 'tree-sitter', 'version': '0.26.0'}, {'name': 'duckdb', 'version': '1.5.5'}]}, 'views': {'_why': 'A declared relational surface over the artifacts, with the caveat that changes what each answer means attached to the view rather than left for the reader to know. Every artifact is {key: [records]}, so one form reads them all: unnest(<collection>, recursive := true). Tables are materialized and then file access is switched off, because a view is lazy and would keep reading the disk.', 'file': {'artifact': 'maps/files.json', 'collection': 'files', 'grain': 'one row per parsed file', 'caveat': 'capability=derived_node_type means symbols, imports and calls were read from node type names rather than a curated table. parse_status=ERRORS_PRESENT means the grammar recovered from a syntax error, so records from that file may be incomplete.'}, 'symbol': {'artifact': 'maps/symbols.json', 'collection': 'symbols', 'grain': 'one row per declaration', 'caveat': "kind is the grammar's own node type with its suffix removed, so it is the grammar's vocabulary and not a normalized one: class, struct, trait and interface all appear as the language spells them. A name of <anonymous> means the grammar declared no name field and no identifier child."}, 'import': {'artifact': 'maps/imports.json', 'collection': 'imports', 'grain': 'one row per import, include or require', 'caveat': 'syntax names the node type it came from, or call:<name> when a language spells an import as a function call, as Ruby and Lua do. A nested container is counted once, at the outermost node.'}, 'call': {'artifact': 'maps/calls.json', 'collection': 'calls', 'grain': 'one row per call site', 'caveat': "RESOLVED BY NAME, not by receiver type. Any object's method of that name lands here, so each row is a CANDIDATE call site and not a proven edge. target=<unresolved> means the grammar put the callee somewhere none of the declared callee fields reached."}, 'dependency': {'artifact': 'dependencies.json', 'collection': 'edges', 'grain': 'one row per file-to-file edge', 'caveat': 'resolution=resolved came from a quoted path, inferred came from matching a bare token against known file stems. An inferred edge can be wrong where two files share a stem.'}, 'unresolved': {'artifact': 'dependencies.json', 'collection': 'unresolved_imports', 'grain': 'one row per import that matched no file in this repository', 'caveat': 'Usually a third-party or standard-library import, which is correct and not a defect. Absence from this table is not evidence an edge was found.'}, 'test': {'artifact': 'tests.json', 'collection': 'tests', 'grain': 'one row per file that looks like a test', 'caveat': 'Discovery is by DIRECTORY AND FILENAME CONVENTION ONLY. Nothing here was executed and no outcome is recorded, so this says a test exists and never that it passes.'}, 'impact': {'artifact': 'changes.json', 'collection': 'impact', 'grain': 'one row per file reached by a change, with its distance', 'caveat': 'Derived by walking dependency edges backwards from changed files, so it inherits the inferred-edge caveat. depth is hops, not severity. Empty on a first run, when there is no prior run to compare against.'}, 'skipped': {'artifact': 'parse_summary.json', 'collection': 'skipped', 'grain': 'one row per file that was not parsed, with the reason', 'caveat': 'A non-empty table is the honest record of a gap, not a failure of the run. Read it before treating any count as complete.'}}, 'terrain': {'exclude_directories': ['.git', '.hg', '.svn', 'isr', '.venv', 'venv', 'node_modules', 'vendor', 'dist', 'build', 'target', '__pycache__', '.mypy_cache', '.pytest_cache', '.ruff_cache', 'coverage', '.next'], 'non_source_extensions': ['.bmp', '.gif', '.ico', '.jpeg', '.jpg', '.lock', '.pdf', '.png', '.pyc', '.svg', '.webp', '.woff', '.woff2', '.zip'], 'test_directories': ['test', 'tests', '__tests__', 'spec', 'specs'], 'test_file_patterns': ['test_*.*', '*_test.*', '*.test.*', '*.spec.*']}, 'syntax': {'_why': 'Tree-sitter node types are named by convention across grammars, so one set of rules reads all 171 of them. Six hand-written language tables gave semantic depth to six languages and left the other 165 with symbols but ZERO imports and ZERO calls, measured. Kotlin was worse: its grammar carries no name fields at all, so the old name-field probe found nothing in a file whose node types are textbook conventional.', 'skip_suffixes': ['_list', '_block', '_body', '_suffix'], 'skip_contains': ['parameter'], 'import_contains': ['import', 'use_declaration', 'using_', 'include', 'require', 'extern_crate'], 'callee_fields': ['function', 'macro', 'method', 'name'], 'import_callees': ['require', 'require_relative', 'import_module', 'load'], 'call_contains': ['call', 'invocation'], 'call_exact': ['new_expression', 'macro_invocation'], 'symbol_suffixes': ['_definition', '_declaration', '_item', '_specifier', '_specification', '_set'], 'symbol_exact': ['class', 'method', 'module', 'singleton_method', 'rule_set'], '_binding_why': "Compiled languages declare with a keyword and the node type says so. Script languages bind a name to a value - const W = () => {}, handler = lambda x: x - and the wrapper node type says only lexical_declaration, which stripped to the kind 'lexical' and named nothing useful. An arrow function inside an object literal was missed entirely. Half of modern code declares this way.", 'binding_types': ['variable_declarator', 'assignment', 'assignment_statement', 'var_spec', 'pair', 'field_definition', 'public_field_definition'], 'binding_name_fields': ['name', 'left', 'key'], 'binding_value_fields': ['value', 'right'], 'binding_unwrap': ['expression_list', 'parenthesized_expression'], 'value_function_contains': ['arrow_function', 'function', 'lambda', 'func_literal', 'closure'], 'value_class_contains': ['class'], 'binding_wrappers': ['lexical_declaration', 'variable_declaration', 'var_declaration', 'expression_statement'], 'name_fields': ['name', 'declarator', 'function', 'alias', 'path'], 'name_child_types': ['identifier', 'type_identifier', 'field_identifier', 'simple_identifier', 'property_identifier', 'constant', 'constructor_name']}}

def _verify_instrument(out_dir: Path, dna: dict[str, Any]) -> dict[str, Any]:
    """Prove the instrument: its own code, its declarations, and its declared outputs.

    One definition of every structural check. These were split across a lens that wrote
    contracts.json and a separate generated verifier, both reading the same declarations
    and free to disagree about them, which is the duplication this whole system treats
    as the primary defect.

    It states its own limit, because a bare PASS invites more trust than it earns:
    structural contracts and artifact integrity, NOT whether any claim in the maps is
    true.
    """
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
        record(f"core:{required}", (out_dir / required).is_file(), "generated core file missing")

    # the DNA itself, and the stage graph it declares
    steps = dna.get("execution_matrix", [])
    record("dna:identity", bool(dna.get("identity", {}).get("genome_version")), "no genome version")
    record("dna:stages_declared", bool(steps), "execution_matrix is empty")
    record("dna:contract_vocabulary", set(dna.get("execution_contract", {})) >= {
        "optional_requires", "external_inputs", "mutates", "invalidates",
        "evidence", "failure_policy", "scope", "trust_tier",
    }, "execution_contract is missing fields")
    record("dna:views_declared", bool({k for k in dna.get("views", {}) if not k.startswith("_")}),
           "no views declared, so nothing is queryable")
    for name, spec in dna.get("views", {}).items():
        if name.startswith("_"):
            continue
        record(f"view:{name}:caveat", bool(spec.get("caveat")),
               "a view without a caveat hands over rows with their conditions removed")

    lenses = []
    for path in sorted((out_dir / "lenses").glob("*.py")):
        try:
            py_compile.compile(str(path), doraise=True)
            node = next(
                item for item in ast_module.parse(path.read_text(encoding="utf-8")).body
                if isinstance(item, ast_module.Assign)
                and any(getattr(t, "id", None) == "LENS" for t in item.targets)
            )
            lens = ast_module.literal_eval(node.value)
            valid = (
                isinstance(lens, dict)
                and isinstance(lens.get("id"), str)
                and all(isinstance(lens.get(key), list) for key in ("requires", "produces", "feeds"))
                and isinstance(lens.get("evidence"), str)
                and lens.get("trust_tier") in tiers
            )
            record(f"lens:{path.name}:contract", valid,
                   "LENS must declare id, requires, produces, feeds, evidence and trust_tier")
            if valid:
                lenses.append((lens, path))
        except Exception as error:
            record(f"lens:{path.name}:compiles", False, f"{type(error).__name__}: {error}")

    identifiers = [lens["id"] for lens, _ in lenses]
    outputs = [output for lens, _ in lenses for output in lens["produces"]]
    record("lens_ids_unique", len(identifiers) == len(set(identifiers)), "duplicate lens id")
    record("artifact_producers_unique", len(outputs) == len(set(outputs)),
           "two lenses declare the same output")

    produced = {output: lens["id"] for lens, _ in lenses for output in lens["produces"]}
    pending = {lens["id"]: {produced[need] for need in lens["requires"] if need in produced}
               for lens, _ in lenses}
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
            record(f"lens:{lens['id']}:input:{need}",
                   need in produced or need in external or need in optional,
                   "no lens produces this and it is not declared external or optional")
        for output in lens["produces"]:
            artifact = out_dir / output
            record(f"lens:{lens['id']}:output:{output}", artifact.is_file(),
                   "declared output missing; run ./capture")
            if artifact.is_file() and artifact.suffix == ".json":
                try:
                    json.loads(artifact.read_text(encoding="utf-8"))
                except (OSError, ValueError) as error:
                    record(f"artifact:{output}:parses", False, str(error))
            elif artifact.is_file() and artifact.suffix == ".md":
                record(f"artifact:{output}:not_empty",
                       bool(artifact.read_text(encoding="utf-8").strip()), "empty document")

    return {
        "status": "PASS" if not failures else "FAIL",
        "scope": "structural contracts and artifact integrity; not semantic claim correctness",
        "lens_count": len(lenses),
        "lens_evidence": {lens["id"]: {"evidence": lens["evidence"], "trust_tier": lens["trust_tier"]}
                          for lens, _ in lenses},
        "checks": checks,
        "failures": failures,
        "generated_files": {path.relative_to(out_dir).as_posix():
                            hashlib.sha256(path.read_bytes()).hexdigest()
                            for path in sorted(out_dir.rglob("*.py"))},
    }


if __name__ == '__main__':
    report = _verify_instrument(OUT, DNA)
    (OUT / 'verification.json').write_text(
        json.dumps(report, indent=2, sort_keys=True) + chr(10), encoding='utf-8')
    print(json.dumps(report, indent=2))
    raise SystemExit(0 if report['status'] == 'PASS' else 1)
