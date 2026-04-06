# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

The initial UML had four classes with clear, separated responsibilities:

- **Owner** — stores the person's name, daily available time, and care preferences. Acts as the entry point to all pets and tasks.
- **Pet** — holds profile data (name, species, age, notes) and owns a list of `Task` objects. Responsible for adding and removing tasks from its own list.
- **Task** — represents a single care activity. Stores category, duration, frequency, priority flag, and completion status.
- **Scheduler** — the core logic class. Takes an `Owner` as input and is responsible for generating a care plan, fitting tasks within the available time budget, and explaining the result.

Relationships in the initial design:
- An `Owner` owns one or more `Pet` objects
- A `Pet` holds zero or more `Task` objects
- An `Owner` uses one `Scheduler`
- A `Scheduler` reads tasks from the `Owner`'s pets to build its plan

**b. Design changes**

Yes — three meaningful changes happened during implementation:

1. **`Task` gained `start_time` and `due_date` fields.** The initial design stored only duration and frequency. Once sorting was added, tasks needed an explicit `"HH:MM"` start time. `due_date` was added when recurring task logic required knowing what day to base the next occurrence on.

2. **`Task.mark_completed()` changed from a simple setter to a factory method.** Originally it just set `self.completed = True`. After adding recurrence logic, it now returns a new `Task` object with the next due date calculated via `timedelta`. This turned a one-line method into the most important method in the class.

3. **`Scheduler` grew from 3 methods to 8.** The initial design only had `generate_plan()`, `add_task()`, and `remove_task()`. Phase 3 added `complete_task()`, `detect_conflicts()`, `sort_by_time()`, `filter_tasks()`, and `explain_plan()` — reflecting the shift from a basic plan generator to a full scheduling assistant.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers three constraints:

1. **Time budget** — the owner's `available_time` in minutes. Tasks that push the total over budget are dropped entirely. This is the hardest constraint — the plan must fit.
2. **Priority** — required tasks are always scheduled before optional ones, regardless of the order they were added. This ensures feeding and medication are never skipped to make room for grooming.
3. **Frequency** — tasks are tagged as `"daily"` or `"weekly"`. The `due_date` field tracks when each task is next due, and `mark_completed()` uses `timedelta` to calculate the following occurrence automatically.

Time was treated as the most important constraint because a plan that exceeds the owner's available time is useless. Priority was second because a pet's required health tasks matter more than optional comfort tasks.

**b. Tradeoffs**

**Tradeoff: O(n²) conflict detection vs. a sorted sweep**

`detect_conflicts()` compares every pair of scheduled tasks using
`itertools.combinations`, which is O(n²). A more efficient approach would be
to sort tasks by `start_time` first and then do a single linear sweep,
checking each task only against the one directly before it — O(n log n) total.

The O(n²) approach was kept because:

1. **Scale doesn't justify the complexity.** A typical pet owner schedules fewer than 20 tasks per day. At that size the two approaches are indistinguishable in speed, and the combinations loop is easier to read and verify at a glance.

2. **The linear sweep only catches adjacent conflicts.** If three tasks overlap (A overlaps B, B overlaps C, A overlaps C), a naive sweep can miss the A–C pair. The pairwise approach catches all combinations correctly without extra bookkeeping.

3. **Readability over micro-optimization.** For a scheduling assistant used by a single owner, correctness and clarity matter more than shaving microseconds. If the task list ever grew large (e.g., a pet hotel managing hundreds of animals), switching to a sorted sweep or an interval tree would be the right call.

---

## 3. AI Collaboration

**a. How you used AI**

AI was used at every phase of the project, but in different ways depending on the task:

- **Design brainstorming (Phase 1):** Used Copilot Chat with `#codebase` to identify which scheduling behaviors were most important to test and which edge cases a pet owner scheduler would realistically face (zero available time, no tasks, duplicate times).
- **Algorithm implementation (Phase 3):** Used Agent Mode to implement `sort_by_time()`, `filter_tasks()`, `detect_conflicts()`, and the recurrence logic. The most useful prompt pattern was describing the exact behavior wanted ("sort HH:MM strings without datetime parsing") rather than asking for generic help.
- **Refactoring (Step 5):** Used Inline Chat on `detect_conflicts()` to ask how to simplify the nested `for i / for j` index loop. The suggestion to use `itertools.combinations` was correct and made the intent of the code immediately clear.
- **Documentation:** Used the Generate Documentation smart action to upgrade informal inline comments to proper Google-style docstrings with `Args:` and `Returns:` sections.

