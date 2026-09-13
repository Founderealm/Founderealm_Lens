# Founderealm Lens

A non-destructive code viewer that reads a repository's source, parses its structure,
and reports evidence-linked findings. It does not execute or modify the code it
observes.

## Activate

**Requirement:** Python 3.10 or newer.

Copy `founderealm_seed.py` into a repository, then run:

```sh
python3 founderealm_seed.py activate --yes
```

Activation writes only its own named tooling and artifacts: `./capture`, `./search`,
`./verify`, the `isr/` evidence directory, `FOUNDEREALM_INSTRUCTIONS.md`, and the
seed-owned `.gitignore` entries. The first `./capture` installs verified parser
dependencies under `isr/dependencies/` and builds the maps.

The source being observed remains untouched. Add lenses for repository questions;
the next `./capture` discovers and runs them.

## What It Runs

Founderealm Lens is a local inspection tool. It reads source files as text and
bytes, hashes them, and asks Tree-sitter to build syntax trees. It reports files,
symbols, imports, calls, and other evidence. It does not import, compile, or run
the language code it is observing.

The first `./capture` also bootstraps its own parser dependencies. It downloads
exact-version wheels for Tree-sitter, the language pack, and DuckDB, checks each
wheel against the published SHA-256 hash, and installs them under
`isr/dependencies/`. This is the tool's local working environment, not code from
the repository being inspected.

Capture writes its own named files and directories: `capture`, `search`, `verify`,
`isr/`, and the Founderealm instruction file. It does not rewrite the source files
it reads.

Lenses are small Python extensions that answer additional repository questions.
Because they are code, a lens runs with the same permissions as the user who runs
`./capture`. Use lenses you trust. The built-in lenses only inspect source and
write their declared evidence artifacts; lenses you add are your responsibility.

## License

Copyright 2026 Founderealm. Licensed under Apache-2.0. See [LICENSE](LICENSE) and
[NOTICE](NOTICE).

Support ongoing development through [Patreon](https://patreon.com/Founderealm).
