# Founderealm Lens

Three files, one job each. Drop them into a repository they have never seen, run once,
and they leave behind a small set of tools that answer questions about that repository
with evidence attached. Then delete all three; what they planted keeps working without
them.

| file | what it is |
|---|---|
| `founderealm_seed.py` | the coordinator: survey the terrain, write the tools, ask before writing anything |
| `founderealm_code.py` | the product: every function that gets copied into the repository |
| `lens_dna.json` | the declarations: parser rules, directories to walk, tables and their caveats, dependency pins, the starter lenses |

The split is the point. A change to the parser is a change to `founderealm_code.py` and
lands in every tree. A change to what gets built is one diff in `lens_dna.json` and no
Python at all. A change to how germination behaves stays in the seed. The filename tells
you the blast radius before you open the file.

None of the three is read at runtime. Every generated file carries the declarations its
own code names, so a germinated tree owes nothing to the thing that made it.

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

**Requires Python 3.10 or newer.** It says so and stops, rather than germinating and
failing later.

```sh
uv tool install founderealm-lens   # or: pipx install founderealm-lens
founderealm activate               # survey the repository, plant the tools
```

Installing brings all three files and resolves the parser runtime for your platform, so
there is nothing to place by hand and the first capture has nothing to download.
Installing writes nothing to any repository; `activate` asks before it creates a single
file.

Or take the three files and run them. No package manager is involved, and the seed
fetches its own hash-verified runtime on first capture:

```sh
python3 founderealm_seed.py            # dormant: prints help, creates nothing
python3 founderealm_seed.py activate   # survey the repository, plant the tools
```

All three must sit in the same directory. If one is missing, the seed says which and
writes nothing.

### What it costs

The three files are about 80 KB and readable end to end before you run anything. What they install is not small: the parser runtime and query engine are
roughly 60 MB, and a germinated tree with compiled grammars is around 85 MB. That is
the price of parsing 371 languages offline, and it is all inside the repository or the
environment you installed into.

Activation reads the file list, names the terrain, writes the tooling, and stops. It
parses nothing and downloads nothing, and it asks before writing anything. Then, in
the repository:

```sh
./capture    # build the map
./search     # ask it something; start with ./search views
./verify     # check the instrument, not your code
```

On Windows, `capture.cmd`, `search.cmd` and `verify.cmd` sit beside them. Both sets are
written on every host, because a repository germinated on one platform gets opened on
another.

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

## What capture actually computes

Capture is not a script that runs eight things in order. It is a fixed point and a
topological sort over a graph it reads off the files in `founderealm/lenses/`, which is
why adding or deleting a lens needs no registry and no edit anywhere else.

Let **L** be the lenses found by parsing each file in `lenses/` for its `LENS` block, and
for each lens `l` let `req(l)` and `prod(l)` be its declared inputs and outputs.

**1. The producer map.** Every artifact is claimed by the lens that declares it.

    P : A -> L,  P(a) = l  where a in prod(l)

**2. Blocking, as a least fixed point.** A lens is blocked if an input exists that
nothing produces, and blocking then propagates along edges until nothing more changes.
`E` is the set of external inputs, satisfied by the world rather than by a lens:
`repository`, `prior_runs`, `dna`, `lens_plan.json`, `all_previous_steps`.

    B_0     = { l : exists r in req(l),  r not in dom(P) + E + optional(l) }
    B_(n+1) = B_n + { l : exists r in req(l) ∩ dom(P),  P(r) in B_n }
    B       = the least fixed point of that

**3. The order.** Kahn's algorithm over the runnable subgraph `L \ B`, taking each
ready set in sorted order so the same tree always produces the same sequence.

    depends(l) = { P(r) : r in req(l) ∩ dom(P) } \ B
    order      = topological sort of (L \ B, depends)

A cycle is the case where the runnable set is non-empty and no lens is ready. Capture
stops and names the cycle rather than running part of it.

**4. Orphans.** Artifacts on disk that no present lens claims, minus the ones the seed
and the bootstrap write for themselves.

    O = { a on disk } \ ( image(P) + seed_owned )

A deleted lens therefore produces two honest signals rather than a crash: its outputs
appear in `O`, and everything downstream appears in `B`, named.

### The graph as it ships

Read down the left for what a lens eats, right for what it emits. The depth column is
the level Kahn's algorithm assigns, so lenses at the same depth are independent of each
other and only their names decide the order.

| depth | lens | requires | produces | evidence |
|---|---|---|---|---|
| 0 | `inventory` | *repository* | `inventory.json` | direct filesystem inventory |
| 1 | `capability` | `inventory.json` | `capabilities.json` | tree-sitter runtime probe |
| 1 | `tests` | `inventory.json` | `tests.json` | directory and filename convention |
| 2 | `parsing` | `inventory.json`, `capabilities.json` | `maps/files.json`, `maps/symbols.json`, `maps/imports.json`, `maps/calls.json`, `parse_summary.json` | tree-sitter syntax |
| 3 | `contracts` | *dna*, `maps/files.json`, `maps/symbols.json`, `maps/imports.json`, `maps/calls.json` | `contracts.json` | structural contract validation |
| 3 | `dependencies` | `maps/files.json`, `maps/imports.json` | `dependencies.json` | derived import token resolution |
| 4 | `changes` | `maps/files.json`, `dependencies.json`, *prior_runs* | `changes.json` | file hash and derived impact |
| 5 | `ledger` | *all previous steps* | `execution_matrix.json`, `history/runs.json` | derived run record |

`parsing` is the only lens that reads source. Everything below depth 2 reads artifacts,
never files, which is why a wrong answer about a symbol is a `parsing` question and a
wrong answer about an edge is a `dependencies` question.

### From artifact to answer

`./search` does not read the graph. It materializes each artifact as a table and then
disables external file access, so a query cannot reach back into the repository.

| table | artifact | collection |
|---|---|---|
| `file` | `maps/files.json` | `files` |
| `symbol` | `maps/symbols.json` | `symbols` |
| `import` | `maps/imports.json` | `imports` |
| `call` | `maps/calls.json` | `calls` |
| `dependency` | `dependencies.json` | `edges` |
| `unresolved` | `dependencies.json` | `unresolved_imports` |
| `test` | `tests.json` | `tests` |
| `impact` | `changes.json` | `impact` |
| `skipped` | `parse_summary.json` | `skipped` |

Each table carries the caveat that limits it, and the caveat prints with the rows.

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
