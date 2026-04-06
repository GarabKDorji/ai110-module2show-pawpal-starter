# pawpal_system.py

from datetime import date, timedelta
from itertools import combinations


class Task:
    def __init__(self, task_name, category, duration, frequency, required=False, start_time=None, due_date=None):
        self.task_name = task_name
        self.category = category        # e.g. "feeding", "grooming", "exercise"
        self.duration = duration        # in minutes
        self.frequency = frequency      # e.g. "daily", "weekly"
        self.required = required
        self.completed = False
        self.start_time = start_time    # "HH:MM" string, e.g. "08:00"
        self.due_date = due_date or date.today()  # date object; defaults to today

    def edit_task(self, task_name=None, category=None, duration=None, frequency=None):
        """Update one or more fields of the task; unchanged fields are left as-is."""
        if task_name is not None:
            self.task_name = task_name
        if category is not None:
            self.category = category
        if duration is not None:
            self.duration = duration
        if frequency is not None:
            self.frequency = frequency

    def mark_required(self):
        """Flag this task as required so the Scheduler prioritizes it."""
        self.required = True

    def mark_completed(self):
        """
        Mark this task as done and return a fresh Task for the next occurrence.
        - "daily"  → due_date + 1 day   (timedelta(days=1))
        - "weekly" → due_date + 7 days  (timedelta(days=7))
        Returns None for one-off tasks (any other frequency string).
        """
        self.completed = True

        if self.frequency == "daily":
            next_due = self.due_date + timedelta(days=1)
        elif self.frequency == "weekly":
            next_due = self.due_date + timedelta(days=7)
        else:
            return None  # non-recurring task — no follow-up created

        return Task(
            task_name=self.task_name,
            category=self.category,
            duration=self.duration,
            frequency=self.frequency,
            required=self.required,
            start_time=self.start_time,
            due_date=next_due,
        )

    def get_task_details(self):
        """Return a formatted string summarizing all task attributes and status."""
        status = "Done" if self.completed else "Pending"
        required_label = "Required" if self.required else "Optional"
        time_label = self.start_time if self.start_time else "No time set"
        return (
            f"[{time_label}] Task: {self.task_name} | Category: {self.category} | "
            f"Duration: {self.duration} min | Frequency: {self.frequency} | "
            f"Due: {self.due_date} | {required_label} | Status: {status}"
        )


class Pet:
    def __init__(self, name, species, age, notes=""):
        self.name = name
        self.species = species
        self.age = age
        self.notes = notes
        self.tasks = []                 # list of Task objects

    def add_task(self, task):
        """Append a Task object to this pet's task list."""
        self.tasks.append(task)

    def remove_task(self, task_name):
        """Remove a task from this pet's list by matching its name."""
        self.tasks = [t for t in self.tasks if t.task_name != task_name]

    def update_info(self, name=None, species=None, age=None, notes=None):
        """Update any pet profile fields; omitted arguments are left unchanged."""
        if name is not None:
            self.name = name
        if species is not None:
            self.species = species
        if age is not None:
            self.age = age
        if notes is not None:
            self.notes = notes

    def get_profile(self):
        """Return a formatted string with the pet's profile info and task count."""
        return (
            f"Pet: {self.name} | Species: {self.species} | "
            f"Age: {self.age} | Notes: {self.notes} | "
            f"Tasks: {len(self.tasks)}"
        )


class Owner:
    def __init__(self, name, available_time, preferences=None):
        self.name = name
        self.available_time = available_time    # total minutes available per day
        self.preferences = preferences or []    # e.g. ["morning walks", "no baths on weekdays"]
        self.pets = []                          # list of Pet objects

    def add_pet(self, pet):
        """Register a Pet object under this owner."""
        self.pets.append(pet)

    def remove_pet(self, pet_name):
        """Remove a pet from the owner's list by matching its name."""
        self.pets = [p for p in self.pets if p.name != pet_name]

    def set_preferences(self, preferences):
        """Replace the owner's care preferences with a new list."""
        self.preferences = preferences

    def update_available_time(self, minutes):
        """Set the total number of minutes the owner has available each day."""
        self.available_time = minutes

    def get_all_tasks(self):
        """Return all tasks across every pet, each tagged with the pet's name."""
        all_tasks = []
        for pet in self.pets:
            for task in pet.tasks:
                all_tasks.append((pet.name, task))
        return all_tasks

    def view_tasks(self):
        """Print all tasks across every pet owned by this owner."""
        all_tasks = self.get_all_tasks()
        if not all_tasks:
            print(f"{self.name} has no tasks scheduled.")
            return
        print(f"\n--- Tasks for {self.name}'s pets ---")
        for pet_name, task in all_tasks:
            print(f"[{pet_name}] {task.get_task_details()}")


