# tests/test_pawpal.py

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pawpal_system import Task, Pet


def test_task_completion():
    """mark_completed() should change the task's completed status to True."""
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
