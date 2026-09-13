<!--
SSOT PROTOCOL
This file describes the PORTABLE SEED: what it is, what it can already do, and what it
still needs from the parent's parts bin.
- What is built and running in THIS repository -> 00_START_HERE.md
- Founderealm (the main program) architecture -> MASTER_GUIDE.md
- ASCII-only. No emoji. No em dashes.

The seed itself is deliberately NOT in this repository. It would collide with the parent
at ./capture and ./search, parse mapping/ as terrain, stand up a second card catalogue
with no way for a reader to know which instrument answered, and stop being a sealed
reference the moment it sat somewhere editable. Keeping it out is what keeps it provable.
-->

# ISR - THE PORTABLE SEED

**What this document is.** An accurate description of a working, tested artifact, and an
honest list of what the mature instrument in this repository has that the seed does not.

**What this document is not.** A description of what runs here. That is
`00_START_HERE.md`.

Read the two as complementary halves rather than as an ancestor and a descendant. The
seed is the architecture. The parent is the intelligence. Each holds something the other
needs.

---

## The founding metaphor (canon)

ISR is a self-symbiotic seed. A seed was evolution's leap that let life leave its native
water, because the seed carries its own provisions, its own genome and its own protection.
ISR is that leap for code intelligence: a package that drops onto a repo it has never seen
and takes root. Most tools are spores that need the water to already be there. ISR is the
seed that packed its own.

Two organisms in one shell. **The mycelium** grows down and out: it threads through every
file, decomposing code into facts and weaving the connective web beneath everything. It is
persistent, and it is the agent's memory across session amnesia. **The bloom** grows up
toward the light: it turns that substrate into queryable answers delivered into the
agent's context. It is ephemeral and regenerates from the mycelium on demand.

The agent is the water and the pollinator. Its arrival germinates the seed, its return
keeps the intelligence alive, and it carries the nectar to the fruit, which is the host
program's shipped, working code. Intelligence has no value until a pollinator turns nectar
into fruit.

Two survival laws govern the species:

1. **Germinate on hostile ground without dying, and never poison the field.**
2. **Bad nectar kills your pollinators. Never lie.** Truthful intelligence is not ethics
   here, it is reproduction: it is how the seed survives from repo to repo.

---
---

# SECTION 1 - WHAT THE SEED IS, AND WHAT IT CAN ALREADY DO

One Python file of roughly 1,500 lines, dormant at rest. It has germinated on foreign
repositories in repeated trials and taken root each time without damaging the host.

## A seed, not an application

Run it without the activation verb and it creates nothing and prints what it would do.
Activation is gated on explicit authorization and preceded by a notice stating the read
scope, the write scope, and every category of file it may create. On activation it writes
its own runtime, its own query recipe, its own verifier, its own lens package, platform
installers and repository-root command wrappers, then runs one capture.

**After that the seed is finished.** The germinated tooling is what gets reused from then
on, indefinitely, and it needs nothing from the seed to keep working.

## It declares a write boundary and honors it

It reads repository source. It writes one dedicated output directory, the command
wrappers at the repository root, and an agent-instruction file only when none exists. It
does not modify observed source. It emits no telemetry.

Those are not prose claims. A trust report is written as an artifact on every activation,
stating the read scope, the write scope, whether the network was used, and how
dependencies were verified.

## Its dependencies are sealed, not trusted

Exact versions, binary wheels only, and every wheel's SHA-256 checked against the digest
the package registry publishes for that exact filename over TLS. The install lands in a
staging directory and atomically replaces the runtime only after the whole lock verifies;
a failure deletes the staging directory and states plainly that host source was not
modified. A later run re-verifies the installed runtime file by file against recorded
hashes and skips the network entirely when it already matches.

## It is language-agnostic by construction, in two labelled tiers

This is the seed's largest advantage over the parent, and the breadth is not theoretical:
it has been run against more than twenty languages in a single repository at once and
produced maps for all of them.

- **Identification** comes from a general-purpose lexer registry covering hundreds of
  file types, with the embedded genes and then the bare extension as fallbacks. It does
  not refuse a file for being unfamiliar.
