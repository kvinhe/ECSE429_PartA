# Bug reports – rest api todo list manager 1.5.5

Form: ID | Summary (<=80 chars) | Description | Impact | Steps to reproduce | Pytest pair (expected in `test_bugs_expected_behavior.py`, actual in `test_bugs_actual_behavior.py`).

## BUG-01: Todo->category link is not visible from GET /categories/:id/todos

**Description:** A link made with POST /todos/:id/categories is stored one way only. The category's todos list stays empty.

**Potential impact:** Clients see different data depending on which side they query; category views miss todos.

**Steps to reproduce:**
1. Create todo T and category C
2. POST /todos/T/categories {"id":"C"} -> 201
3. GET /categories/C/todos -> {"todos":[]} (expected T)

**Test:** `test_bugs_expected_behavior.py::test_category_lists_todo_linked_from_todo_side`

## BUG-02: Category->todo link is not visible from GET /todos/:id/categories

**Description:** Mirror of BUG-01: POST /categories/:id/todos is not reflected on the todo.

**Potential impact:** Same inconsistency as BUG-01 in the other direction.

**Steps to reproduce:**
1. Create T and C
2. POST /categories/C/todos {"id":"T"} -> 201
3. GET /todos/T/categories -> empty (expected C)

**Test:** `test_todo_lists_category_linked_from_category_side`

## BUG-03: Project->category link is not visible from GET /categories/:id/projects

**Description:** POST /projects/:id/categories is stored one way only.

**Potential impact:** Category cannot list its projects.

**Steps to reproduce:**
1. Create project P and category C
2. POST /projects/P/categories {"id":"C"} -> 201
3. GET /categories/C/projects -> empty (expected P)

**Test:** `test_category_lists_project_linked_from_project_side`

## BUG-04: GET on relationship of a nonexistent parent returns 200 with other data

**Description:** GET /todos/987654/categories, /projects/987654/tasks and /todos/987654/tasksof return 200 and a list of related objects of OTHER parents.

**Potential impact:** Wrong data returned silently; clients cannot detect a bad id. Possible information leak.

**Steps to reproduce:**
1. Link any todo to a category
2. GET /todos/987654/categories -> 200 containing that category (expected 404)

**Test:** `test_relationship_of_missing_parent_returns_404`

## BUG-05: PUT /todos/:id requires title although docs say 'fields to amend'

**Description:** Swagger describes PUT as amending with the fields in the body; a body without title is rejected with 400.

**Potential impact:** Clients following the docs cannot do partial updates with PUT.

**Steps to reproduce:**
1. Create todo
2. PUT /todos/ID {"description":"only"} -> 400 'title : field is mandatory' (expected 200)

**Test:** `test_put_todo_with_only_description_succeeds`

## BUG-06: doneStatus returned as string but string input is rejected

**Description:** Responses contain "doneStatus":"true" yet sending "true" (string) gives 400 'should be BOOLEAN'; only JSON true works.

**Potential impact:** Round-tripping a GET response into a PUT/POST fails; typing is inconsistent.

**Steps to reproduce:**
1. GET /todos/1 -> doneStatus "false"
2. PUT /todos/1 {"title":"x","doneStatus":"false"} -> 400 (expected 200)

**Test:** `test_returned_done_status_can_be_sent_back`

## BUG-07: Failed (400) creations still consume object ids

**Description:** Each rejected POST /todos advances the id counter, leaving gaps in ids.

**Potential impact:** Id exhaustion/gaps; ids unpredictable; minor information about request volume.

**Steps to reproduce:**
1. Create todo (id N)
2. Send two invalid POSTs (empty title, bad doneStatus)
3. Create todo -> id N+3 (expected N+1)

**Test:** `test_failed_creation_does_not_consume_an_id`

## BUG-08: GET /todos/:id/tasksof/:id returns 404, swagger documents 405

**Description:** Relationship instance URLs accept only DELETE; GET is documented as 405 but returns 404 even when the link exists.

**Potential impact:** Wrong status code; clients cannot distinguish 'unsupported' from 'not found'.

**Steps to reproduce:**
1. Link todo T to project P
2. GET /todos/T/tasksof/P -> 404 (expected 405)

**Test:** `test_get_on_relationship_instance_returns_405`

## BUG-09: PUT /projects/:id silently removes the project's task links

**Description:** Replacing a project with PUT resets omitted fields AND drops all task relationships.

**Potential impact:** Silent data loss of relationships on an ordinary rename.

**Steps to reproduce:**
1. Create project P and link todo T
2. PUT /projects/P {"title":"renamed"} -> 200
3. GET /projects/P/tasks -> empty (T still exists)

**Test:** `test_put_project_keeps_task_relationships`

## BUG-10: Deleting a category leaves a ghost link listed on the todo

**Description:** After DELETE /categories/C, GET /todos/T/categories still returns C with its title; GET /categories/C is 404.

**Potential impact:** Referential integrity broken; deleted data still exposed; clients dereferencing it fail.

**Steps to reproduce:**
1. Link T to C from the todo side
2. DELETE /categories/C -> 200
3. GET /todos/T/categories -> still lists C (expected empty)

**Test:** `test_deleting_category_removes_it_from_todo_categories`

## BUG-11: Deleting a todo leaves a ghost link listed on the category

**Description:** After DELETE /todos/T, GET /categories/C/todos still returns T with full details.

**Potential impact:** Same integrity problem as BUG-10.

**Steps to reproduce:**
1. Link C to T from the category side
2. DELETE /todos/T -> 200
3. GET /categories/C/todos -> still lists T (expected empty)

**Test:** `test_deleting_todo_removes_it_from_category_todos`

## BUG-12: Relationship creation fails when the id is sent as XML

**Description:** POST /todos/:id/categories with <category><id>N</id></category> returns 404 'Could not find thing matching value for id'; JSON works.

**Potential impact:** XML clients cannot create relationships although XML is advertised for all payloads.

**Steps to reproduce:**
1. Create T and C
2. POST /todos/T/categories with Content-Type application/xml body <category><id>C</id></category> -> 404 (expected 201)

**Test:** `test_xml_relationship_creation_succeeds`
