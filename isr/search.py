#!/usr/bin/env python3
"""ISR query recipe: a read-only relational surface over the artifacts."""
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'isr'
sys.path.insert(0, str(OUT / 'dependencies'))

VIEWS = {'file': {'artifact': 'maps/files.json', 'collection': 'files', 'grain': 'one row per parsed file', 'caveat': 'capability=derived_node_type means symbols, imports and calls were read from node type names rather than a curated table. parse_status=ERRORS_PRESENT means the grammar recovered from a syntax error, so records from that file may be incomplete.'}, 'symbol': {'artifact': 'maps/symbols.json', 'collection': 'symbols', 'grain': 'one row per declaration', 'caveat': "kind is the grammar's own node type with its suffix removed, so it is the grammar's vocabulary and not a normalized one: class, struct, trait and interface all appear as the language spells them. A name of <anonymous> means the grammar declared no name field and no identifier child."}, 'import': {'artifact': 'maps/imports.json', 'collection': 'imports', 'grain': 'one row per import, include or require', 'caveat': 'syntax names the node type it came from, or call:<name> when a language spells an import as a function call, as Ruby and Lua do. A nested container is counted once, at the outermost node.'}, 'call': {'artifact': 'maps/calls.json', 'collection': 'calls', 'grain': 'one row per call site', 'caveat': "RESOLVED BY NAME, not by receiver type. Any object's method of that name lands here, so each row is a CANDIDATE call site and not a proven edge. target=<unresolved> means the grammar put the callee somewhere none of the declared callee fields reached."}, 'dependency': {'artifact': 'dependencies.json', 'collection': 'edges', 'grain': 'one row per file-to-file edge', 'caveat': 'resolution=resolved came from a quoted path, inferred came from matching a bare token against known file stems. An inferred edge can be wrong where two files share a stem.'}, 'unresolved': {'artifact': 'dependencies.json', 'collection': 'unresolved_imports', 'grain': 'one row per import that matched no file in this repository', 'caveat': 'Usually a third-party or standard-library import, which is correct and not a defect. Absence from this table is not evidence an edge was found.'}, 'test': {'artifact': 'tests.json', 'collection': 'tests', 'grain': 'one row per file that looks like a test', 'caveat': 'Discovery is by DIRECTORY AND FILENAME CONVENTION ONLY. Nothing here was executed and no outcome is recorded, so this says a test exists and never that it passes.'}, 'impact': {'artifact': 'changes.json', 'collection': 'impact', 'grain': 'one row per file reached by a change, with its distance', 'caveat': 'Derived by walking dependency edges backwards from changed files, so it inherits the inferred-edge caveat. depth is hops, not severity. Empty on a first run, when there is no prior run to compare against.'}, 'skipped': {'artifact': 'parse_summary.json', 'collection': 'skipped', 'grain': 'one row per file that was not parsed, with the reason', 'caveat': 'A non-empty table is the honest record of a gap, not a failure of the run. Read it before treating any count as complete.'}}

def _connect_tables(out_dir: Path, views: dict) -> tuple[Any, list]:
    """Materialize every present artifact as a table, then switch file access off.

    Loading and then locking is what makes this read-only at the engine level: DuckDB
    refuses to re-enable external access while the database lives, so nothing a caller
    submits afterwards can reach the filesystem. These are TABLES and not views,
    because a view stays lazy and would keep reading the disk after the lock.

    An artifact that is absent or unreadable leaves its table uncreated and is named in
    the returned list. A table silently created empty would answer count(*) = 0, and 0
    is not the same as no records.
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
        except Exception as error:
            absent.append(f"{name} ({type(error).__name__})")
    connection.execute("SET enable_external_access=false")
    return connection, absent


def _query(connection: Any, views: dict, absent: list, argv: list) -> int:
    """One SELECT, a plain term, or the table list. A caveat travels with the answer.

    The caveat prints beside the rows rather than living in documentation, because a
    correct row with its conditions removed is how a confident wrong answer is made:
    every call row here is resolved by NAME, and a reader who does not know that will
    read a candidate as a proven edge.
    """
    import duckdb

    if not argv or argv[0] in ("-h", "--help", "views"):
        print('./search "SELECT ..."   one SELECT across the tables below')
        print("./search <term>         that term across files, symbols, imports and calls")
        print("./search views          this list\n")
        for name, spec in views.items():
            if any(entry.split(" ")[0] == name for entry in absent):
                print(f"  {name:11} ABSENT - run ./capture")
                continue
            rows = connection.execute(f'SELECT count(*) FROM "{name}"').fetchone()[0]
            columns = [d[0] for d in connection.execute(f'SELECT * FROM "{name}" LIMIT 0').description]
            print(f"  {name:11} {rows:>6} rows   {spec['grain']}")
            print(f"              columns: {', '.join(columns)}")
            print(f"              CAVEAT: {spec['caveat']}\n")
        return 0

    request = " ".join(argv)
    term = None
    # Ask the ENGINE what this is. A prefix test on SELECT let DROP TABLE and
    # COPY ... TO fall through to the term path, where they were searched for as
    # literal text and answered with a row count, which reads like an answer.
    try:
        statements = duckdb.extract_statements(request)
    except Exception:
        statements = []
    if statements:
        if len(statements) != 1 or statements[0].type.name != "SELECT":
            kind = " then ".join(statement.type.name for statement in statements)
            print(f"[ISR] One SELECT only; the engine read this as {kind}.", file=sys.stderr)
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
    except Exception as error:
        print(f"[ISR] {type(error).__name__}: {error}", file=sys.stderr)
        if absent:
            print(f"[ISR] absent tables: {absent}", file=sys.stderr)
        return 2

    names = [description[0] for description in cursor.description]
    rows = cursor.fetchall()
    print(" | ".join(names))
    print("-" * 70)
    for row in rows:
        print(" | ".join("" if value is None else str(value) for value in row))
    print(f"\n{len(rows)} row(s)" + (f" for {term!r}" if term else ""))
    # Matched on FROM and JOIN rather than anywhere in the text. A bare substring
    # attached the file caveat to a query whose only mention of it was
    # count(DISTINCT file), a column. A caveat on a table nobody read is noise, and
    # noise is how the real ones stop being read.
    read_from = set(re.findall(r'(?:from|join)\s+"?([a-z_]+)"?', sql, flags=re.IGNORECASE))
    for name, spec in views.items():
        if name in read_from:
            print(f"CAVEAT {name}: {spec['caveat']}")
    if absent:
        print(f"ABSENT tables, so this answer is partial (run ./capture): {absent}")
    return 0


if __name__ == '__main__':
    connection, missing = _connect_tables(OUT, VIEWS)
    raise SystemExit(_query(connection, VIEWS, missing, sys.argv[1:]))
