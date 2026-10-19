---
name: founderealm-lens
description: >
  The repository as one SQL database, any language. Use before grep: definitions, calls,
  what a change touches, dead code, docs, diagrams. Recipes and rules for lens_query.
---

# Founderealm Lens

The repository you are in, as one DuckDB database. One capture fills it; every question
is a SELECT. It reads source and never runs it. Capture is cheap and brings the map to now:
capture whenever the files may have changed, rather than answer from an old map.

## The dials are yours

The kernel ships defaults, not every repository. No tool could carry the settings for
every codebase's layout, languages and grammars, so each repository's map is tuned by the
agent using it, in files under `founderealm/` that the repository owns and the next capture
reads. Tuning is normal use, not repair: after a capture, read `lens_status`, turn what it
points at, capture again, and see the counts move. Tell the user what you changed; the files
are theirs to commit.

The tool ships no corrections, not even ones true of every program in a language (Rust's
calls by path, React's capitalized elements), and it does not run the fog test for you.
Either would be the tool knowing a codebase's answers before it has asked the questions,
and no one could then trust that every row came from the code and its grammar alone. It
ships the way to look: the map, `lens_status`, and the fog test as a question you ask.

| dial | what it turns | turn it when |
|---|---|---|
| `terrain.toml` `[scope]` | what is read: directories excluded or included, non-source extensions, the size ceiling | `left_out` shows a directory that should be read, or generated or vendored code is being read |
| `terrain.toml` `[languages]`, `[extensions]`, `[shebangs]` | which grammar reads which file | `skipped_or_failed` lists source files with "no language detected", or a file is read by the wrong grammar |
| `terrain.toml` `[queries]` | which grammars' query files run together | a language should run another's queries too |
| `queries/<language>/<kind>.scm` | what tags, locals or highlights mark | the fog test lists names called in a shape not marked, or `grammar` reports a pattern left out or never matched |
| `lenses/<name>.sql` | a question asked often, run by its name | the same question has been asked twice |

## The tables

- `file`: every file listed, with its language, size, hash, and status: PARSED,
  ERRORS_PRESENT, SKIPPED or FAILED, with the reason.
- `node`: every named syntax node: `file, id, last, parent, pos, type, field, line, col,
  end_line, end_col, start_byte, end_byte, text`. Ids are depth first, so a node's
  descendants are the ids from `id` to `last`: expand them with
  `unnest(range(id, last + 1))` and join on equality, never BETWEEN. `text` is set only
  on nodes with no named children. `type` and `field` are each grammar's own words.
- `capture`: everything each grammar's own tags, locals and highlights queries mark, and
  the repository's corrections: `file, query, match, name, node`. Captures of one match
  share `match`.
- `grammar`: which query files ran for each language, and any pattern left out and why.
- `inventory`: what was left out, by directory, and the rule that left it out.
- `map`: what wrote the map: the kernel's version, the language pack's, and the grammar
  collection's.

`lens_status` gives every table and saved query with its columns and whole caveat, and
`checks`: whether the map holds together (every parent, range, capture and leaf where it
should be, and every language whose tags ran marking a definition), each with how many rows
fail it and the first file where one does. A failing check means an answer may be wrong
there: say so. A correction file with a pattern that never matched says so in `grammar`.

## The loop

1. `lens_status` first: whether there is a map, how old it is, what it covers, and
   `first_questions`: three questions about this repository, its SQL written out. Ask one
   as it stands, then change the name. The recipes below cover the rest.
2. No map and nothing planted: the first capture writes one directory, `founderealm/`.
   Ask the user, then `lens_capture` with `user_approved: true`.
3. `lens_query` with one SELECT, or a saved query's name. Each answer names the caveat
   of every table it read; repeat a caveat when it limits what you say.
4. Capture whenever the files may have changed: it is cheap, and it brings the map to now.
   The map is what the files were when it was filled, and every answer says how long ago
   that was.
5. When status points at a dial (above), turn it and capture again.

## Reading an answer

- Calls match by name: a call to `get` is every `get`. Candidates, never proven edges.
- A tags query marks calls, not a function passed or assigned as a value, nor a call
  inside a macro's arguments. Never-called is not unreferenced: an identifier node with
  that text is the mention.
- `highlights` rows say what each node is in one vocabulary across every language
  (comment, string, function, type, ...): ask those rather than a grammar's own node types.
  The names are dotted, general first: `comment.documentation` is a comment, `function.method`
  a function. Ask by prefix, `name = 'comment' OR name LIKE 'comment.%'`, or the specific
  ones are missed.
- Count or GROUP BY before listing: a repository can hold millions of rows.
- Before trusting "nothing calls X" in a language, run the fog test below once. A grammar's
  tags query may not mark every call shape (Rust's own misses `a::b()`), and a missed call
  looks exactly like no call. The glass is wiped per repository, with a correction file.
- A SKIPPED or FAILED file, or a directory left out, was not surveyed. Say it is
  unknown and never fill it in.
- A wrong column comes back with the columns of every table you named. No rows comes back
  with where to look next: a name spelled otherwise, a file not read, a grammar that marks
  it differently.
- The binary answers only through these tools. Run from a shell, the plugin points the
  command back here, where the answer arrives whole and the user sees it.

## Recipes

Change NAME, FILE or WORD and ask as written. Each tags capture is joined to the capture
named `name` in the same (file, query, match), whose node holds the text: a definition's
or call's own node has none, since `node` keeps text on leaves only.

Where NAME is defined:

```sql
SELECT c.name AS kind, n.file, n.line
FROM capture c JOIN node n ON n.id = c.node
JOIN capture m ON m.file = c.file AND m.query = 'tags' AND m.match = c.match AND m.name = 'name'
JOIN node nn ON nn.id = m.node
WHERE c.query = 'tags' AND c.name LIKE 'definition.%' AND nn.text = 'NAME'
```

Every call to NAME, by file:

```sql
SELECT n.file, count(*) AS calls, list(n.line ORDER BY n.line) AS lines
FROM capture c JOIN node n ON n.id = c.node
JOIN capture m ON m.file = c.file AND m.query = 'tags' AND m.match = c.match AND m.name = 'name'
JOIN node nn ON nn.id = m.node
WHERE c.query = 'tags' AND c.name = 'reference.call' AND nn.text = 'NAME'
GROUP BY n.file ORDER BY calls DESC
```

What FILE holds, in order (a grammar may mark one definition two ways, so kinds are joined):

```sql
SELECT nn.text AS name, string_agg(DISTINCT c.name, ', ') AS kinds, n.line, n.end_line
FROM capture c JOIN node n ON n.id = c.node
JOIN capture m ON m.file = c.file AND m.query = 'tags' AND m.match = c.match AND m.name = 'name'
JOIN node nn ON nn.id = m.node
WHERE c.query = 'tags' AND c.name LIKE 'definition.%' AND c.file = 'FILE'
GROUP BY nn.text, n.line, n.end_line ORDER BY n.line
```

What a change to NAME touches: each call, with the innermost definition holding it. Ask
again with each name in `inside` for the next hop.

```sql
WITH t AS (
  SELECT c.name AS kind, nn.text AS name, n.file, n.id, n.last, n.line
  FROM capture c JOIN node n ON n.id = c.node
  JOIN capture m ON m.file = c.file AND m.query = 'tags' AND m.match = c.match AND m.name = 'name'
  JOIN node nn ON nn.id = m.node
  WHERE c.query = 'tags')
SELECT r.file, r.line, arg_max(d.name, d.id) AS inside
FROM t r LEFT JOIN t d ON d.file = r.file AND d.kind LIKE 'definition.%' AND r.id > d.id AND r.id <= d.last
WHERE r.kind = 'reference.call' AND r.name = 'NAME'
GROUP BY r.file, r.line ORDER BY r.file, r.line
```

Dead-code candidates: definitions whose name no other node anywhere holds, so nothing
calls, passes, imports or mentions them, inside a macro or out. What a runner or another
program calls by name (main, tests, handlers) shows here too.

```sql
WITH t AS (
  SELECT nn.text AS name, n.file
  FROM capture c JOIN node n ON n.id = c.node
  JOIN capture m ON m.file = c.file AND m.query = 'tags' AND m.match = c.match AND m.name = 'name'
  JOIN node nn ON nn.id = m.node
  WHERE c.query = 'tags' AND c.name LIKE 'definition.%'),
once AS (SELECT text FROM node WHERE text IN (SELECT name FROM t) GROUP BY text HAVING count(*) = 1)
SELECT file, count(DISTINCT name) AS named_once, list(DISTINCT name) AS names
FROM t WHERE name IN (SELECT text FROM once)
GROUP BY file ORDER BY named_once DESC
```

Who calls whom inside FILE, as a Mermaid diagram, counting only names this repository
defines:

```sql
WITH t AS (
  SELECT c.name AS kind, nn.text AS name, n.file, n.id, n.last
  FROM capture c JOIN node n ON n.id = c.node
  JOIN capture m ON m.file = c.file AND m.query = 'tags' AND m.match = c.match AND m.name = 'name'
  JOIN node nn ON nn.id = m.node
  WHERE c.query = 'tags'),
f AS (SELECT * FROM t WHERE file = 'FILE'),
e AS (
  SELECT r.id, r.name AS callee, arg_max(d.name, d.id) AS caller
  FROM f r JOIN f d ON d.kind LIKE 'definition.%' AND r.id > d.id AND r.id <= d.last
  WHERE r.kind = 'reference.call' AND r.name IN (SELECT name FROM t WHERE kind LIKE 'definition.%')
  GROUP BY r.id, r.name)
SELECT 'graph LR' || chr(10) || string_agg(DISTINCT '  ' || caller || ' --> ' || callee, chr(10)) AS mermaid
FROM e
```

Every line of the docs that mentions WORD:

```sql
SELECT filename, line, text FROM (
  SELECT filename, unnest(string_split(content, chr(10))) AS text,
         unnest(range(1, len(string_split(content, chr(10))) + 1)) AS line
  FROM read_text('**/*.md'))
WHERE text ILIKE '%WORD%'
```

Every mention of NAME, by file: what the tags query cannot see as a call, such as a call
inside a macro's arguments (in Rust, nearly every assertion in a test) or a function passed
as a value. The definition itself is one of the mentions.

```sql
SELECT file, count(*) AS mentions, list(line ORDER BY line) AS lines
FROM node WHERE text = 'NAME'
GROUP BY file ORDER BY mentions DESC
```

The fog test, per language: functions the tags query saw defined whose name is mentioned
elsewhere but never seen called. A few are expected: functions passed as values, called
inside a macro's arguments, or called by a runner. When the list is long, open three of
the names at their mentions: if they are called in a shape the tags query does not mark,
write `founderealm/queries/<language>/tags.scm` for that shape, capture again, and run
this again to see the list shrink. A call counts from any language, so a function defined
in a `.ts` file and called from a `.tsx` one is seen; mentions count only in the language
that defines it, so a same-named word in another language is not one.

```sql
WITH t AS (
  SELECT c.name AS kind, nn.text AS name, f.language
  FROM capture c JOIN file f ON f.path = c.file
  JOIN capture m ON m.file = c.file AND m.query = 'tags' AND m.match = c.match AND m.name = 'name'
  JOIN node nn ON nn.id = m.node
  WHERE c.query = 'tags'),
fns AS (SELECT DISTINCT language, name FROM t WHERE kind IN ('definition.function', 'definition.method')),
seen AS (SELECT DISTINCT name FROM t WHERE kind = 'reference.call'),
mentioned AS (
  SELECT f.language, n.text AS name, count(*) AS n
  FROM node n JOIN file f ON f.path = n.file
  WHERE n.text IN (SELECT name FROM fns) GROUP BY ALL)
SELECT d.language, count(*) AS functions,
       count(*) FILTER (WHERE s.name IS NULL AND m.n > 1) AS mentioned_never_seen_called,
       list(d.name) FILTER (WHERE s.name IS NULL AND m.n > 1) AS names
FROM fns d LEFT JOIN seen s USING (name) LEFT JOIN mentioned m USING (language, name)
GROUP BY d.language ORDER BY mentioned_never_seen_called DESC
```

A name with no rows may be spelled otherwise:

```sql
SELECT text, count(*) AS n FROM node
WHERE text ILIKE '%part%' AND length(text) < 80
GROUP BY text ORDER BY n DESC LIMIT 20
```

## Saved queries

A question this repository asks often becomes `founderealm/lenses/<name>.sql`:
`-- caveat:` lines saying what limits its rows, then one SELECT. It is a view made when a
question is asked, never stored, so it is always as current as the map; one saved query
may read another, and asking its name runs it. The kernel plants none: what a repository
asks is written in that repository, by whoever asks it.

## Files, docs and data

A question can read any file inside the repository, and none outside it, at the moment
it is asked: `read_text('docs/**/*.md')`, `read_csv(...)`, `read_json(...)`. Nothing is
stored. Diffs are git's: git says which lines moved, the map says what they are.

## After an update

An update changes the kernel, not the repository. If `lens_status` shows `kernel` differing
from the kernel in `made_by` (or `made_by` reporting no `map` table), the map was written
before the update: `lens_capture` rebuilds it whole.
`terrain.toml`, `queries/` and `lenses/` are never written over. A saved query listed in
`saved_queries_broken` names a column the new tables do not have: fix that name in its
`.sql` file. A correction reported in `grammar` as left out or never matched was written
against the old grammar's trees: rewrite it against the new ones.

## Steering: terrain.toml and query corrections

`founderealm/terrain.toml` says what is left out (`[scope]`) and which grammar reads what
(`[languages]`, `[extensions]`, `[shebangs]`, `[queries]`). A list in `[scope]` replaces
its default, and a list left out keeps it. `[shebangs]` and `[queries]` add to their
defaults key by key. `[languages]` and `[extensions]` are only what the file says: the
planted file writes the defaults out, so removing one there removes it.

When `grammar` says a query pattern was left out (a predicate not evaluated, or a node
type that grammar never puts in a tree), or a query misses a shape the fog test finds,
write the correction as
`founderealm/queries/<language>/<kind>.scm` (tags, locals or highlights), against the
node shapes that grammar really builds: look at a few `node` rows of that language first.
It is composed after the grammar's own. Capture again after either.
