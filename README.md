# Founderealm Lens

**Your whole codebase as one SQL database for Claude Code, in any language. Like grep, with joins.**

Version 2.0.0-beta.3, a public beta. Tested by hand on macOS (Apple silicon) and Linux
(arm64). Every release is also built and checked on Linux (x86_64) and Windows (x86_64)
before it is published, but those two have not yet been tested by hand.

## What

Founderealm Lens is a Claude Code plugin and MCP server. It reads every file in a
repository once with [tree-sitter](https://tree-sitter.github.io/) and writes what it reads
into one local [DuckDB](https://duckdb.org/) database, the map:

- every file, read or skipped, with the reason it was skipped;
- every named syntax node, with its type, position and text;
- every definition, call, scope, comment and string that each language's own tree-sitter
  queries mark.

Your agent then asks the map questions in SQL instead of searching by hand: where a name is
defined, everything that calls it, what a file holds, what a change to it touches, what
nothing uses, what the docs say about it, and a diagram of who calls whom. The plugin's
skill gives the agent a written-out query for each of these.

It works in any language tree-sitter has a grammar for, and knows nothing about any of them
itself: what it reads comes from each language's grammar and that grammar's own queries.

## Why

An agent learning a codebase by searching it reads one file, one match, one guess at a time,
and cannot tell what it missed. The map holds every file at once, so one question answers
from all of them, and every answer says what limits it: which files were not read, and that
calls are matched by name, so they are candidates rather than proof.

## Where

Everything stays on your machine, in the repository you are working in.

- **It writes** one folder, `founderealm/`, in the repository: its settings (`terrain.toml`),
  a `lenses/` folder for saved queries, the map (`map.duckdb`) and the grammars it fetched,
  plus query corrections in `queries/` if any are written. Its own `.gitignore` keeps the
  map and the grammars out of git; the settings, saved queries and corrections are yours to
  commit. Nothing else in the repository is written or changed.
- **It reads** the files git lists (or every file, in a folder without git), minus what
  `terrain.toml` leaves out. A question can read files inside the repository and none
  outside it.
- **It needs the network** only to fetch its binary once per version, to ask which grammar
  collection release is current once each time it starts, and to fetch that release's
  grammars once per repository, all from this repository's releases, each checked against
  its SHA-256: the binary against the one the plugin carries, the grammars against the
  manifest of the collection release. Release 1.0.0 holds 373 grammars: the 372 of the
  [tree-sitter-language-pack](https://github.com/xberg-io/tree-sitter-language-pack) 1.22.1
  release, at the same revisions, and MDX. Each release carries every grammar's license in
  `NOTICES.md`.
- **It checks Bash calls** through one hook. Claude Code hands it each shell command
  before it runs; if the command runs the lens binary or its launcher, the hook blocks it
  and points the agent to the lens tools instead. In a shell, an agent trims long output
  with `| head`, `| tail` or a redirect, and a lens answer cut that way loses the caveats
  and counts that say what its rows mean. Every other command runs untouched. The hook
  keeps nothing and sends nothing.

## What it never does

- It never runs the repository's code. It reads source and nothing else.
- It never sends the repository's contents anywhere.
- In the repository it writes nothing outside `founderealm/`, and it asks before it writes
  that folder the first time. Outside the repository it keeps only the downloaded binary,
  in Claude Code's data folder for the plugin (or `~/.cache/founderealm-lens`).
- It ships no answers of its own. It carries no corrections for any language, not even ones
  true of every program in a language, and decides nothing about a codebase before it has
  read it. Every row comes from the code and the grammar that read it.

## When

Whenever an agent would otherwise search: before changing a function, to see everything
that calls it; when looking for code that nothing uses; when learning a repository it has
never seen; when it needs to know what the docs or the config say. A capture brings the map
up to the present and is cheap, so the agent captures again whenever the files may have
changed. Capture takes longer the larger the repository; it has been tested on repositories
of up to about 26,000 files.

## How

### Install

With the Claude Code command line:

```sh
claude plugin marketplace add Founderealm/Founderealm_Lens
claude plugin install founderealm-lens@founderealm
```

The first time the plugin starts, its launcher downloads the binary for your platform from
this repository's releases and runs it only if its SHA-256 matches the one in the plugin.
Binaries are built for macOS on Apple silicon, Linux (x86_64 and arm64, with glibc 2.28 or
newer: RHEL 8, Debian 10, Ubuntu 20.04 and later) and Windows (x86_64).

### Use

Ask your agent about the code. It starts with `lens_status`, which says whether there is a
map, what it covers, whether it holds together, and, where your languages' grammars mark
definitions, three questions about your repository ready to ask. Before the first capture writes `founderealm/`, it asks you.

| tool | what it does |
|---|---|
| `lens_status` | whether there is a map, how old it is, what it covers, whether it holds together, every table with its columns and caveat, and three questions ready to ask |
| `lens_query` | one SELECT over the map, or the name of a saved query |
| `lens_capture` | bring the map up to the present; the first one plants `founderealm/`, once you approve |

### Tune

No tool can carry the right settings for every codebase, so the agent using the lens tunes
it for yours, in files under `founderealm/`: which folders and files are read and by which
grammar (`terrain.toml`), what a grammar's queries miss in this codebase
(`queries/<language>/<kind>.scm`), and the questions asked often enough to keep
(`lenses/<name>.sql`). `lens_status` says where each is needed, and the skill's "fog test"
finds the calls a language's own queries do not mark. The agent tells you what it changed,
and you commit those files with your code.

### Update

When the plugin updates, the next session uses the new version, and a new grammar collection
arrives the same way, without a plugin update. Nothing in your repository changes until the
next capture, which rebuilds the map; your settings, corrections and saved queries are never
written over. `lens_status` shows the kernel and collection in use beside the ones that wrote
the map, and the agent captures again when they differ.

### Troubleshooting

- **The lens tools are missing.** `/mcp` in Claude Code shows whether the `lens` server
  connected. The launcher writes what went wrong to the server's log: no prebuilt binary
  for this platform, a download that failed, or a SHA-256 that did not match (the file is
  deleted and nothing runs). After an update, start a new session.
- **A download fails.** The binary and the grammars come from `github.com` and GitHub's
  release download host; a proxy or firewall has to allow both.
- **A file is FAILED with "the grammar ... could not be fetched".** The first capture in a
  repository needs the network for the grammars. Capture again once it is there.
- **Linux says a `GLIBC_` version is not found.** The system is older than glibc 2.28.
- **The answers look stale.** `lens_status` says how old the map is; capture again.

Anything else goes to the [issues](https://github.com/Founderealm/Founderealm_Lens/issues),
and a security problem to [SECURITY.md](SECURITY.md).

## Who

Made by [Founderealm](https://github.com/Founderealm). Questions and problems go to this
repository's [issues](https://github.com/Founderealm/Founderealm_Lens/issues). If it helps
you, you can support it on [Patreon](https://patreon.com/Founderealm).

## License

Apache-2.0: see [LICENSE](LICENSE) and [NOTICE](NOTICE). The binary is built from private
source and published under the same license. The licenses of the software compiled into it
are in [THIRD_PARTY.md](THIRD_PARTY.md), which every release carries beside the binaries.
