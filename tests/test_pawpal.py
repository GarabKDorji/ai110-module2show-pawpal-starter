# tests/test_pawpal.py

import sys
import os
from datetime import date, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pawpal_system import Task, Pet, Owner, Scheduler


# ── Helpers ───────────────────────────────────────────────────────────────────

def make_scheduler(available_time=120):
    """Return a fresh Owner + Scheduler with one pet (Buddy) registered."""
    owner = Owner(name="Alex", available_time=available_time)
    buddy = Pet(name="Buddy", species="Dog", age=3)
    owner.add_pet(buddy)
    return Scheduler(owner), buddy


# ── Existing tests (kept) ─────────────────────────────────────────────────────

def test_task_completion():
    """mark_completed() should set completed to True."""
    task = Task(task_name="Morning Walk", category="exercise", duration=30, frequency="daily")
    assert task.completed == False
    task.mark_completed()
    assert task.completed == True


def test_task_addition():
    """Adding a task to a Pet should increase the pet's task count by 1."""
    pet = Pet(name="Buddy", species="Dog", age=3)
    assert len(pet.tasks) == 0
    pet.add_task(Task(task_name="Feeding", category="feeding", duration=10, frequency="daily"))
    assert len(pet.tasks) == 1


# ── 1. Sorting correctness ────────────────────────────────────────────────────

def test_sort_by_time_chronological_order():
    """Tasks added out of order should come back sorted earliest → latest."""
    scheduler, buddy = make_scheduler()
    buddy.add_task(Task("Afternoon Walk", "exercise", 30, "daily", start_time="14:00"))
    buddy.add_task(Task("Feeding",        "feeding",  10, "daily", start_time="07:30"))
    buddy.add_task(Task("Morning Walk",   "exercise", 30, "daily", start_time="08:00"))
    scheduler.generate_plan()

    sorted_plan = scheduler.sort_by_time()
    times = [t.start_time for _, t in sorted_plan]
    assert times == ["07:30", "08:00", "14:00"], f"Expected sorted times, got {times}"


def test_sort_by_time_no_start_time_goes_last():
    """Tasks without a start_time should appear at the end of the sorted list."""
    scheduler, buddy = make_scheduler()
    buddy.add_task(Task("Mystery Task", "exercise", 10, "daily", start_time=None))
    buddy.add_task(Task("Feeding",      "feeding",  10, "daily", start_time="07:30"))
    scheduler.generate_plan()

    sorted_plan = scheduler.sort_by_time()
    last_task = sorted_plan[-1][1]
    assert last_task.start_time is None, "Task with no time should sort to the end"


# ── 2. Recurrence logic ───────────────────────────────────────────────────────

def test_daily_recurrence_due_date():
    """Completing a daily task should return a new task due tomorrow."""
    today = date.today()
    task = Task("Feeding", "feeding", 10, "daily", due_date=today)
    next_task = task.mark_completed()

    assert next_task is not None, "Daily task should produce a follow-up"
    assert next_task.due_date == today + timedelta(days=1), (
        f"Expected {today + timedelta(days=1)}, got {next_task.due_date}"
    )
    assert next_task.completed == False, "New task should start as Pending"


def test_weekly_recurrence_due_date():
    """Completing a weekly task should return a new task due in 7 days."""
    today = date.today()
    task = Task("Bath Time", "grooming", 20, "weekly", due_date=today)
    next_task = task.mark_completed()

    assert next_task is not None, "Weekly task should produce a follow-up"
    assert next_task.due_date == today + timedelta(days=7), (
        f"Expected {today + timedelta(days=7)}, got {next_task.due_date}"
    )


def test_one_off_task_no_recurrence():
    """A task with frequency 'monthly' should return None — no follow-up."""
    task = Task("Vet Visit", "health", 60, "monthly")
    next_task = task.mark_completed()
    assert next_task is None, "Non-daily/weekly task should not recur"


def test_complete_task_adds_to_pet():
    """Scheduler.complete_task() should append the next task to the pet's list."""
    scheduler, buddy = make_scheduler()
    buddy.add_task(Task("Feeding", "feeding", 10, "daily", start_time="07:30"))
    scheduler.generate_plan()

    task_count_before = len(buddy.tasks)
    scheduler.complete_task("Buddy", "Feeding")
    assert len(buddy.tasks) == task_count_before + 1, (
        "A new recurring task should have been added to Buddy's list"
    )


# ── 3. Conflict detection ─────────────────────────────────────────────────────

