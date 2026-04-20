import subprocess
import sys
import webbrowser
import time

streamlit_command = [
    sys.executable,
    "-m",
    "streamlit",
    "run",
    r"C:\macro_dashboard\app.py",
    "--server.headless=true"
]

# start streamlit server
process = subprocess.Popen(streamlit_command)

# wait for server to start
time.sleep(3)

# open browser
webbrowser.open("http://localhost:8501")

# keep script alive while streamlit runs
process.wait()