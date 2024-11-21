import asyncio
from hermes.server.job_queue.task_manager import tasks

async def get_next_task():
    """
    Asynchronously returns the next pending task.
    If no tasks are available, waits before retrying.
    """
    while True:
        for task_id, task in tasks.items():
            if task["status"] == "pending":
                tasks[task_id]["status"] = "assigned"
                return task
        
        # No pending tasks, wait briefly to yield control
        await asyncio.sleep(1)