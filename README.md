# ECSE 429 – Part A: Exploratory Testing + Unit Test Suite

**Application under test:** rest api todo list manager v1.5.5
(`java -jar runTodoManagerRestAPI-1.5.5.jar`, http://localhost:4567)

**Team (3 members — scope: todos, projects, categories + interoperability session)**
| Name | Student ID | Email |
|---|---|---|
| Kevin He | 261167637 | kevin.he2@mail.mcgill.ca |
| Nathan Audegond | 261171251 | nathan.audegond@mail.mcgill.ca |
| Eric Deng | 261138815 | eric.deng@mail.mcgill.ca |

**Session participants (as recorded in session_notes/)**
- Charter I – Todos (CH1): Kevin He + Eric Deng
- Charter II – Projects (CH2): Nathan Audegond + Kevin He
- Charter III – Categories (CH3): Eric Deng + Nathan Audegond
- Charter IV – Interoperability (CH4): Kevin He + Nathan Audegond + Eric Deng

**Repo:** https://github.com/kvinhe/ECSE429_PartA

## Contents
- `Part_A_Report.pdf` — written report (6 pages)
- `session_notes/` — one PDF per charter (4 charters × 45 min), named
  `CH1_Todos_Notes.pdf`, `CH2_Projects_Notes.pdf`, `CH3_Categories_Notes.pdf`,
  `CH4_Interoperability_Notes.pdf`. Each PDF follows the same section structure:
  Session Participants; Section 1 Session Summary (1.1 charter, 1.2 version,
  1.3 set up, 1.4 build); Section 2 Session Notes (date/time, colour legend
  As Expected / Bug / To Explore, and the exploration table
  Time | Endpoint Tested | Response | Reference File) covering every call
  in the session — 66 calls in total, each with its documented status,
  expected behaviour, observed response and verdict folded into the table;
  Section 3 Referenced Files; Section 4 Summary of Session Findings
  (4.1 findings + bug table, 4.2 concerns / areas of potential risk,
  4.3 new testing ideas).
- `PartA_UnitTests_Video.mp4` — screen recording of the full suite: default
  order, seeds 7 and 31337, and a service-down run (recorded on macOS)
- `bug_reports.md` — bug form + 12 bug reports (BUG-01 … BUG-12)
- `tests/` — pytest unit test suite (12 modules, 185 tests)
- `exploratory/` — curl capability scripts for the 4 sessions (+ `common.sh`)
- `logs/` — exploratory session logs and unit test run logs
  (default order, 3 seeded random orders, service-down run, raw bug failures)

## Charter evidence map
Files for each charter:

| Charter | Session notes | Capability script | Evidence log | Main follow-up tests |
|---|---|---|---|---|
| CH1 – Todos | `session_notes/CH1_Todos_Notes.pdf` | `exploratory/session1_todos.sh` | `logs/exploratory_session1_todos.log` | `tests/test_todos_api.py`, `tests/test_todo_relationships_api.py`, `tests/test_payload_formats_api.py` |
| CH2 – Projects | `session_notes/CH2_Projects_Notes.pdf` | `exploratory/session2_projects.sh` | `logs/exploratory_session2_projects.log` | `tests/test_projects_api.py`, `tests/test_project_relationships_api.py` |
| CH3 – Categories | `session_notes/CH3_Categories_Notes.pdf` | `exploratory/session3_categories.sh` | `logs/exploratory_session3_categories.log` | `tests/test_categories_api.py`, `tests/test_category_relationships_api.py` |
| CH4 – Interoperability | `session_notes/CH4_Interoperability_Notes.pdf` | `exploratory/session4_interoperability.sh` | `logs/exploratory_session4_interoperability.log` | `tests/test_interoperability_api.py` |

Each log records the status and response body of every request, in run
order. Bug follow-ups for every charter live in `tests/test_bugs_expected_behavior.py` and
`tests/test_bugs_actual_behavior.py`, cross-referenced from `bug_reports.md`.

## Run
1. Start a fresh app: `java -jar runTodoManagerRestAPI-1.5.5.jar`
2. `pip install -r tests/requirements.txt`
3. From this folder:
   - `python -m pytest tests` — default order
   - `python -m pytest tests --random-seed 7` — pseudo-random order (seed printed)
   - `python -m pytest tests --runxfail -k expected` — raw failures of the bug checks
4. Exploratory scripts: `bash exploratory/session1_todos.sh` (… 2, 3, 4)

Set `TODO_API_URL` to test another host/port.

**Expected result:** 171 passed, 14 xfailed
(14 expected-behaviour checks covering 12 distinct bugs; verified 2026-10-14
against a fresh server in default order and with seeds 7, 31337 and 20261014).
