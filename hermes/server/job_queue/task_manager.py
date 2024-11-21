import uuid
import asyncio


# In-memory storage for tasks
tasks = {}

def create_task(job_id, scene_path, frame, ROP_node):
    """
    Creates a task for the given job and returns its ID and data.
    """
    task_id = str(uuid.uuid4())
    task = {
        "task_id": task_id,
        "job_id": job_id,
        "scene_path": scene_path,
        "frame": frame,
        "ROP_node": ROP_node,
        "status": "pending"
    }
    tasks[task_id] = task
    return task_id, task

def update_task_status(task_id, status):
    """
    Updates the status of a task.
    """
    if task_id in tasks:
        tasks[task_id]["status"] = status
        # print(f"Task {task_id} updated to status {status}.")
    else:
        print(f"Task {task_id} not found in tasks.")


async def cleanup_completed_tasks(task_id, delay=10):
    """
    Removes completed tasks from the dictionary after a delay.
    """
    await asyncio.sleep(delay)
    if task_id in tasks and tasks[task_id]["status"] == "completed":
        del tasks[task_id]
        print(f"Task {task_id} removed after completion.")

