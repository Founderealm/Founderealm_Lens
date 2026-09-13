# ISR Seed

One file. Drops into a repository it has never seen, writes a small set of tools that
map that repository, and then gets out of the way. It can be deleted afterwards; the
tools it planted keep working without it.

## Use

    python3 isr_seed.py                          # dormant: prints help, creates nothing
    python3 isr_seed.py activate --root <repo>    # survey the ground, plant the tools

Activation reads the file list, names the terrain, writes the tooling, and stops. It
parses nothing and downloads nothing. Then, in the target repository:

    ./capture    build the map
    ./search     ask it something (start with `./search views`)
    ./verify     check the instrument, not your code

The first `./capture` installs a parser runtime whose wheels are pinned to exact
versions and verified against the SHA-256 digests the package index publishes. Later
captures need no network.

## What it answers

A relational surface over the artifacts, read-only at the engine level: tables are
materialized and then file access is switched off, so no query can reach the disk.

    ./search "SELECT language, count(*) FROM symbol GROUP BY 1 ORDER BY 2 DESC"

Every table carries a caveat, and the caveat prints with the rows. Call sites resolve
by name, so they are candidates and not proven edges, and the answer says so every
time rather than leaving it in documentation.

`ABSENT`, `BLOCKED` and `ORPHANED` are answers. They mean nobody surveyed that ground.

## The lenses are examples

`isr/lenses/` holds eight small scripts. Each declares what it requires, what it
produces, and what kind of evidence it rests on. The runtime reads those declarations
out of the files themselves, so adding a lens means dropping a file in the directory.
There is no registry.

Delete the ones you do not want. `./capture` names the artifacts nothing produces any
more, and blocks and names any lens whose input is gone rather than failing on it.

## Languages

Identification and parsing come from a grammar pack covering well over a hundred
languages. Symbols, imports and calls are read from node type names, which grammars
name by convention, so there is no per-language table to maintain and no language the
tool refuses. Where a grammar does not load, that is reported with the reason.

## Limits

- Structural only. `./verify` proves contracts and artifact integrity, not whether any
  claim in the maps is true. It says so in its own output.
- Tests are discovered by directory and filename convention. Nothing is executed and
  no outcome is recorded.
- Requires Python 3.10 or newer.

## License

Not yet chosen.