class Scheduler:
    def __init__(self, owner):
        self.owner = owner              # Scheduler is linked to one Owner
        self.generated_plan = []        # list of (pet_name, Task) tuples

    def add_task(self, pet_name, task):
        """Add a task to a specific pet by name."""
        for pet in self.owner.pets:
            if pet.name == pet_name:
                pet.add_task(task)
                return
        print(f"Pet '{pet_name}' not found.")

    def remove_task(self, pet_name, task_name):
        """Remove a task from a specific pet by name."""
        for pet in self.owner.pets:
            if pet.name == pet_name:
                pet.remove_task(task_name)
                return
        print(f"Pet '{pet_name}' not found.")

    def generate_plan(self):
        """
        Build a prioritized daily plan that fits within the owner's available time.
        Required tasks are scheduled first, then optional tasks in order added.
        """
        all_tasks = self.owner.get_all_tasks()
        required = [(pn, t) for pn, t in all_tasks if t.required]
        optional = [(pn, t) for pn, t in all_tasks if not t.required]

        self.generated_plan = []
        time_remaining = self.owner.available_time

        for pet_name, task in required + optional:
            if task.duration <= time_remaining:
                self.generated_plan.append((pet_name, task))
                time_remaining -= task.duration

        return self.generated_plan

    def complete_task(self, pet_name, task_name):
        """Mark a task done and automatically schedule its next occurrence.

        Calls ``Task.mark_completed()``, which uses ``timedelta`` to calculate
        the next due date — +1 day for "daily" tasks, +7 days for "weekly"
        tasks — and returns a fresh ``Task`` object. That object is added back
        to the pet so it appears in future calls to ``generate_plan()``.
        One-off tasks (any other frequency) are marked done with no follow-up.

        Args:
            pet_name (str): Name of the pet whose task should be completed.
                Comparison is case-insensitive.
            task_name (str): Name of the task to complete.
                Comparison is case-insensitive.

        Returns:
            None: Side effects only — marks the task complete and may append
            a new Task to the pet's task list.
        """
        for pet in self.owner.pets:
            if pet.name.lower() != pet_name.lower():
                continue
            for task in pet.tasks:
                if task.task_name.lower() != task_name.lower():
                    continue
                next_task = task.mark_completed()
                if next_task:
                    pet.add_task(next_task)
                    print(f"  ✓ '{task_name}' done. Next occurrence added for {next_task.due_date} ({next_task.frequency}).")
                else:
                    print(f"  ✓ '{task_name}' done. No recurrence (one-off task).")
                return
        print(f"  Task '{task_name}' not found for pet '{pet_name}'.")

    def detect_conflicts(self):
        """Check every pair of scheduled tasks for overlapping time windows.

        Strategy: convert each "HH:MM" start_time to total minutes since
        midnight, then apply the standard interval-overlap test —
        ``a_start < b_end and b_start < a_end`` — for every unique pair via
        ``itertools.combinations``. Tasks without a ``start_time`` are skipped
        because their window cannot be determined.

        Returns:
            list[str]: Human-readable warning messages, one per conflict found.
                Returns an empty list when no overlaps are detected. The program
                never raises an exception from this method.

        Example warning::

            "CONFLICT: [Buddy] 'Morning Walk' (08:00, 30 min) overlaps with
             [Buddy] 'Training' (08:15, 20 min)"
        """
        def to_minutes(hhmm):
            h, m = map(int, hhmm.split(":"))
            return h * 60 + m

        timed = [(pn, t) for pn, t in self.generated_plan if t.start_time]
        warnings = []

        for (pn_a, task_a), (pn_b, task_b) in combinations(timed, 2):
            a_start = to_minutes(task_a.start_time)
            b_start = to_minutes(task_b.start_time)
            if a_start < b_start + task_b.duration and b_start < a_start + task_a.duration:
                warnings.append(
                    f"  CONFLICT: [{pn_a}] '{task_a.task_name}' "
                    f"({task_a.start_time}, {task_a.duration} min) overlaps with "
                    f"[{pn_b}] '{task_b.task_name}' "
                    f"({task_b.start_time}, {task_b.duration} min)"
                )

        return warnings

    def sort_by_time(self):
        """Sort the generated plan chronologically by each task's start_time.

        Uses ``sorted()`` with a lambda key so that zero-padded "HH:MM" strings
        compare correctly via lexicographic order ("08:00" < "09:30" < "14:00").
        Tasks whose ``start_time`` is ``None`` are placed at the end of the list.

        Returns:
            list[tuple[str, Task]]: A new list of (pet_name, Task) pairs ordered
            from earliest to latest start time.
        """
        return sorted(
            self.generated_plan,
            key=lambda pair: pair[1].start_time if pair[1].start_time else "99:99"
        )

    def filter_tasks(self, pet_name=None, completed=None):
        """Filter the generated plan by pet name and/or completion status.

        Both parameters are optional; omitting one means "no filter on that axis".
        Filters are applied together (AND logic), so passing both narrows further.

        Args:
            pet_name (str | None): Keep only tasks belonging to this pet.
                Comparison is case-insensitive. ``None`` keeps all pets.
            completed (bool | None): ``True`` returns only finished tasks,
                ``False`` returns only pending tasks, ``None`` returns both.

        Returns:
            list[tuple[str, Task]]: Filtered list of (pet_name, Task) pairs.
        """
        results = self.generated_plan
        if pet_name is not None:
            results = [(pn, t) for pn, t in results if pn.lower() == pet_name.lower()]
        if completed is not None:
            results = [(pn, t) for pn, t in results if t.completed == completed]
        return results

    def explain_plan(self):
        """Print a human-readable summary of the generated plan."""
        if not self.generated_plan:
            print("No plan generated yet. Call generate_plan() first.")
            return

        total = sum(t.duration for _, t in self.generated_plan)
        print(f"\n--- Daily Care Plan for {self.owner.name} ---")
        print(f"Available time: {self.owner.available_time} min | Scheduled: {total} min\n")
        for pet_name, task in self.generated_plan:
            print(f"  [{pet_name}] {task.get_task_details()}")
        print(f"\n{len(self.generated_plan)} task(s) scheduled.")
