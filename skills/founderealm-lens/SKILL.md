---
name: founderealm-lens
description: >
  The repository as one SQL database, any language. Use before grep: definitions, calls,
  what a change touches, folders, docs, diagrams. How to call it, how to steer it, and a
  menu of questions for lens_query.
---

# Founderealm Lens

## What it is

The repository you are in, as one DuckDB database: the map. One capture reads every file
with tree-sitter; every question after that is one SELECT. It reads source and never runs
it, and it writes nothing but its own `founderealm/` directory.

The map is shaped like the repository: one tree numbered in one sequence, the root
folder, each folder, each file in its folder, each file's syntax nodes. Whatever is inside
a folder, a file, a function or a doc section is the ids from its `id` to its `last`.

## Calling it

- `lens_status`: start here. Whether there is a map and how old it is, what it covers,
  the checks that it holds together, every table with its columns and caveat, and three
  questions about this repository, ready to ask.
- `lens_query`: one SELECT, or a saved query's name. Every answer names the caveat of each
  table it read; repeat a caveat when it limits what you say. A failing check in status
  means an answer may be wrong there: say so.
- `lens_capture`: rebuild the map, whole, in seconds. Capture whenever the files may have
  changed. The first capture writes `founderealm/`: ask the user, then pass
  `user_approved: true`.

## Updating and steering it

Capture brings the map to now. After a kernel update, `lens_status` shows `kernel` beside
`made_by`, what wrote the map: when they differ, capture again.

The kernel ships defaults, never a repository's answers. Where it doesn't fit the
repository you are in, turn a dial in `founderealm/`, capture, and watch status move.
Those files are the repository's: tell the user what you changed.

| dial | what it turns | turn it when |
|---|---|---|
| `terrain.toml` `[scope]` | what is read: directories excluded or included, non-source extensions, the size ceiling | `left_out` misses a directory, or generated or vendored code is read |
| `terrain.toml` `[languages]`, `[extensions]`, `[shebangs]` | which grammar reads which file | `skipped_or_failed` says "no language detected", or a file is read by the wrong grammar |
| `terrain.toml` `[queries]` | which grammars' query files run together | a language should run another's queries too |
| `terrain.toml` `[text]` `catalog`, `titles` | which languages are docs, catalogued rather than copied, and what marks a title | a doc language is copied whole, or a data language is catalogued |
| `terrain.toml` `[text]` `code`, `code_span`, `min_term` | what marks code in a doc for `term`, and the shortest name kept | the docs mark code another way, or `term` holds noise |
| `queries/<language>/<kind>.scm` | adds to what a grammar's tags, locals or highlights query marks | the fog test names a call shape not marked, or `grammar` reports a pattern left out or never matched |
| `lenses/<name>.sql` | a question asked by name: `-- caveat:` lines, then one SELECT | the same question has been asked twice |

A list in `[scope]` or `[text]` replaces its default, and one left out keeps it. Write a
query correction against the node shapes the grammar really builds: look at a few `node`
rows of that language first.

## The map

| table | one row for each |
|---|---|
| `folder` | folder: `path` (`''` is the root, every other ends in `/`), `id, last, parent, sha256`. The hash covers every name and kind under it, the contents of every parsed file and the size of every other |
| `file` | listed file: `path, id, last, parent, kind, language, catalog, bytes, sha256, status, reason` |
| `node` | named syntax node: `file, id, last, parent, type, line, end_line, start_byte, end_byte, text`. Text is kept on leaves only, and in a doc only in its titles |
| `capture` | thing a grammar's tags, locals or highlights query marks: `file, query, match, name, node` |
| `tag` | a view: tags capture with the name it marks, `kind, name, file, line, end_line, id, last`. Most code questions start here |
| `card` | doc book or section: `id, last, file, kind, title, path, line, end_line, start_byte, end_byte` |
| `term` | name the code defines that a doc marks as code: `term, card, line` |
| `grammar` | language: which query files ran, and patterns left out and why |
| `inventory` | directory left out, and the rule that left it out |
| `map` | what wrote the map: the kernel, the language pack and the grammar collection |

## Reading an answer

- Calls match by name: a call to `get` is every `get`. Candidates, never proven edges.
- Count definitions by `id`, never by row: a grammar may mark one definition two ways.
- A tags query marks calls, not a function passed as a value or called inside a macro's
  arguments. Every mention of a name (below) finds those.
