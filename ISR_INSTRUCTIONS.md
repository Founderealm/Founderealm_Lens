# ISR

This repository carries a map of itself. Read the map before reading source
broadly. Source is the final authority; the map is how you find the right
source fast.

    ./capture    rebuild the map. Seconds. Run it when code changed.
    ./search     ask it something. Start with `./search views`.
    ./verify     check the instrument itself, not your code.

## Reading an answer

Every table carries a CAVEAT and it prints with the rows. Read it. Call sites
resolve by NAME, so they are candidates and not proven edges. A null means
never measured, not zero.

ABSENT, BLOCKED and ORPHANED are answers, not errors. They mean nobody
surveyed that ground. Report them as unknown. Do not fill them in.

Use grep when the map says it does not know. That is what the map is for.

## The lenses are examples

`isr/lenses/` holds eight small scripts. They are a demonstration of what is
possible, not a fixed set and not a framework.

Write your own. Copy `NEW_LENS.py.example`, declare its `LENS` contract, write
the JSON it promises. `./capture` finds it by reading that declaration. There
is no registry to edit.

Delete the ones you do not want. `./capture` notices: it names the artifacts
nothing produces any more, and it blocks and names any lens whose input is
gone rather than failing on it.

Never hand-edit an artifact. Fix the lens, then capture again.
