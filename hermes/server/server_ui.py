import asyncio
import json
import websockets

from PySide6.QtWidgets import (
    QApplication, QVBoxLayout, QLabel, QTreeWidget, QTreeWidgetItem, QWidget,
    QMainWindow, QProgressBar
)
from PySide6.QtCore import Qt


class ServerUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Server Monitor")
        self.setGeometry(100, 100, 1200, 600)

        # Central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # UI Elements
        self.status_label = QLabel("Connecting to server...")
        self.task_list = QTreeWidget()
        self.task_list.setHeaderLabels([
            "Job ID", "Scene Path", "Frame", "ROP Node",
            "Status", "Completion", "Elapsed Time", "Time Left"
        ])

        # Add widgets to layout
        layout.addWidget(self.status_label)
        layout.addWidget(self.task_list)

        # Start WebSocket connection
        asyncio.ensure_future(self.start_websocket())

    async def start_websocket(self):
        """
        Connect to the server WebSocket and listen for real-time updates.
        """
        uri = "ws://127.0.0.1:8000/ws/ui"
        while True:
            try:
                async with websockets.connect(uri) as websocket:
                    self.status_label.setText("Connected to server.")
                    print("Connected to WebSocket.")  # Debug log
                    while True:
                        # Receive updates from the server
                        message = await websocket.recv()
                        # print(f"Received WebSocket message: {message}")  # Debug log

                        data = json.loads(message)
                        tasks = data.get("tasks", {})
                        self.update_task_list(tasks)
            except Exception as e:
                self.status_label.setText("Disconnected. Retrying...")
                print(f"WebSocket error: {e}")
                await asyncio.sleep(5)  # Retry after delay


    def update_task_list(self, tasks):
        """
        Dynamically update the QTreeWidget with the latest task data.
        """
        # print(f"Updating task list with {len(tasks)} tasks.")  # Debug log
    
        # Create a mapping of existing items by Task ID for easy lookup
        existing_items = {
            self.task_list.topLevelItem(i).text(0): self.task_list.topLevelItem(i)
            for i in range(self.task_list.topLevelItemCount())
        }

        for task_id, task in tasks.items():
            # print(f"Processing task: {task_id}, Data: {task}")  # Debug log

            # Extract task details with fallbacks for missing data
            scene_path = task.get("scene_path", "Unknown")
            frame = task.get("frame", 0)
            ROP_node = task.get("ROP_node", "Unknown")
            percent_complete = task.get("percent_complete", 0)
            elapsed_time = task.get("elapsed_time", "N/A")
            time_left = task.get("time_left", "N/A")
            status = task.get("status", "Unknown")

            if task_id in existing_items:
                # Update existing row
                item = existing_items[task_id]
                item.setText(4, status)
                item.setText(6, elapsed_time)
                item.setText(7, time_left)

                # Update progress bar
                progress_bar = self.task_list.itemWidget(item, 5)
                if progress_bar:
                    progress_bar.setValue(percent_complete)
                    if percent_complete == 100:
                        progress_bar.setStyleSheet("QProgressBar { background-color: green; }")
                        item.setText(4, "completed")  # Set status to completed
            else:
                # Add a new row for new tasks
                print(f"Adding new task: {task_id}")  # Debug log
                item = QTreeWidgetItem([
                    task_id, scene_path, str(frame), ROP_node,
                    status, "", elapsed_time, time_left
                ])
                self.task_list.addTopLevelItem(item)

                # Create and customize a QProgressBar
                progress_bar = QProgressBar()
                progress_bar.setRange(0, 100)
                progress_bar.setValue(percent_complete)
                progress_bar.setAlignment(Qt.AlignCenter)

                # Add the progress bar to the completion column
                self.task_list.setItemWidget(item, 5, progress_bar)



if __name__ == "__main__":
    app = QApplication([])

    # Set up asyncio event loop to work with PySide6
    loop = asyncio.get_event_loop()

    ui = ServerUI()
    asyncio.ensure_future(ui.start_websocket())

    app.exec()