The most helpful prompt pattern was combining a specific method name with the exact behavior: *"how could `detect_conflicts()` be simplified for readability without changing its correctness?"* Generic prompts like *"improve my code"* produced unfocused suggestions.

**b. Judgment and verification**

When asked to simplify `detect_conflicts()`, Copilot initially suggested replacing the loop with a single-pass sweep that only compared each task against the next one in sorted order. That approach is more efficient but has a correctness flaw: it misses non-adjacent conflicts when three or more tasks overlap in different combinations.

The suggestion was rejected and the `itertools.combinations` approach was kept instead — it's still more readable than the original `for i / for j` loop, but it checks every unique pair rather than just neighbors. The decision was verified by writing a test case with three overlapping tasks and confirming that all three conflict pairs were detected.

**Which Copilot features were most effective:**
- **Agent Mode** was the most powerful — it could read the full codebase, understand how `Task`, `Pet`, `Owner`, and `Scheduler` related to each other, and implement a complete method that fit the existing design without being told about every attribute.
- **Inline Chat** was best for focused, single-method improvements where the surrounding context mattered (e.g., "why does this sort place None values at the end?").
- **Separate chat sessions for different phases** prevented context bleed — the testing session didn't mix up implementation details with test strategy, and the refactoring session focused only on the algorithm without re-litigating earlier design decisions.

**How separate chat sessions helped:**
Opening a new session at the start of each phase meant each conversation had a clear goal. The testing session focused entirely on edge cases without drifting into UI work. The refactoring session was scoped to one method. When context was kept narrow, AI suggestions were more precise and required less filtering.

---

## 4. Testing and Verification

**a. What you tested**

The 17-test suite covered five areas:

1. **Sorting correctness** — tasks added in scrambled order (`14:00`, `07:30`, `08:00`) must come back sorted chronologically; tasks with no `start_time` must sort to the end.
2. **Recurrence logic** — daily tasks must return a new task due `today + 1 day`; weekly tasks due `today + 7 days`; one-off frequencies must return `None`.
3. **Conflict detection** — same-pet overlaps, cross-pet overlaps, and tasks with no `start_time` (which should never trigger a false positive).
4. **Plan generation** — required tasks must appear before optional; no tasks should be scheduled when available time is 0.
5. **Filtering** — case-insensitive pet name filter; `completed=True` returns only done tasks.

These behaviors were prioritized because they represent the core value of the app. A scheduler that sorts incorrectly or misses a conflict is worse than no scheduler — it gives the owner false confidence.

**b. Confidence**

★★★★☆ (4/5)

The backend logic is fully verified. One star is held back for two reasons:
- Tasks without a `start_time` are silently skipped by `detect_conflicts()` rather than flagged to the user.
- There are no tests for the Streamlit UI layer in `app.py` — session state behavior, button interactions, and form validation are untested.

If given more time, the next tests would cover: completing a task twice (should only create one follow-up), adding 0-duration tasks, and verifying that the filter returns an empty list gracefully rather than crashing when no tasks match.

---

## 5. Reflection

**a. What went well**

The separation of concerns between `Task`, `Pet`, `Owner`, and `Scheduler` held up well throughout every phase. Because each class had a single, clear responsibility, adding new features in Phase 3 never required rewriting existing methods — it only required adding new ones. The recurrence logic, for example, fit entirely inside `Task.mark_completed()` without touching any other class.

**b. What you would improve**

If given another iteration, the `Scheduler` would be redesigned to filter tasks by `due_date` before building the daily plan. Right now it includes all tasks regardless of when they're due — a task created for next week still appears in today's plan. Adding a `today_only=True` flag to `generate_plan()` would make the schedule more realistic.

The Streamlit UI would also be extended to let the owner mark tasks complete directly from the app, so the recurrence logic actually runs during a live session rather than only through `main.py`.

**c. Key takeaway**

The most important lesson was that **AI tools amplify the quality of your design decisions — they don't replace them**. When the class structure was clear and each method had a single responsibility, AI could implement new features quickly and correctly. When a prompt was vague or the design was unclear, AI suggestions required significant filtering and correction. Being the "lead architect" meant making the hard structural decisions first — what belongs in `Task` vs. `Scheduler`, when to add a field vs. a method — and then using AI to execute those decisions efficiently. The AI never decided what the system should do; it only helped build what had already been designed.
