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
import ast
import hashlib
import inspect
import json
import sys
from pathlib import Path
from typing import Any

import founderealm_code as product

# DNA is data, not host-specific behavior.
DNA_FILENAME = "lens_dna.json"

# The declarations are a blueprint: read while a tree is built and never after,
# because every generated file carries the declarations it needs. Once a tree exists,
# all three files can be deleted.

def _dna_path() -> Path:
    """The data file this program reads. Beside the seed, or beside the installed module."""
    return Path(__file__).resolve().parent / DNA_FILENAME

def _dna() -> dict[str, Any]:
    """The declarations this program runs on, read from the data file, not from code."""
    path = _dna_path()
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise SystemExit(
            f"[Founderealm] {DNA_FILENAME} is missing. It must sit beside "
            f"{Path(__file__).name}, at {path}."
        ) from None
    except ValueError as error:
        raise SystemExit(f"[Founderealm] {path} is not valid JSON: {error}") from None


# Derived from the stages, so there is one declaration of this fact rather than two.
ARTIFACTS = tuple(
    output for step in _dna()["execution_matrix"] for output in step["produces"]
)
OUT_NAME = _dna()["activation"]["output_dir"]


def _find_repo_root(start: Path) -> Path:
    current = start.resolve()
    for candidate in (current, *current.parents):
        if (candidate / ".git").exists():
            return candidate
    return current


def _product_functions() -> dict[str, Any]:
    """Every function in the product module, by name. The pool a lens is built from."""
    return {
        name: value
        for name, value in vars(product).items()
        if inspect.isfunction(value) and value.__module__ == product.__name__
    }


def _referenced_names(source: str) -> set[str]:
    return {node.id for node in ast.walk(ast.parse(source)) if isinstance(node, ast.Name)}


def _recipe_closure(recipe: str) -> tuple[Any, ...]:
    """The seed functions a recipe reaches, read from the recipe rather than listed.

    Read from the recipe rather than listed, so the two cannot disagree. Emitted in
    definition order so the same recipe always produces the same bytes.
    """
    functions = _product_functions()
    # Provided by the lens prelude in a form suited to a germinated tree; emitting the
    # seed's versions would shadow them with code that looks beside the seed instead.
    provided = {"_dna", "_dna_path"}
    needed: set[str] = set()
    pending = [name for name in _referenced_names(recipe) if name in functions]
    while pending:
        name = pending.pop()
        if name in needed:
            continue
        needed.add(name)
        pending.extend(
            found
            for found in _referenced_names(inspect.getsource(functions[name]))
            if found in functions and found not in needed
        )
    return tuple(
        sorted(
            (functions[name] for name in needed - provided),
            key=lambda function: function.__code__.co_firstlineno,
        )
    )


