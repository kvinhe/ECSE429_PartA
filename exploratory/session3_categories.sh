#!/bin/bash
# Session 3 - categories. Charter: identify capabilities and instabilities of /categories.
source "$(dirname "$0")/common.sh"
call GET /categories
call POST /categories -H "$JSON" -d '{"title":"errands","description":"outside"}'
call POST /categories -H "$JSON" -d '{"description":"no title"}'
call POST /categories -H "$JSON" -d '{"title":""}'
call POST /categories/1 -H "$JSON" -d '{"description":"amended"}'
call PUT /categories/1 -H "$JSON" -d '{"title":"Office"}'
call GET /categories/1/todos
call POST /categories/1/todos -H "$JSON" -d '{"id":"2"}'
call GET /categories/1/todos
call GET /todos/2/categories                                            # BUG-02: one-way link
call POST /categories/1/projects -H "$JSON" -d '{"id":"1"}'
call GET /categories/1/projects
call GET /projects/1/categories                                         # BUG-03 (mirror)
call DELETE /categories/1/todos/2
call DELETE /categories/1/todos/2
call GET /categories/987654