def test_conflict_detected_same_pet_overlap():
    """Two tasks on the same pet with overlapping windows should be flagged."""
    scheduler, buddy = make_scheduler()
    # Morning Walk: 08:00–08:30, Training: 08:15–08:35 → 15-min overlap
    buddy.add_task(Task("Morning Walk", "exercise", 30, "daily", start_time="08:00"))
    buddy.add_task(Task("Training",     "exercise", 20, "daily", start_time="08:15"))
    scheduler.generate_plan()

    conflicts = scheduler.detect_conflicts()
    assert len(conflicts) == 1, f"Expected 1 conflict, got {len(conflicts)}"
    assert "Morning Walk" in conflicts[0]
    assert "Training" in conflicts[0]


def test_conflict_detected_across_pets():
    """Tasks belonging to different pets can still conflict."""
    owner = Owner(name="Alex", available_time=120)
    buddy    = Pet(name="Buddy",    species="Dog", age=3)
    whiskers = Pet(name="Whiskers", species="Cat", age=5)
    owner.add_pet(buddy)
    owner.add_pet(whiskers)

    # Buddy 07:30–07:40, Whiskers 07:35–07:45 → 5-min overlap
    buddy.add_task(   Task("Feeding", "feeding", 10, "daily", start_time="07:30"))
    whiskers.add_task(Task("Feeding", "feeding", 10, "daily", start_time="07:35"))

    scheduler = Scheduler(owner)
    scheduler.generate_plan()

    conflicts = scheduler.detect_conflicts()
    assert len(conflicts) == 1, f"Expected 1 cross-pet conflict, got {len(conflicts)}"


def test_no_conflict_when_tasks_are_sequential():
    """Back-to-back tasks that don't overlap should produce no conflicts."""
    scheduler, buddy = make_scheduler()
    # Walk ends exactly at 08:30; Feeding starts at 08:30 — adjacent, not overlapping
    buddy.add_task(Task("Morning Walk", "exercise", 30, "daily", start_time="08:00"))
    buddy.add_task(Task("Feeding",      "feeding",  10, "daily", start_time="08:30"))
    scheduler.generate_plan()

    conflicts = scheduler.detect_conflicts()
    assert conflicts == [], f"Expected no conflicts, got {conflicts}"


def test_no_conflict_with_no_start_times():
    """Tasks without start_time should be skipped — no false positives."""
    scheduler, buddy = make_scheduler()
    buddy.add_task(Task("Walk",    "exercise", 30, "daily", start_time=None))
    buddy.add_task(Task("Feeding", "feeding",  10, "daily", start_time=None))
    scheduler.generate_plan()

    conflicts = scheduler.detect_conflicts()
    assert conflicts == [], "Tasks without start_time should never conflict"


# ── 4. Edge cases ─────────────────────────────────────────────────────────────

def test_pet_with_no_tasks_generates_empty_plan():
    """An owner whose pet has zero tasks should get an empty plan, not a crash."""
    scheduler, _ = make_scheduler()   # Buddy has no tasks
    plan = scheduler.generate_plan()
    assert plan == []


def test_owner_with_zero_available_time():
    """No tasks should be scheduled when the owner has 0 minutes available."""
    scheduler, buddy = make_scheduler(available_time=0)
    buddy.add_task(Task("Feeding", "feeding", 10, "daily", required=True))
    plan = scheduler.generate_plan()
    assert plan == [], "No tasks should fit in 0 minutes"


def test_required_tasks_scheduled_before_optional():
    """Required tasks must appear in the plan before optional ones."""
    scheduler, buddy = make_scheduler(available_time=50)
    buddy.add_task(Task("Optional Grooming", "grooming",  20, "daily", required=False))
    buddy.add_task(Task("Required Feeding",  "feeding",   10, "daily", required=True))
    scheduler.generate_plan()

    pet_names, tasks = zip(*scheduler.generated_plan)
    task_names = [t.task_name for t in tasks]
    assert task_names.index("Required Feeding") < task_names.index("Optional Grooming"), (
        "Required task should appear before optional task in the plan"
    )


def test_filter_by_pet_name_case_insensitive():
    """filter_tasks should match pet names regardless of case."""
    scheduler, buddy = make_scheduler()
    buddy.add_task(Task("Feeding", "feeding", 10, "daily"))
    scheduler.generate_plan()

    result = scheduler.filter_tasks(pet_name="buddy")   # lowercase
    assert len(result) == 1
    assert result[0][0] == "Buddy"


def test_filter_completed_tasks():
    """filter_tasks(completed=True) should return only done tasks."""
    scheduler, buddy = make_scheduler()
    buddy.add_task(Task("Feeding",      "feeding",  10, "daily"))
    buddy.add_task(Task("Morning Walk", "exercise", 30, "daily"))
    scheduler.generate_plan()

    buddy.tasks[0].mark_completed()   # mark Feeding done
    scheduler.generate_plan()         # regenerate so plan reflects new state

    done = scheduler.filter_tasks(completed=True)
    assert len(done) == 1
    assert done[0][1].task_name == "Feeding"
