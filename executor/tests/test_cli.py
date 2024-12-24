import unittest
import subprocess
import time
import signal
import sys
import os.path


executor_parent_dir = os.path.dirname(os.path.dirname(__file__))


class TestExecutorCLI(unittest.TestCase):

    def test_http_server(self):
        cli_command = [sys.executable, "-u", "-m", "http.server", "8000"]
        process = subprocess.Popen(cli_command, cwd=executor_parent_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        code = process.poll()

        self.assertIsNone(code, "HTTP server failed to start or exit.")

    def test_cli(self):
        cli_command = [sys.executable, "-u", "-m", "python_executor.executor", "--session-id", "test-session", "--session-dir", "/tmp"]

        print("Starting CLI tool... in", executor_parent_dir)

        process = subprocess.Popen(cli_command, cwd=executor_parent_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        time.sleep(3)

        code = process.poll()

        self.assertIsNone(code, f"CLI tool failed to start or exit with code {code}")

        process.send_signal(signal.SIGINT)

        process.wait()
    
    def test_cli_fail(self):
        cli_command = [sys.executable, "-u", "-m", "python_executor.executor"]

        print("Starting CLI tool... in", executor_parent_dir)

        process = subprocess.Popen(cli_command, cwd=executor_parent_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        time.sleep(3)

        code = process.poll()

        self.assertIsNotNone(code, "CLI tool failed to exit.")
