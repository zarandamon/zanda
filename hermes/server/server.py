from fastapi import FastAPI, WebSocket
# from hermes.shared.logging_config import logger


from hermes.server.job_queue.job_manager import create_job, jobs
from hermes.server.job_queue.task_manager import create_task, tasks
from hermes.server.websocket.worker_handler import handle_worker
from hermes.server.websocket.server_ui_handler import handle_server_ui


app = FastAPI()

@app.post("/submit-job")
async def submit_job(job: dict):
    """
    Receives a job request and creates an associated task.
    """
    job_id, job_data = create_job(job["scene_path"], job["frame"], job["ROP_node"])
    task_id, task_data = create_task(job_id, job["scene_path"], job["frame"], job["ROP_node"])
    print(f"Job created: {job_id}, Task created: {task_id}")  # Debug log

    return {
        "message": "Job submitted successfully",
        "job_id": job_id,
        "task_id": task_id,
        "task": task_data
    }


@app.websocket("/ws/worker")
async def worker_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for worker connections.
    """
    await handle_worker(websocket)

@app.websocket("/ws/ui")
async def ui_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for the ServerUI to receive real-time updates.
    """
    await handle_server_ui(websocket)

@app.get("/status")
async def get_status():
    """
    Returns the current status of tasks.
    """
    return {
        "tasks": tasks
    }
