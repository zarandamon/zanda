import uuid

# In-memory storage for jobs
jobs = {}

def create_job(scene_path, frame, ROP_node):
    """
    Creates a new job and returns its ID and data.
    """
    job_id = str(uuid.uuid4())
    job = {
        "scene_path": scene_path,
        "frame": frame,
        "ROP_node": ROP_node,
        "status": "pending"
    }
    jobs[job_id] = job
    return job_id, job

def update_job_status(job_id, status):
    """
    Updates the status of a job.
    """
    if job_id in jobs:
        jobs[job_id]["status"] = status
