# main.py — testing ground for PawPal+

from pawpal_system import Owner, Pet, Task, Scheduler

# --- Create Owner ---
owner = Owner(name="Alex", available_time=120, preferences=["morning routine", "no baths on weekdays"])

# --- Create Pets ---
buddy    = Pet(name="Buddy",    species="Dog", age=3, notes="Loves long walks")
whiskers = Pet(name="Whiskers", species="Cat", age=5, notes="Indoor only")

# --- Tasks (two intentional conflicts planted) ---
#
#  CONFLICT 1 (same pet): Buddy's "Morning Walk" starts 08:00 (30 min → ends 08:30)
#                         Buddy's "Training"    starts 08:15 (20 min → ends 08:35)
#
#  CONFLICT 2 (diff pets): Buddy's   "Feeding"  starts 07:30 (10 min → ends 07:40)
#                          Whiskers' "Feeding"  starts 07:35 (10 min → ends 07:45)
#
buddy.add_task(Task("Afternoon Walk", category="exercise",  duration=30, frequency="daily",  required=True,  start_time="14:00"))
buddy.add_task(Task("Feeding",        category="feeding",   duration=10, frequency="daily",  required=True,  start_time="07:30"))  # overlaps Whiskers 07:35
buddy.add_task(Task("Bath Time",      category="grooming",  duration=20, frequency="weekly", required=False, start_time="10:00"))
buddy.add_task(Task("Morning Walk",   category="exercise",  duration=30, frequency="daily",  required=True,  start_time="08:00"))  # overlaps Training 08:15
buddy.add_task(Task("Training",       category="exercise",  duration=20, frequency="daily",  required=False, start_time="08:15"))  # ← conflict with Morning Walk

whiskers.add_task(Task("Feeding",     category="feeding",   duration=10, frequency="daily",  required=True,  start_time="07:35"))  # ← conflict with Buddy Feeding
whiskers.add_task(Task("Evening Play",category="exercise",  duration=15, frequency="daily",  required=False, start_time="18:00"))

owner.add_pet(buddy)
owner.add_pet(whiskers)

scheduler = Scheduler(owner)
scheduler.generate_plan()

# ── SORTED SCHEDULE ───────────────────────────────────────────────────────────
print("=" * 68)
print("        PAWPAL+ — TODAY'S SCHEDULE (sorted by time)")
print("=" * 68)
for pet_name, task in scheduler.sort_by_time():
    print(f"  [{pet_name}] {task.get_task_details()}")

# ── CONFLICT DETECTION ────────────────────────────────────────────────────────
print("\n" + "=" * 68)
print("        CONFLICT DETECTION")
print("=" * 68)
conflicts = scheduler.detect_conflicts()
if conflicts:
    for warning in conflicts:
        print(warning)
else:
    print("  No conflicts detected.")

# ── COMPLETE SOME TASKS (recurring logic) ─────────────────────────────────────
print("\n" + "=" * 68)
print("        COMPLETING TASKS — recurring follow-ups auto-created")
print("=" * 68)
scheduler.complete_task("Buddy",    "Feeding")      # daily  → +1 day
scheduler.complete_task("Whiskers", "Feeding")      # daily  → +1 day
scheduler.complete_task("Buddy",    "Bath Time")    # weekly → +7 days

# ── FILTER: pending tasks only ────────────────────────────────────────────────
scheduler.generate_plan()
print("\n" + "=" * 68)
print("        FILTER — PENDING TASKS ONLY")
print("=" * 68)
for pet_name, task in scheduler.filter_tasks(completed=False):
    print(f"  [{pet_name}] {task.get_task_details()}")

print("=" * 68)
