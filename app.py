import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")
st.caption("Smart pet care scheduling for busy owners.")

# ── Session state init ────────────────────────────────────────────────────────

if "owner" not in st.session_state:
    st.session_state.owner = None
if "scheduler" not in st.session_state:
    st.session_state.scheduler = None
if "raw_tasks" not in st.session_state:
    # list of dicts so we can rebuild the scheduler on each run
    st.session_state.raw_tasks = []

# ── Section 1: Owner & Pet setup ──────────────────────────────────────────────

st.header("1. Owner & Pet")

col1, col2 = st.columns(2)
with col1:
    owner_name = st.text_input("Owner name", value="Alex")
    available_time = st.number_input("Available time today (min)", min_value=0, max_value=480, value=120)
with col2:
    pet_name = st.text_input("Pet name", value="Buddy")
    species = st.selectbox("Species", ["Dog", "Cat", "Rabbit", "Other"])

# ── Section 2: Add tasks ──────────────────────────────────────────────────────

st.header("2. Add Tasks")

with st.form("add_task_form", clear_on_submit=True):
    c1, c2, c3 = st.columns(3)
    with c1:
        task_name = st.text_input("Task name", value="Morning Walk")
        category  = st.selectbox("Category", ["exercise", "feeding", "grooming", "health", "other"])
    with c2:
        duration   = st.number_input("Duration (min)", min_value=1, max_value=240, value=30)
        frequency  = st.selectbox("Frequency", ["daily", "weekly", "monthly"])
    with c3:
        start_time = st.text_input("Start time (HH:MM)", value="08:00")
        required   = st.checkbox("Required task", value=True)

    submitted = st.form_submit_button("Add Task")
    if submitted:
        st.session_state.raw_tasks.append({
            "task_name":  task_name,
            "category":   category,
            "duration":   int(duration),
            "frequency":  frequency,
            "start_time": start_time.strip() or None,
            "required":   required,
        })
        st.success(f"Added '{task_name}' to the list.")

# Show current task list
if st.session_state.raw_tasks:
    st.subheader("Tasks entered")
    st.table(st.session_state.raw_tasks)

    if st.button("Clear all tasks"):
        st.session_state.raw_tasks = []
        st.session_state.scheduler = None
        st.rerun()

# ── Section 3: Generate schedule ─────────────────────────────────────────────

st.header("3. Generate Schedule")

if st.button("Generate Schedule", type="primary"):
    if not st.session_state.raw_tasks:
        st.warning("Add at least one task before generating a schedule.")
    else:
        # Build objects fresh from session state
        owner = Owner(name=owner_name, available_time=int(available_time))
        pet   = Pet(name=pet_name, species=species, age=0)
        for td in st.session_state.raw_tasks:
            pet.add_task(Task(
                task_name  = td["task_name"],
                category   = td["category"],
                duration   = td["duration"],
                frequency  = td["frequency"],
                required   = td["required"],
                start_time = td["start_time"],
            ))
        owner.add_pet(pet)

        scheduler = Scheduler(owner)
        scheduler.generate_plan()

        st.session_state.owner     = owner
        st.session_state.scheduler = scheduler

# ── Section 4: Results ────────────────────────────────────────────────────────

if st.session_state.scheduler:
    scheduler = st.session_state.scheduler
    owner     = st.session_state.owner

    st.header("4. Today's Plan")

    # ── Conflict warnings (shown first so owner can act) ─────────────────────
    conflicts = scheduler.detect_conflicts()
    if conflicts:
        st.error(f"⚠️ {len(conflicts)} scheduling conflict(s) found — please review before starting your day.")
        for msg in conflicts:
            st.warning(msg.strip())
    else:
        st.success("✅ No scheduling conflicts detected.")

    # ── Sorted schedule table ─────────────────────────────────────────────────
    sorted_plan = scheduler.sort_by_time()

    if sorted_plan:
        total_min = sum(t.duration for _, t in sorted_plan)
        st.caption(f"Scheduled: **{total_min} min** of {int(owner.available_time)} min available")

        rows = []
        for pn, task in sorted_plan:
            rows.append({
                "Time":     task.start_time or "—",
                "Pet":      pn,
                "Task":     task.task_name,
                "Category": task.category,
                "Duration": f"{task.duration} min",
                "Frequency": task.frequency,
                "Priority": "Required" if task.required else "Optional",
                "Status":   "✅ Done" if task.completed else "🔲 Pending",
            })
        st.table(rows)
    else:
        st.info("No tasks fit within the available time.")

    # ── Filter panel ──────────────────────────────────────────────────────────
    st.header("5. Filter Tasks")

    col_a, col_b = st.columns(2)
    with col_a:
        filter_pet = st.text_input("Filter by pet name (leave blank for all)")
    with col_b:
        filter_status = st.selectbox("Filter by status", ["All", "Pending", "Done"])

    completed_flag = None
    if filter_status == "Done":
        completed_flag = True
    elif filter_status == "Pending":
        completed_flag = False

    filtered = scheduler.filter_tasks(
        pet_name  = filter_pet.strip() or None,
        completed = completed_flag,
    )

    if filtered:
        filter_rows = []
        for pn, task in filtered:
            filter_rows.append({
                "Time":     task.start_time or "—",
                "Pet":      pn,
                "Task":     task.task_name,
                "Status":   "✅ Done" if task.completed else "🔲 Pending",
            })
        st.table(filter_rows)
    else:
        st.info("No tasks match the current filter.")
