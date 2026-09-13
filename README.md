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

## License

Copyright 2026 Founderealm. Licensed under Apache-2.0. See [LICENSE](LICENSE) and
[NOTICE](NOTICE).

Support ongoing development through [Patreon](https://patreon.com/Founderealm).
