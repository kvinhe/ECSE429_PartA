#!/bin/bash
# Session 4 - interoperability. Charter: identify capabilities and instabilities when
# todos, projects and categories are combined; look for orphaned / ghost relationships.
source "$(dirname "$0")/common.sh"
T=$(curl -s -X POST $BASE/todos -H "$JSON" -d '{"title":"interop todo"}' | python3 -c 'import sys,json;print(json.load(sys.stdin)["id"])')
P=$(curl -s -X POST $BASE/projects -H "$JSON" -d '{"title":"interop project"}' | python3 -c 'import sys,json;print(json.load(sys.stdin)["id"])')
C=$(curl -s -X POST $BASE/categories -H "$JSON" -d '{"title":"interop category"}' | python3 -c 'import sys,json;print(json.load(sys.stdin)["id"])')
echo "created todo=$T project=$P category=$C"
call POST /projects/$P/tasks -H "$JSON" -d "{\"id\":\"$T\"}"
call GET /todos/$T/tasksof                       # project<->todo link is two-way
call POST /todos/$T/categories -H "$JSON" -d "{\"id\":\"$C\"}"
call GET /categories/$C/todos                    # BUG-01: empty
call POST /todos/$T/categories -d "<category><id>$C</id></category>" -H "$XML"   # BUG-12
call DELETE /categories/$C
call GET /todos/$T/categories                    # BUG-10: ghost category still listed
call DELETE /todos/$T
call DELETE /projects/$P
