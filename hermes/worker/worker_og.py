import asyncio
import websockets
import json
import re
import os
import signal

WORKER_ID = "worker_001"
SERVER_URI = os.getenv("SERVER_URI", "ws://127.0.0.1:8000/ws/worker")



async def process_task(task, websocket):
    """
    Processes a task by calling hip_render.py via Hython and reports progress.
    """
    task_id = task['task_id']
    scene_path = task['scene_path']
    frame = task['frame']
    render_node = task['ROP_node']  # Update as needed

    print(f"Processing task {task_id}...")


    try:
        # Path to Hython and hip_render.py
        hython_executable = r"C:\Program Files\Side Effects Software\Houdini 20.5.278\bin\hython.exe"  # Update path
        script_path = r"/zanda/hermes/worker/tasks/hip_render_tsk.py"  # Adjust path

        progress_regex = re.compile(r'(\d+)% Lap=([0-9:.]+) Left=([0-9:.]+)')

        # custom_env["ARNOLD_LICENSE_ORDER"] = "user"  # Use the correct licensing method
        # custom_env["solidangle_LICENSE"] = "single"
        # custom_env["ADSKFLEX_LICENSE_FILE"] = "@adskflex"
        # custom_env["ARNOLD_FORCE_ABORT_ON_LICENSE_FAIL"] = "0"

        # Custom environment with license variables
        custom_env = os.environ.copy()  # Copy current environment variables
        custom_env["QT_QPA_PLATFORM"] = "minimal"

        # Create subprocess asynchronously
        process = await asyncio.create_subprocess_exec(
            hython_executable, script_path, scene_path, render_node, str(frame),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=custom_env  # Pass the custom environment
        )

        async def read_stream_and_update_progress(stream, websocket, task_id):
            """
            Reads the process output and sends progress updates.
            """
            progress_regex = re.compile(r"(\d+)% Lap=([0-9:.]+) Left=([0-9:.]+)")
            
            async for line in stream:
                decoded_line = line.decode().strip()
                print(f"[STDOUT] {decoded_line}")

                # Match progress lines
                match = progress_regex.search(decoded_line)
                if match:
                    percent_complete = int(match.group(1))
                    elapsed_time = match.group(2)
                    time_left = match.group(3)

                    # Send progress update
                    progress_data = {
                        "task_id": task_id,
                        "percent_complete": percent_complete,
                        "elapsed_time": elapsed_time,
                        "time_left": time_left,
                    }

                    try:
                        await websocket.send(json.dumps(progress_data))
                        print(f"Progress update sent: {progress_data}")
                    except Exception as e:
                        print(f"Failed to send progress update: {e}")

        # Create tasks to read stdout and stderr
        # Pass the websocket object instead of "STDOUT" or "STDERR"
        stdout_task = asyncio.create_task(read_stream_and_update_progress(process.stdout, websocket, task_id))
        stderr_task = asyncio.create_task(read_stream_and_update_progress(process.stderr, websocket, task_id))


        # Wait for the process to complete and for the output to be consumed
        await process.wait()
        await asyncio.gather(stdout_task, stderr_task)

        if process.returncode == 0:
            print(f"Task {task_id} completed successfully.")
        else:
            print(f"Task {task_id} failed. See logs for details.")

    except Exception as e:
        print(f"Error while processing task {task_id}: {e}")

async def worker():
    while True:
        try:
            async with websockets.connect(SERVER_URI) as websocket:
                print(f"Worker {WORKER_ID} connected to server.")
                while True:
                    task = await websocket.recv()
                    task = json.loads(task)
                    print(f"Received task: {task}")
                    await process_task(task, websocket)
        except websockets.exceptions.ConnectionClosedError as e:
            print(f"Connection closed: {e}")
        except Exception as e:
            print(f"Connection error: {e}")


async def shutdown(signal, loop):
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    [task.cancel() for task in tasks]
    await asyncio.gather(*tasks, return_exceptions=True)
    loop.stop()


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, lambda s, l=loop: asyncio.create_task(shutdown(s, l)))

    try:
        loop.run_until_complete(worker())
    finally:
        loop.close()