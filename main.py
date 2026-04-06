# main.py — testing ground for PawPal+

from pawpal_system import Owner, Pet, Task, Scheduler

# --- Create Owner ---
owner = Owner(name="Alex", available_time=90, preferences=["morning routine", "no baths on weekdays"])

# --- Create Pets ---
buddy = Pet(name="Buddy", species="Dog", age=3, notes="Loves long walks")
whiskers = Pet(name="Whiskers", species="Cat", age=5, notes="Indoor only")

# --- Add Tasks to Buddy ---
buddy.add_task(Task("Morning Walk",   category="exercise",  duration=30, frequency="daily",  required=True))
buddy.add_task(Task("Feeding",        category="feeding",   duration=10, frequency="daily",  required=True))
buddy.add_task(Task("Bath Time",      category="grooming",  duration=20, frequency="weekly", required=False))

# --- Add Tasks to Whiskers ---
whiskers.add_task(Task("Feeding",     category="feeding",   duration=10, frequency="daily",  required=True))
whiskers.add_task(Task("Playtime",    category="exercise",  duration=15, frequency="daily",  required=False))

# --- Register Pets with Owner ---
owner.add_pet(buddy)
owner.add_pet(whiskers)

# --- Set up Scheduler and Generate Plan ---
scheduler = Scheduler(owner)
scheduler.generate_plan()

print("=" * 50)
print("         PAWPAL+ — TODAY'S SCHEDULE")
print("=" * 50)
scheduler.explain_plan()
print("=" * 50)
