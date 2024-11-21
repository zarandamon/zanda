from fastapi import WebSocket, WebSocketDisconnect
from hermes.server.job_queue.task_manager import update_task_status, cleanup_completed_tasks
from hermes.server.job_queue.scheduler import get_next_task

import asyncio
# from hermes.shared.logging_config import logger

# In-memory storage for worker WebSocket connections
workers = []

async def handle_worker(websocket: WebSocket):
    await websocket.accept()
    workers.append(websocket)
    print("Worker connected.")

    try:
        while True:
            task = get_next_task()
            if task:
                print(f"Sending task {task['task_id']} to worker.")
                await websocket.send_json(task)

                # Use a single response-receiving loop
                try:
                    response = await websocket.receive_json()
                    print(f"Received worker response: {response}")
                    
                    if "percent_complete" in response:
                        print(f"Task progress: {response['percent_complete']}%")
                    elif response.get("status") == "completed":
                        update_task_status(response["task_id"], "completed")
                        print(f"Task {response['task_id']} completed.")
       
                        # Schedule cleanup for completed tasks
                        asyncio.ensure_future(cleanup_completed_tasks(response["task_id"]))


                except Exception as e:
                    print(f"Error receiving message from worker: {e}")
                    break  # Exit loop to prevent blocking
    except WebSocketDisconnect:
        print("Worker disconnected.")
    finally:
        workers.remove(websocket)