def _recipe_dna(recipe: str, helper_source: str, dna: dict[str, Any]) -> dict[str, Any]:
    """The declarations this lens reads, so it can carry them and owe nothing at runtime.

    A germinated tree must keep working after all three files are deleted, so
    no generated file may read a declarations file. Only the keys the code names travel.
    """
    text = recipe + helper_source
    return {
        key: value
        for key, value in dna.items()
        if f"'{key}'" in text or f'"{key}"' in text
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
        # Written on every host, not only Windows: a repository is shared, and a tree
        # germinated on one platform gets opened on another.
        windows = root / f"{name}.cmd"
        windows.write_text(
            "@echo off\r\n"
            "rem Written by founderealm_seed during activation. The interpreter is pinned\r\n"
            "rem to the one that germinated this tree. Override with FOUNDEREALM_PYTHON.\r\n"
            'if defined FOUNDEREALM_PYTHON (set "_FR_PY=%FOUNDEREALM_PYTHON%")'
            f' else (set "_FR_PY={sys.executable}")\r\n'
            f'"%_FR_PY%" "%~dp0{output_dir.name}\\{script}"{verb} %*\r\n',
            encoding="utf-8",
        )
        created.append(windows.name)
    return created


def _write_runtime(output_dir: Path) -> None:
    """Write the shutter: one call into the capture routine expanded above."""
    output_dir.mkdir(parents=True, exist_ok=True)
    out_name = output_dir.name
    (output_dir / "shutter.py").write_text(
        "#!/usr/bin/env python3\n"
        '"""Non-destructive Founderealm instrumentation shutter, grown by founderealm_seed.py."""\n'
        "import json\nimport os\nimport subprocess\nimport sys\nfrom pathlib import Path\n\n"
        f"ROOT = Path(__file__).resolve().parents[1]\nOUT_NAME = {out_name!r}\n\n"
        + inspect.getsource(product._run_capture)
        + "\n\nif __name__ == '__main__':\n"
        "    if sys.argv[1:] != ['capture']:\n"
        "        raise SystemExit('shutter accepts only capture')\n"
        "    raise SystemExit(_run_capture(ROOT, OUT_NAME))\n",
        encoding="utf-8",
    )
    (output_dir / "shutter.py").chmod(0o755)


def _write_search_recipe(output_dir: Path, dna: dict[str, Any]) -> None:
    """Write the generated query recipe and its declared tables."""
    output_dir.mkdir(parents=True, exist_ok=True)
    out_name = output_dir.name
    views = {
        name: spec for name, spec in dna["views"].items() if not name.startswith("_")
    }
    helpers = inspect.getsource(product._connect_tables) + "\n\n" + inspect.getsource(product._query)
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
        + inspect.getsource(product._verify_instrument)
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
        "from importlib.machinery import PathFinder\nfrom importlib.metadata import PackageNotFoundError, distributions, version\n"
        "from pathlib import Path\nfrom typing import Any\nfrom urllib.request import urlopen\n\n"
        f"ARTIFACTS = {ARTIFACTS!r}\nROOT = Path(os.environ['FOUNDEREALM_ROOT']).resolve()\nOUT = ROOT / {out_name!r}\n\n"
    )
    for step in dna["execution_matrix"]:
        entry = getattr(product, f"lens_{step['id']}")
        recipe = inspect.getsource(entry)
        helper_source = "\n\n".join(
            inspect.getsource(helper) for helper in _recipe_closure(recipe)
        )
        carried = _recipe_dna(recipe, helper_source, dna)
        declarations = (
            "# Carried, not read: this lens owes nothing to any file once it is written,\n"
            "# and holds only the declarations its own code names.\n"
            f"DNA = {carried!r}\n\n\n"
            "def _dna() -> dict[str, Any]:\n"
            "    return DNA\n\n"
        )
        source = (
            '#!/usr/bin/env python3\n"""Expanded Founderealm lens recipe.\n\n'
            f"Question: {step['id']}\n"
            f"Inputs: {', '.join(step['requires']) or 'repository filesystem'}\n"
            f"Outputs: {', '.join(step['produces'])}\n"
            "This file is standalone after germination; its source was expanded from\n"
            'the seed recipe so it can be inspected, changed, or replaced locally.\n"""\n\n'
            + lens_prelude
            + declarations
            + helper_source
            + f"\n\nLENS = {step!r}\n\n"
            + recipe
            + f"\n\nif __name__ == '__main__':\n    {entry.__name__}()\n"
        )
        (lenses_dir / f"{step['id']}.py").write_text(source, encoding="utf-8")


def _write_instructions(root: Path) -> bool:
    """Write the root handoff document only when it does not already exist."""
    document = _dna()["documents"]["instructions"]
    path = root / document["filename"]
    if path.exists():
        return False
    path.write_text(document["text"], encoding="utf-8")
    return True


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


def _survey(root: Path, output_dir: Path, dna: dict[str, Any]) -> dict[str, Any]:
    """Name the ground from the file list alone: no parsing, no grammar, no network."""
    files, mode = product._candidate_files(root, output_dir, dna)
    supported, unsupported, not_source = product._classify_files(files, dna)
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
        "non_source_files": len(not_source),
        "output_dir": str(output_dir),
        "identified_by": "file_extension",
    }


def _germination_report(terrain: dict[str, Any], output_dir: Path) -> str:
    """What was found, what was planted, and the one command to run next."""
    runtime_line = _runtime_sentence(
        product._environment_satisfies(_dna()["dependencies"]["packages"])
    )
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
        "and it downloaded nothing.",
        runtime_line,
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


def _runtime_sentence(present: bool) -> str:
    """Say which of the two runtime paths this tree is on, rather than assuming one."""
    if present:
        return (
            "The parser runtime is already installed in this environment, so the first\n"
            "capture downloads nothing and builds the map straight away."
        )
    return (
        "The first capture installs a hash-verified parser runtime and then builds the\n"
        "map, which is a separate thing to agree to."
    )


def _climb_notice(start: Path, root: Path) -> str:
    """Say so when the repository root is not the directory the command was typed in.

    The root is found by walking up to a .git, which lands on the wrong terrain when the
    directory merely sits under an unrelated repository. Mapping somewhere other than
    where the operator is standing must be stated, not merely implied by a path.
    """
    start = start.resolve()
    if start == root:
        return ""
    return "\n".join(
        (
            "",
            f"NOTE: you typed this in  {start}",
            f"      which sits under a repository rooted at  {root}",
            "      and that root, not the directory you are in, is what will be mapped.",
            "      To map the directory you are in instead, run it with:  --root .",
            "",
        )
    )


