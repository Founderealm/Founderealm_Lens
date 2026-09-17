# Founderealm Lens

One Python file. Drop it into a repository it has never seen, run it once, and it
leaves behind a small set of tools that answer questions about that repository with
evidence attached. Then you can delete it; what it planted keeps working without it.

It reads source as text and bytes. It never imports, compiles, or executes the code
it observes.

Built for AI coding agents. Claude Code, Cursor, Copilot, Aider and anything else
working in a repository it did not write spend most of their context re-deriving the
same structure: what exists, where it is defined, what calls it. This gives that agent
a map to query instead, in SQL, and makes it answer with the limits of its own evidence
attached. It works just as well for a person with a terminal; the agent is simply the
reader that pays the highest price for a confident wrong answer.

## Why

Working in a codebase means answering the same questions over and over. Where is this
defined, what calls it, what breaks if it moves. Grep answers slowly and, worse,
answers incompletely without saying so: a slice of the truth reads exactly like all
of it, and nothing in the output marks where the looking stopped. An AI agent does
this faster than you can and then fills the gaps it did not find.

Map the repository once and those questions become lookups. The cost is paid when the
code changes; the saving lands on every question asked between changes, which is
where the hours actually go.

And the answers say when they do not know. `ABSENT`, `BLOCKED` and `UNKNOWN` are
answers here. They mean nobody surveyed that ground, and they are meant to be
reported as such rather than filled in. That is the property an agent needs most: a
model cannot tell a partial answer from a complete one unless the tool says which it
handed over.

## Use

**Requires Python 3.10 or newer.**

```sh
python3 founderealm_seed.py            # dormant: prints help, creates nothing
python3 founderealm_seed.py activate   # survey the repository, plant the tools
```

Activation reads the file list, names the terrain, writes the tooling, and stops. It
parses nothing and downloads nothing, and it asks before writing anything. Then, in
the repository:

```sh
./capture    # build the map
./search     # ask it something; start with ./search views
./verify     # check the instrument, not your code
```

Run `./capture` when the code has changed. A large, complex repository can take up to
a minute; a small one is a fraction of a second. That number is not the point. It is
paid once per change and it replaces re-deriving the same context on every question
you ask until the next one.

## What an answer looks like

```
$ ./search "SELECT kind, name, file, line FROM symbol WHERE kind = 'function'"

kind     | name     | file  | line
----------------------------------------------------------------------
function | handler  | m.py  | 1
function | Widget   | m.ts  | 1
function | arrow    | m.ts  | 4

3 row(s)
CAVEAT symbol: kind is the grammar's own node type with its suffix removed, so it is
the grammar's vocabulary and not a normalized one: class, struct, trait and interface
all appear as the language spells them. A name of <anonymous> means the grammar
declared no name field and no identifier child.
```

The caveat is the point. It prints beside the rows rather than living in
documentation, because a correct row with its conditions stripped off is how a
confident wrong answer gets made. Every table carries one. The `call` table announces
that it resolves by name, so each row is a candidate call site and not a proven edge.

`./search views` lists every table with its columns, its row count and its caveat.

## Languages

Symbols, imports and calls are read from Tree-sitter node type names, which grammars
name by convention, so there is no per-language table to maintain and no language the
tool refuses. Over three hundred grammars are reachable.

That also means it reads code that declares things by binding them to a name, not
only code that declares them with a keyword: `const Widget = () => {}` is reported as
the function `Widget`, and an arrow function sitting in an object literal is found.

Where a grammar will not load, that is reported with the reason rather than passed
over.

## What it writes, and where

Activation creates only its own named things: `./capture`, `./search`, `./verify`,
the `founderealm/` evidence directory, `FOUNDEREALM_INSTRUCTIONS.md` if no such file exists,
and its own entries appended to `.gitignore`. Source files are not modified.

Parser dependencies install under `founderealm/dependencies/`, inside the repository, never
into your home directory. Wheels are pinned to exact versions and each is checked
against the SHA-256 the package index publishes; grammars arrive as one archive whose
digest is published in a manifest inside a wheel that was already verified.

After that first capture there is no network traffic at all. You do not have to take
that on faith:

```sh
HTTPS_PROXY=http://127.0.0.1:9 HTTP_PROXY=http://127.0.0.1:9 ./capture
```

If that succeeds, nothing reached out. If something ever does, that command starts
failing.

## Lenses are examples, not a framework

`founderealm/lenses/` holds eight small scripts. Each declares what it requires, what it
produces, and what kind of evidence it rests on. The runtime reads those declarations
out of the files themselves, so **adding a lens means dropping a file in the
directory**. There is no registry to edit.

Delete the ones you do not want. `./capture` notices: it names artifacts that nothing
produces any more, and it blocks and names any lens whose input is gone rather than
failing on it.

**A lens is code, and it runs with your permissions.** The eight that ship only read
source and write their declared artifacts. Ones you add are yours to trust.

## Limits

- **Structural, not semantic.** `./verify` proves contracts, generated code and
  artifact integrity, not whether any claim in the maps is true. It says so in its
  own output.
- **Call sites resolve by name**, not by receiver type. Candidates, not proven edges.
- **Tests are found by directory and filename convention.** Nothing is executed and
  no outcome is recorded, so the tool can say a test exists and never that it passes.
- **Tree-sitter grammars are compiled native code** loaded into the process. That is
  inherent to Tree-sitter rather than to this tool, and it is worth knowing.

## License

Copyright 2026 Founderealm. Licensed under Apache-2.0. See [LICENSE](LICENSE) and
[NOTICE](NOTICE).

Support ongoing development through [Patreon](https://patreon.com/Founderealm).