- **Parsing** comes from a bundled grammar pack covering well over a hundred languages.
  Each grammar is probed at runtime and recorded as available or unavailable with a
  reason.
- **Depth is negotiated, and then stated.** A language with an embedded gene is parsed
  *semantically* into typed symbol kinds such as class, function, interface, trait,
  struct and type. A language without one is parsed *generically*: any syntax node
  carrying a name field is harvested as a declaration, which holds across grammars
  because that field is the conventional one for named declarations.

The discipline is that the tiers are never confused. Every file record carries which tier
parsed it. Every symbol carries whether its evidence was direct or generic. The capability
artifact reports the tier per language. And where a grammar parses but no gene exists, the
seed writes down the question someone should answer to supply one, rather than guessing or
failing.

So the embedded language list is a table of semantic depth, not a capability ceiling.
There is an unbounded generic floor beneath it.

## Its stage graph is declared, and found without a registry

Eight stages: inventory, capability, parsing, dependencies, tests, changes, contracts,
catalogue. Each declares what it requires, what it produces, what it feeds, the kind of
evidence it rests on, and a provenance tier for its own recipe. Execution order is derived
by topological sort with cycle detection, never maintained by hand.

After germination each stage is a standalone script carrying its own contract, and the
runtime finds them by reading those declarations out of the files themselves. **Adding a
lens means dropping a file into a directory.** There is no registry to edit and therefore
no registry to drift from. An example lens ships beside them to make the contract
concrete.

The contract vocabulary is itself declared, including fields the parent has no equivalent
for: a soft-requirement distinction, explicit statements of what a stage mutates and what
it invalidates, a failure policy chosen from block-downstream, emit-unknown or
emit-partial, the population a stage may inspect, and the trust tier of its recipe.

## It verifies its own generated code

An independent verify command, itself generated, compiles every lens, validates every
contract, checks that stage identifiers and artifact producers are unique, proves the
dependency graph acyclic, confirms every declared input is either produced upstream or
declared external, and confirms every declared output exists and parses. It records a hash
of every generated file and writes its report as an artifact.

It also states its own limit: structural contracts and artifact integrity, explicitly not
semantic claim correctness. That is the state-the-denominator discipline, volunteered
rather than retrofitted after a bare PASS misled someone.

## It separates what changed from how much time passed

Per-file hashes are compared against the previous run, and changes propagate through
reverse dependency edges into an impact set with a depth on every entry. A repository
fingerprint is a stable root over the ordered file and hash set. A second fingerprint
deliberately excludes run timestamps, so two runs can be compared on whether the
intelligence actually changed rather than on whether the clock moved. Run history is
bounded by design.

## What it writes is honest about its own shape

Artifact writes are atomic: temporary file, then replace. The findings document summarizes
every artifact without assuming its schema, so it cannot go stale when an artifact changes
shape. Git's own file list is the inventory authority so ignore rules stay authoritative,
and when git is unavailable the fallback mode is named in the output rather than silently
substituted.

## And it is fast

Eight stages complete in under a second.

That number is load-bearing rather than a micro-optimization. The parent's capture takes
around forty seconds, which is what forces a deliberate press-the-shutter model and makes
"is this stale?" a question the reader has to keep asking. At sub-second the question stops
existing, and continuous intelligence follows from speed rather than from a daemon.

---
---

# SECTION 2 - WHAT IT STILL NEEDS FROM THE PARTS BIN

All of the following exists and runs in this repository. None of it is in the seed.

## 1. A query engine

The seed has no database. It writes JSON artifacts and answers queries by scanning a card
catalogue in process, with a small boolean expression language supporting AND, OR, NOT,
parentheses and field-value terms. That is well past a substring match and it costs no
dependency, but it cannot join, cannot aggregate, and cannot answer a question spanning
two artifacts without the caller loading both.

**DuckDB is the right swap, and the dependency risk has been measured rather than
assumed.** The current release declares no mandatory runtime dependencies at all: every
package in its metadata sits behind an optional extra. It therefore installs as exactly
one package under the seed's no-dependency, exact-version, hash-verified model, and the
seed's wheel verification already handles platform-specific binaries correctly because it
checks the digest published for whichever filename was selected.

