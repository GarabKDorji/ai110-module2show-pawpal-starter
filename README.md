# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Smarter Scheduling

Phase 3 added four algorithmic improvements to the `Scheduler` class:

### Sort by time
`Scheduler.sort_by_time()` returns the daily plan ordered chronologically.
It uses `sorted()` with a lambda key on each task's `"HH:MM"` `start_time`
field — zero-padded strings compare correctly via lexicographic order, so no
datetime parsing is needed.

### Filter by pet or status
`Scheduler.filter_tasks(pet_name=None, completed=None)` narrows the plan to
tasks matching any combination of pet name (case-insensitive) and completion
status (`True` = done, `False` = pending). Both filters apply together (AND
logic); omitting either one disables that filter.

### Recurring tasks
`Task.mark_completed()` now returns a fresh `Task` for the next occurrence
using Python's `timedelta`:
- `"daily"` → due date + 1 day
- `"weekly"` → due date + 7 days
- any other frequency → `None` (one-off, no follow-up)

`Scheduler.complete_task(pet_name, task_name)` calls `mark_completed()` and
automatically re-adds the next task to the pet, so it appears in future plans
without manual intervention.

### Conflict detection
`Scheduler.detect_conflicts()` compares every unique pair of timed tasks using
`itertools.combinations` and the standard interval-overlap test
(`a_start < b_end and b_start < a_end`). It returns a list of human-readable
warning strings — the program never crashes on a conflict.

---

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.
