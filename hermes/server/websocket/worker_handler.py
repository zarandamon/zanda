import asyncio
from fastapi import WebSocket, WebSocketDisconnect
from hermes.server.job_queue.task_manager import update_task_status
from hermes.server.job_queue.scheduler import get_next_task
from hermes.server.job_queue.task_manager import tasks

# In-memory storage for worker WebSocket connections
workers = []

async def handle_worker(websocket: WebSocket):
    await websocket.accept()
    print("Worker connected.")
    
    try:
        while True:
            # Fetch the next task asynchronously
            task = await get_next_task()

            if task:
                print(f"Sending task {task['task_id']} to worker.")
                try:
                    await websocket.send_json(task)

                    while True:
                        # Wait for progress updates or task completion from the worker
                        response = await websocket.receive_json()
                        print(f"Received worker response: {response}")

                        # Ensure response contains necessary fields
                        if all(key in response for key in ["task_id", "percent_complete", "elapsed_time", "time_left"]):
                            task_id = response["task_id"]
                            if task_id in tasks:
                                tasks[task_id]["percent_complete"] = response["percent_complete"]
                                tasks[task_id]["elapsed_time"] = response["elapsed_time"]
                                tasks[task_id]["time_left"] = response["time_left"]
                                # print(f"Updated task {task_id}: {tasks[task_id]}")
                            else:
                                print(f"Task {task_id} not found in tasks.")
                        elif response.get("percent_complete") == 100:
                            # Update task status to completed
                            update_task_status(response["task_id"], "completed")
                            # print(f"Task {response['task_id']} marked as completed.")

                        else:
                            print(f"Incomplete or unknown response: {response}")

                except WebSocketDisconnect:
                    print("Worker disconnected.")
                    break
                except Exception as e:
                    print(f"Error communicating with worker: {e}")
                    break
            else:
                print("No tasks available.")
                await asyncio.sleep(1)  # Yield control if no tasks
    except WebSocketDisconnect:
        print("Worker disconnected.")
    finally:
        if websocket in workers:
            workers.remove(websocket)
            print("Worker removed.")

