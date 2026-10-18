#!/bin/sh
# A Bash command that runs the lens binary is pointed to the lens tools instead, where the
# answer arrives whole and the user sees it. Claude Code passes the tool call as JSON on
# stdin; exit 2 blocks the call and shows the agent door.md.
if grep -Eq '("command":[[:space:]]*"|[;&|(][[:space:]]*)[^[:space:]";&|]*(founderealm-lens|server/lens)([[:space:]")<]|$)'; then
    cat "${CLAUDE_PLUGIN_ROOT}/hooks/door.md" >&2
    exit 2
fi
exit 0
