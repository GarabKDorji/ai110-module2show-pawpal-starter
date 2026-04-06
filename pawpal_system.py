# pawpal_system.py


class Task:
    def __init__(self, task_name, category, duration, frequency, required=False):
        self.task_name = task_name
        self.category = category        # e.g. "feeding", "grooming", "exercise"
        self.duration = duration        # in minutes
        self.frequency = frequency      # e.g. "daily", "weekly"
        self.required = required
        self.completed = False

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
        """Mark this task as done by setting completed to True."""
        self.completed = True

    def get_task_details(self):
        """Return a formatted string summarizing all task attributes and status."""
        status = "Done" if self.completed else "Pending"
        required_label = "Required" if self.required else "Optional"
        return (
            f"Task: {self.task_name} | Category: {self.category} | "
            f"Duration: {self.duration} min | Frequency: {self.frequency} | "
            f"{required_label} | Status: {status}"
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
