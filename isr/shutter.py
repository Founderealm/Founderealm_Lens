#!/usr/bin/env python3
"""Non-destructive ISR instrumentation shutter, grown by founderealm_seed.py."""
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_NAME = 'isr'

def _run_capture(root: Path) -> int:
    """Find lenses by their own declarations, order what can run, and name what cannot.

    The lenses are examples. The reader is expected to add and to DELETE them, so this
    has to survive both. It did not: deleting a lens left its artifact behind as an
    orphan that downstream lenses went on reading, so capture reported success while
    feeding on data nothing produced any more; and deleting the artifact too made a
    downstream lens die on a raw FileNotFoundError with a Python traceback for a report.

    A lens whose required input no present lens produces is now BLOCKED, named, and
    skipped, along with everything downstream of it. Artifacts that no present lens
    declares are reported as orphans. That is the failure policy the DNA has declared
    from the start and nothing honored.
    """
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
                f"[ISR] {path.name} carries no readable LENS contract, not run: {error}"
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
    # Blocking is transitive: a lens reading the output of a blocked lens cannot run
    # either, and saying so is more use than letting it fail on its own.
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
            print(f"[ISR] lens dependency cycle, nothing ran: {sorted(pending)}")
            return 1
        order.extend(ready)
        for name in ready:
            pending.pop(name)
        for needs in pending.values():
            needs.difference_update(ready)

    # Written by the seed or the bootstrap rather than by a lens, so their absence from
    # any `produces` list is correct and not a finding. A check that cries wolf on its
    # own scaffolding is how the real orphans stop being read.
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
    environment = os.environ | {"ISR_ROOT": str(root)}
    for identifier in order:
        result = subprocess.run(
            [sys.executable, str(by_id[identifier])],
            cwd=root,
            env=environment,
            check=False,
        )
        if result.returncode:
            print(
                f"[ISR] {identifier} exited {result.returncode}; stages after it did not run"
            )
            return result.returncode

    print(f"[ISR] {len(order)} lens(es) ran: {', '.join(order)}")
    for identifier, reasons in sorted(blocked.items()):
        print(f"[ISR] BLOCKED {identifier}: {'; '.join(reasons)}")
    if orphans:
        print(f"[ISR] ORPHANED, produced by no present lens: {', '.join(orphans)}")
    return 0


if __name__ == '__main__':
    if sys.argv[1:] != ['capture']:
        raise SystemExit('shutter accepts only capture')
    raise SystemExit(_run_capture(ROOT))
