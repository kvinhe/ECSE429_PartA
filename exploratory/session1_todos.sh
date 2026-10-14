#!/bin/bash
# Session 1 - todos. Charter: identify capabilities and instabilities of /todos.
source "$(dirname "$0")/common.sh"
call GET /todos
call POST /todos -H "$JSON" -d '{"title":"buy milk"}'
call POST /todos -H "$JSON" -d '{"title":"full","doneStatus":true,"description":"all fields"}'
call POST /todos -H "$JSON" -d '{}'
call POST /todos -H "$JSON" -d '{"title":"x","doneStatus":"maybe"}'
call POST /todos -H "$JSON" -d '{"title":"x","id":99}'
call POST /todos -H "$JSON" -d '{"title":"x","colour":"red"}'
call POST /todos -H "$JSON" -d '{bad json'
call POST /todos -H "$XML" -H 'Accept: application/xml' -d '<todo><title>from xml</title></todo>'
call POST /todos -H "$XML" -d '<todo><title>broken</todo>'
call GET /todos/1 -H 'Accept: application/xml'
call PUT /todos/1 -H "$JSON" -d '{"description":"only description"}'      # BUG-05
call PUT /todos/1 -H "$JSON" -d '{"title":"scan paperwork","doneStatus":false}'
call POST /todos/1 -H "$JSON" -d '{"description":"amended"}'
call POST /todos/1 -H "$JSON" -d '{"description":""}'
call GET '/todos?doneStatus=false'
call GET '/todos?nofield=1'                                              # silently ignored
call GET /todos/987654
call DELETE /todos/987654
call PATCH /todos/1
call HEAD /todos -I
call OPTIONS /todos -i
