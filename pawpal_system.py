# pawpal_system.py


class Owner:
    def __init__(self, name, available_time, preferences):
        self.name = name
        self.available_time = available_time
        self.preferences = preferences

    def set_preferences(self):
        pass

    def update_available_time(self):
        pass

    def view_tasks(self):
        pass


class Pet:
    def __init__(self, name, species, age, notes):
        self.name = name
        self.species = species
        self.age = age
        self.notes = notes

    def update_info(self):
        pass

    def get_profile(self):
        pass


class Task:
    def __init__(self, task_name, category, duration, priority, required):
        self.task_name = task_name
        self.category = category
        self.duration = duration
        self.priority = priority
        self.required = required

    def edit_task(self):
        pass

    def mark_required(self):
        pass

    def get_task_details(self):
        pass


class Scheduler:
    def __init__(self, tasks, available_time, generated_plan):
        self.tasks = tasks
        self.available_time = available_time
        self.generated_plan = generated_plan

    def add_task(self):
        pass

    def remove_task(self):
        pass

    def generate_plan(self):
        pass

    def explain_plan(self):
        pass