- Ask what is inside something by its `id`..`last` range, never by `LIKE` on a path.
- A SKIPPED or FAILED file, or a directory left out, was not read: say it is unknown.
- A doc's words are never stored: DuckDB reads the file when asked (`read_text`,
  `read_blob`), and `true_to_the_map` says whether it is still the file captured.
- Count or GROUP BY before listing: a repository can hold millions of rows.
- No rows comes back with where to look next.

## Menu

Change the CAPITALS and ask as written. FOLDER ends in `/`; PLACE is a folder or a file.

### Code

Where NAME is defined:

```sql
SELECT kind, file, line FROM tag WHERE kind LIKE 'definition.%' AND name = 'NAME'
```

Every call to NAME, by file:

```sql
SELECT file, count(*) AS calls, list(line ORDER BY line) AS lines
FROM tag WHERE kind = 'reference.call' AND name = 'NAME'
GROUP BY file ORDER BY calls DESC
```

What FILE holds, in order:

```sql
SELECT name, string_agg(DISTINCT kind, ', ') AS kinds, line, end_line
FROM tag WHERE kind LIKE 'definition.%' AND file = 'FILE'
GROUP BY name, line, end_line ORDER BY line
```

What a change to NAME touches: each call with its folder and the definition holding it.
Ask again with each name in `inside` for the next hop.

```sql
SELECT p.path AS folder, r.file, r.line, arg_max(d.name, d.id) AS inside
FROM tag r JOIN file f ON f.path = r.file JOIN folder p ON p.id = f.parent
LEFT JOIN tag d ON d.file = r.file AND d.kind LIKE 'definition.%' AND r.id > d.id AND r.id <= d.last
WHERE r.kind = 'reference.call' AND r.name = 'NAME'
GROUP BY p.path, r.file, r.line ORDER BY r.file, r.line
```

Every mention of NAME, the definition and the calls a tags query can't see included:

```sql
SELECT file, count(*) AS mentions, list(line ORDER BY line) AS lines
FROM node WHERE text = 'NAME' GROUP BY file ORDER BY mentions DESC
```

Dead-code candidates: definitions whose name no other node holds. What a runner calls by
name (main, tests, handlers) shows here too.

```sql
WITH d AS (SELECT name, file FROM tag WHERE kind LIKE 'definition.%'),
once AS (SELECT text FROM node WHERE text IN (SELECT name FROM d) GROUP BY text HAVING count(*) = 1)
SELECT file, count(DISTINCT name) AS named_once, list(DISTINCT name) AS names
FROM d WHERE name IN (SELECT text FROM once)
GROUP BY file ORDER BY named_once DESC
```

A name with no rows, spelled otherwise:

```sql
SELECT text, count(*) AS n FROM node
WHERE text ILIKE '%PART%' AND length(text) < 80
GROUP BY text ORDER BY n DESC LIMIT 20
```

### Folders

Everything inside FOLDER, file by file, at any depth:

```sql
SELECT f.path, f.kind, f.status,
       count(DISTINCT t.id) FILTER (WHERE t.kind LIKE 'definition.%') AS definitions,
       count(DISTINCT t.id) FILTER (WHERE t.kind = 'reference.call') AS calls
FROM folder d JOIN file f ON f.id BETWEEN d.id AND d.last
LEFT JOIN tag t ON t.file = f.path
WHERE d.path = 'FOLDER'
GROUP BY f.path, f.kind, f.status ORDER BY f.path
```

Where FOLDER reaches: the folders outside it that define a name it calls. By name, so the
more folders one name reaches, the less any one of them is the one.

```sql
WITH t AS (SELECT t.kind, t.name, t.id, f.parent AS folder FROM tag t JOIN file f ON f.path = t.file),
def AS (SELECT DISTINCT name, id, folder FROM t WHERE kind LIKE 'definition.%'),
here AS (SELECT id, last FROM folder WHERE path = 'FOLDER')
SELECT p.path AS reaches, count(DISTINCT r.id) AS calls, list(DISTINCT r.name) AS names
FROM here, t r JOIN def d ON d.name = r.name JOIN folder p ON p.id = d.folder
WHERE r.kind = 'reference.call' AND r.id BETWEEN here.id AND here.last
  AND NOT d.id BETWEEN here.id AND here.last
GROUP BY p.path ORDER BY calls DESC
```

