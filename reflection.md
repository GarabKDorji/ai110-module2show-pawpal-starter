# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

Owner — represents the person using the app. Responsible for storing their name, availability, and care preferences, and for viewing their task list.

Pet — represents each pet. Responsible for holding profile data (species, age, notes) and providing an up-to-date profile when needed.

Task — represents a single care activity (e.g. feeding, grooming). Responsible for storing task details like category, duration, priority, and whether it's required.

Scheduler — the core logic class. Responsible for managing the collection of tasks, generating a care plan based on the owner's available time, and explaining that plan.

Relationships:

An Owner owns one or more Pets
An Owner uses one Scheduler
A Scheduler manages zero or more Tasks
A Task is assigned to a specific Pet

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

**Tradeoff: O(n²) conflict detection vs. a sorted sweep**

`detect_conflicts()` compares every pair of scheduled tasks using
`itertools.combinations`, which is O(n²). A more efficient approach would be
to sort tasks by `start_time` first and then do a single linear sweep,
checking each task only against the one directly before it — O(n log n) total.

The O(n²) approach was kept because:

1. **Scale doesn't justify the complexity.** A typical pet owner schedules
   fewer than 20 tasks per day. At that size the two approaches are
   indistinguishable in speed, and the combinations loop is easier to read and
   verify at a glance.

2. **The linear sweep only catches adjacent conflicts.** If three tasks
   overlap (A overlaps B, B overlaps C, A overlaps C), a naive sweep can miss
   the A–C pair. The pairwise approach catches all combinations correctly
   without extra bookkeeping.

3. **Readability over micro-optimization.** For a scheduling assistant used by
   a single owner, correctness and clarity matter more than shaving
   microseconds. If the task list ever grew large (e.g., a pet hotel managing
   hundreds of animals), switching to a sorted sweep or an interval tree would
   be the right call.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