def _activation_notice(root: Path, output_dir: Path, start: Path | None = None) -> str:
    return "\n".join(
        (
            "Founderealm Lens: Informed Activation",
            "",
            "This creates a repository-local intelligence camera for evidence-led navigation.",
            _climb_notice(start if start is not None else root, root),
            f"Read scope:  {root}",
            f"Write scope: {output_dir}",
            "",
            "It will create shutter, search, verification, installer, lens, JSON, Markdown, cache, and local parser-runtime files.",
            "Nothing it writes is hidden: one visible directory, three visible commands.",
            "It appends entries to .gitignore, or creates that file if it is absent, so",
            "the runtime it installs is not committed to your repository.",
            "It may create FOUNDEREALM_INSTRUCTIONS.md only when that file is absent.",
            "It will not modify observed source files or send telemetry.",
            "It reads the FILE LIST only, to name the terrain. It parses nothing and",
            "downloads nothing.",
            _runtime_sentence(product._environment_satisfies(_dna()["dependencies"]["packages"])),
        )
    )


def activate(
    root: Path, output_name: str, *, authorized: bool = False, climb: bool = True
) -> int:
    """Survey the repository, write local tooling, and stop before capture.

    climb=False honours the given directory as the root. A named root is an instruction,
    so walking up out of it would override the operator rather than help them.
    """
    dna = _dna()
    requested = root
    root = _find_repo_root(root) if climb else root.resolve()
    output_dir = (root / output_name).resolve()
    if output_dir == root or root not in output_dir.parents:
        raise ValueError(
            "output directory must be a dedicated directory inside the repository"
        )
    if not authorized:
        print(_climb_notice(requested, root), end="")
        raise PermissionError("activation requires explicit authorization")
    terrain = _survey(root, output_dir, dna)
    _germinate(root, output_dir, dna)
    print(_germination_report(terrain, output_dir))
    return 0


MINIMUM_PYTHON = (3, 10)


def _refuse_old_python() -> int | None:
    """Stop before writing anything when the interpreter is below the declared floor.

    requires-python gates an install; nothing gates this file downloaded on its own.
    The check must precede any write, or a failure arrives after the repository changed.
    """
    if sys.version_info >= MINIMUM_PYTHON:
        return None
    running = ".".join(str(part) for part in sys.version_info[:3])
    wanted = ".".join(str(part) for part in MINIMUM_PYTHON)
    print(
        f"[Founderealm] Needs Python {wanted} or newer; this is {running}."
        f"\n[Founderealm] Nothing was written. Run it with a newer interpreter.",
        file=sys.stderr,
    )
    return 1


def main(argv: list[str] | None = None) -> int:
    refusal = _refuse_old_python()
    if refusal is not None:
        return refusal
    parser = argparse.ArgumentParser(
        description="Dormant Founderealm Lens seed. No files or dependencies are created without activate."
    )
    subparsers = parser.add_subparsers(dest="command")
    activate_parser = subparsers.add_parser(
        "activate", help="germinate Founderealm Lens in a repository"
    )
    activate_parser.add_argument(
        "--root",
        type=Path,
        default=None,
        help="map this directory, exactly; without it the repository root above the "
        "current directory is found and mapped",
    )
    activate_parser.add_argument("--output", default=_dna()["activation"]["output_dir"])
    args = parser.parse_args(argv)
    if args.command != "activate":
        parser.print_help()
        print(
            "\n[Founderealm] Dormant. Run the activate command to create any files or install dependencies."
        )
        return 0
    try:
        climb = args.root is None
        start = Path.cwd() if climb else args.root
        root = _find_repo_root(start) if climb else start.resolve()
        output_dir = (root / args.output).resolve()
        print(_activation_notice(root, output_dir, start))
        try:
            answer = input("Authorize these writes? [y/N] ").strip().lower()
        except EOFError:
            # No one is there to authorize, so the answer is no.
            print("\n[Founderealm] No authorization possible without a terminal; nothing was written.")
            return 1
        if answer not in {"y", "yes"}:
            print("[Founderealm] Activation cancelled; no files were written.")
            return 0
        return activate(root, args.output, authorized=True, climb=False)
    except (OSError, PermissionError, RuntimeError, ValueError) as error:
        print(f"[Founderealm] Activation failed honestly: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
