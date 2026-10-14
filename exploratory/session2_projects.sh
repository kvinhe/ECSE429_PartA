#!/bin/bash
# Session 2 - projects. Charter: identify capabilities and instabilities of /projects.
source "$(dirname "$0")/common.sh"
call GET /projects
call POST /projects -H "$JSON" -d '{"title":"thesis"}'
call POST /projects -H "$JSON" -d '{"title":"launch","completed":true,"active":true,"description":"q4"}'
call POST /projects -H "$JSON" -d '{"description":"no title"}'
call POST /projects -H "$JSON" -d '{"title":"x","completed":"yes"}'
call GET /projects/1
call POST /projects/1 -H "$JSON" -d '{"active":true}'
call PUT /projects/1 -H "$JSON" -d '{"title":"Office Work"}'              # BUG-09: relationships dropped?
call GET /projects/1/tasks
call POST /projects/1/tasks -H "$JSON" -d '{"title":"todo created under project"}'
call POST /projects/1/tasks -H "$JSON" -d '{"id":"1"}'
call POST /projects/1/tasks -H "$JSON" -d '{"id":"987654"}'
call GET /projects/987654/tasks                                          # BUG-04
call DELETE /projects/1/tasks/1
call DELETE /projects/1/tasks/1
call GET /projects/1/tasks/1
call DELETE /projects/987654
call GET '/projects?title=thesis'