Who calls whom inside PLACE, as a Mermaid diagram: a box for each folder and file, an
arrow for each call to a name defined once inside PLACE. A name defined twice draws none.

```sql
WITH here AS (SELECT id, last FROM folder WHERE path = 'PLACE' UNION ALL SELECT id, last FROM file WHERE path = 'PLACE'),
t AS (SELECT t.kind, t.name, t.id, t.last FROM here, tag t WHERE t.id BETWEEN here.id AND here.last),
def AS (SELECT DISTINCT name, id, last FROM t WHERE kind LIKE 'definition.%'),
once AS (SELECT name, any_value(id) AS id FROM def GROUP BY name HAVING count(*) = 1),
call AS (SELECT r.name, max(d.id) AS caller FROM t r JOIN def d ON r.id > d.id AND r.id <= d.last
         WHERE r.kind = 'reference.call' GROUP BY r.id, r.name),
edge AS (SELECT c.caller, o.id AS callee, count(*) AS n FROM call c JOIN once o ON o.name = c.name
         WHERE c.caller <> o.id GROUP BY ALL),
used AS (SELECT caller AS id FROM edge UNION SELECT callee FROM edge),
box AS (
  SELECT f.id, f.last, 'subgraph d' || f.id || '["' || regexp_extract(f.path, '([^/]+/)$', 1) || '"]' AS open
  FROM here, folder f WHERE f.id BETWEEN here.id AND here.last
    AND EXISTS (SELECT 1 FROM used u WHERE u.id BETWEEN f.id AND f.last)
  UNION ALL
  SELECT f.id, f.last, 'subgraph f' || f.id || '["' || regexp_extract(f.path, '[^/]+$') || '"]'
  FROM here, file f WHERE f.id BETWEEN here.id AND here.last
    AND EXISTS (SELECT 1 FROM used u WHERE u.id BETWEEN f.id AND f.last)),
lines(pos, tie, line) AS (
  SELECT -1, 0, 'graph LR'
  UNION ALL SELECT id, 0, open FROM box
  UNION ALL SELECT last + 0.5, -id, 'end' FROM box
  UNION ALL SELECT d.id, 0, 'n' || d.id || '["' || d.name || '"]' FROM def d JOIN used u ON u.id = d.id
  UNION ALL SELECT 1e15, caller * 1e7 + callee, 'n' || caller || ' -->|' || n || '| n' || callee FROM edge)
SELECT string_agg(line, chr(10) ORDER BY pos, tie) AS mermaid FROM lines
```

Folders that look the same: the same names, parsed contents and sizes under them. An
unparsed file (an image, a binary) matches by size, not bytes: read it before calling it a
copy.

```sql
SELECT sha256, count(*) AS copies, list(path ORDER BY path) AS folders
FROM folder GROUP BY sha256 HAVING count(*) > 1 ORDER BY copies DESC
```

### Docs

The docs are read from their files when asked: name them in the glob, `'**/*.md'`, plus
`'**/*.mdx'` where terrain.toml reads MDX as Markdown.

Where the docs talk about WORD, by line and section:

```sql
WITH lines AS (
  SELECT regexp_replace(filename, '^\./', '') AS file, sha256(content) AS sha,
         unnest(string_split(content, chr(10))) AS text,
         unnest(range(1, len(string_split(content, chr(10))) + 1)) AS line
  FROM read_text('**/*.md'))
SELECT l.file, l.line, arg_max(c.path, c.id) AS section,
       any_value(l.sha) = f.sha256 AS true_to_the_map, l.text
FROM lines l JOIN file f ON f.path = l.file AND f.catalog
JOIN card c ON c.file = l.file AND l.line BETWEEN c.line AND c.end_line
WHERE l.text ILIKE '%WORD%'
GROUP BY l.file, l.line, l.text, f.sha256 ORDER BY l.file, l.line
```

The sections whose own lines hold both WORD1 and WORD2, the tightest first:

