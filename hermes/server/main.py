import asyncio
from threading import Thread
from PySide6.QtWidgets import QApplication
from qasync import QEventLoop
import uvicorn

from hermes.server.server import app  # FastAPI app
from hermes.server.server_ui import ServerUI  # PySide6 Server UI

dark_theme = """
    QWidget {
        background-color: #121212;  /* Dark gray background */
        color: #ffffff;  /* White text */
    }

    QTreeWidget {
        background-color: #1e1e1e;  /* Slightly lighter gray for tree */
        alternate-background-color: #252526;
        color: #ffffff;
        border: 1px solid #3c3c3c;
    }

    QHeaderView::section {
        background-color: #2d2d2d;  /* Header background */
        color: #ffffff;  /* Header text */
        border: 1px solid #3c3c3c;
    }

    QProgressBar {
        border: 1px solid #3c3c3c;
        text-align: center;
        color: #ffffff;
        background: #2d2d2d;
    }

    QProgressBar::chunk {
        background-color: #4caf50;  /* Green progress bar */
    }

    QLabel {
        color: #ffffff;
    }

    QLineEdit, QTextEdit {
        background-color: #1e1e1e;
        color: #ffffff;
        border: 1px solid #3c3c3c;
    }

    QPushButton {
        background-color: #2d2d2d;
        color: #ffffff;
        border: 1px solid #3c3c3c;
        padding: 5px;
    }

    QPushButton:hover {
        background-color: #3e3e3e;
    }

    QPushButton:pressed {
        background-color: #4caf50;
        color: #000000;
    }
"""

def start_fastapi_server():
    """
    Start the FastAPI server in a separate thread.
    """
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")


def start_ui():
    """
    Start the PySide6 UI and integrate it with the asyncio event loop using qasync.
    """
    # Create the PySide6 application
    app = QApplication([])

    # Set the dark theme stylesheet
    app.setStyleSheet(dark_theme)
    
    # Create a qasync event loop for integration
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    # Instantiate and show the UI
    ui = ServerUI()
    ui.show()

    # Start the asyncio event loop
    with loop:
        loop.run_forever()


if __name__ == "__main__":
    # Start the FastAPI server in a separate thread
    fastapi_thread = Thread(target=start_fastapi_server, daemon=True)
    fastapi_thread.start()

    # Start the UI in the main thread
    start_ui()