It requires Python 3.10 or newer, which is already this seed's floor, so it costs
nothing. Installed size is not a consideration and should not be raised as one: a
compiled grammar set is the price of reading any language, and it is a one-time static
cost of the same order as any virtual environment a developer already carries.

What it buys is the parent's entire relational surface: one statement across every
artifact at once, real list columns, window functions, and joins that are impossible
today.

## 2. Declared views with caveats attached to the answers

The most valuable honesty feature the parent has, and the hardest won. Every view is
declared with its grain, its columns, and a plain statement of what would make a reader
misread its rows: that call sites resolve by name and are candidates rather than proven
edges, that one findings table holds raw pre-investigation hits whose row count overstates
the problem, that a null means never measured rather than zero.

The seed carries an evidence field on every record, which is the foundation for this. It
has no caveat layer, and a correct row with its conditions stripped off is exactly how a
confident wrong answer gets made.

## 3. A read-window gate

The seed's search prints every match as JSON with no size governor. That is the precise
failure this whole lineage exists to answer: an artifact that grows until the reader stops
reading and starts inventing, silently, with fabricated output indistinguishable from
sourced output.

The parent refuses past a threshold sized for the weakest reader, reports how large the
answer is and where its weight sits per file, and requires an explicit yes. Nothing is
truncated and nothing is written to disk.

Of everything in this section this matters most, because it protects the reader rather
than the data.

## 4. The output contract

Both parent commands refuse to run when their output cannot survive the trip, from one
shared implementation so the two cannot drift. An answer is its rows plus the caveats that
change their meaning plus the age of the evidence, so a filter that keeps only the rows
produces a shorter answer that is also a more confident one. And a pipeline's exit status
is the last command's, not the tool's, so a truncated run looks fine and proves nothing.

## 5. Observed writes, not merely present outputs

The seed's verifier confirms that a declared output exists. The parent's watchdog records,
per declared artifact, whether it actually saw the producing stage write it during this
run, or found it already present and older than the run, or did not find it at all. Those
are different claims, and exit zero is not accepted as evidence that anything was
produced.

## 6. Test evidence with proof states

The seed discovers tests by directory and filename convention and records that they exist.
It records no outcomes.

The parent harvests real run results and reports four states: proven, invalidated, unknown
and never run, where proven means a passing test ran and neither the file nor its test has
changed since. No clock is involved. Change invalidates a proof; time does not. The parent
also maps every production line to the tests that actually executed it, and re-runs only
the blast radius of a change.

This is the largest body of intelligence the seed lacks, and it cannot be derived from
source text at any depth. It has to be harvested from executions.

## 7. Context blurbs

The seed records line, column and byte offsets for every symbol, import and call, so it
already holds the coordinates. It shows none of them.

The parent renders a hit with three lines either side, merges overlapping windows so no
line prints twice and no false gap appears, and verifies that the recorded coordinate
still holds the expected text before printing, reporting a move rather than quietly
displaying the wrong code.

## 8. A reasoning gate

The parent can be asked for a task rather than a fact, and answers with a nine-stage
account of what the terrain supports: what it surveyed, what it cannot answer, the
falsifiers it can name, and a permit it withholds on the stages only the agent can
satisfy. A withheld permit is a statement about the ground, not a refusal.

## 9. A call-resolution caveat

The seed resolves a call to its target by reading the called expression out of the syntax
node. That is the same name-based resolution the parent uses and it carries the same
limit: any object's method of that name lands in the same bucket, so each hit is a
candidate call site rather than a proven edge. The parent says so on every answer. The
seed should carry the same caveat, because the data is equally true and equally easy to
misread.

---
---

## The inversion worth recording

The migration is usually described as moving the parent's lens pipeline onto the seed's
parser abstraction. The parser is the smallest part of what the seed has.

Worth taking from the seed: the contract model, registry-free lens discovery, the
independent verifier over generated code, the trust and failure vocabulary, the declared
and honored write boundary, and the speed.

Worth taking from the parent: the caveat layer, the read-window gate, the output contract,
observed-write verification, test evidence with proof states, context blurbs, and the
reasoning gate.

Neither list is a subset of the other. That is why both documents exist, and why the two
artifacts are kept apart.