```sql
WITH lines AS (
  SELECT regexp_replace(filename, '^\./', '') AS file,
         unnest(string_split(content, chr(10))) AS text,
         unnest(range(1, len(string_split(content, chr(10))) + 1)) AS line
  FROM read_text('**/*.md')),
placed AS (
  SELECT l.text, max(c.id) AS card
  FROM lines l JOIN card c ON c.file = l.file AND l.line BETWEEN c.line AND c.end_line
  GROUP BY l.file, l.line, l.text)
SELECT c.file, c.path, c.line, c.end_line
FROM placed p JOIN card c ON c.id = p.card
GROUP BY c.id, c.file, c.path, c.line, c.end_line
HAVING bool_or(p.text ILIKE '%WORD1%') AND bool_or(p.text ILIKE '%WORD2%')
ORDER BY c.end_line - c.line
```

Every book, the biggest first, with how many sections it holds:

```sql
SELECT f.path, f.bytes, count(c.id) FILTER (WHERE c.kind = 'section') AS sections
FROM file f LEFT JOIN card c ON c.file = f.path
WHERE f.catalog GROUP BY f.path, f.bytes ORDER BY f.bytes DESC
```

A book's table of contents:

```sql
SELECT path, line, end_line FROM card WHERE file = 'FILE' AND kind = 'section' ORDER BY id
```

The same title in more than one book: where the docs cover one subject twice, the first
place to look when docs are consolidated.

```sql
SELECT lower(title) AS title, count(DISTINCT file) AS books,
       (list(DISTINCT file || ':' || line))[1:10] AS first_10
FROM card WHERE kind = 'section'
GROUP BY lower(title) HAVING count(DISTINCT file) > 1 ORDER BY books DESC, title
```

A section read whole from its book. The same slice reads any node of any file:

```sql
SELECT c.file, c.path, c.line, c.end_line, sha256(b.content) = f.sha256 AS true_to_the_map,
       decode(b.content[c.start_byte + 1:c.end_byte]) AS words
FROM card c JOIN file f ON f.path = c.file
JOIN read_blob('**/*.md') b ON regexp_replace(b.filename, '^\./', '') = c.file
WHERE c.path = 'TITLE › PATH'
```

Where the docs name NAME as code:

```sql
SELECT c.file, t.line, c.path
FROM term t JOIN card c ON c.id = t.card
WHERE t.term = 'NAME' ORDER BY c.file, t.line
```

The code a section names, it and every section under it, with where each name is defined:

```sql
WITH d AS (SELECT name, kind, file, line FROM tag WHERE kind LIKE 'definition.%')
SELECT t.term, d.kind, d.file, d.line
FROM card s JOIN card c ON c.file = s.file AND c.id BETWEEN s.id AND s.last
JOIN term t ON t.card = c.id JOIN d ON d.name = t.term
WHERE s.path = 'TITLE › PATH' GROUP BY ALL ORDER BY t.term
```

Comments and docstrings are code: they stay in `node`, whole up to the leaf text limit,
and the highlights query marks a comment `comment`.

### Checking the lens

The fog test, per language: functions defined, mentioned, but never seen called. A few
are expected (functions passed as values, called in a macro, called by a runner). When the
list is long, open three at their mentions: a call shape the tags query misses gets a
correction in `queries/<language>/tags.scm`, then capture and run this again.

```sql
WITH t AS (SELECT t.kind, t.name, f.language FROM tag t JOIN file f ON f.path = t.file),
fns AS (SELECT DISTINCT language, name FROM t WHERE kind IN ('definition.function', 'definition.method')),
seen AS (SELECT DISTINCT name FROM t WHERE kind = 'reference.call'),
mentioned AS (
  SELECT f.language, n.text AS name, count(*) AS n
  FROM node n JOIN file f ON f.path = n.file
  WHERE n.text IN (SELECT name FROM fns) GROUP BY ALL)
SELECT d.language, count(*) AS functions,
       count(*) FILTER (WHERE s.name IS NULL AND m.n > 1) AS mentioned_never_seen_called,
       (list(d.name ORDER BY d.name) FILTER (WHERE s.name IS NULL AND m.n > 1))[1:20] AS first_20
FROM fns d LEFT JOIN seen s USING (name) LEFT JOIN mentioned m USING (language, name)
GROUP BY d.language ORDER BY mentioned_never_seen_called DESC
```

What each language's query files did, and what was left out:

```sql
SELECT language, files, tags, locals, highlights FROM grammar ORDER BY files DESC
```
