import asyncio
from fastapi import WebSocket, WebSocketDisconnect
from hermes.server.job_queue.task_manager import tasks  # Import the shared tasks dictionary
# from hermes.shared.logging_config import logger


async def handle_server_ui(websocket: WebSocket):
    """
    Handles UI WebSocket communication and sends updates for active tasks only.
    """
    await websocket.accept()
    print("UI WebSocket connection established.")
    try:
        while True:
            # Filter out completed tasks and use 0 as default for percent_complete
            active_tasks = {
                task_id: task
                for task_id, task in tasks.items()
                if task.get("status") != "completed" or task.get("percent_complete", 0) < 100
            }

            # Send only active tasks to the UI
            await websocket.send_json({"tasks": active_tasks})

            # Debug log to confirm filtered tasks
            # print(f"Sending active tasks to UI: {active_tasks}")

            await asyncio.sleep(1)  # Periodic updates
    except WebSocketDisconnect:
        print("UI WebSocket disconnected.")






