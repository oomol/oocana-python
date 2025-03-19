#!/usr/bin/env python3
import json
import os
import sys
import subprocess
from pathlib import Path

def create_executor():
    try:
        # Ensure working in the correct directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        executor_path = os.path.join(script_dir, "executor.sh")
        
        print(f"create python executor")
        if not os.path.exists(executor_path):
            print(f"Error: executor.sh not found at {executor_path}")
            return False
            
        process = subprocess.Popen([executor_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                    text=True, bufsize=1)
        
        # Print output as it comes in
        while True:
            stdout_line = process.stdout.readline()
            stderr_line = process.stderr.readline()
            
            if stdout_line:
            print(f"stdout: {stdout_line.strip()}")
            if stderr_line:
            print(f"stderr: {stderr_line.strip()}")
            
            # Check if process is still running
            if process.poll() is not None:
            # Get any remaining output
            for stdout_line in process.stdout:
                print(f"stdout: {stdout_line.strip()}")
            for stderr_line in process.stderr:
                print(f"stderr: {stderr_line.strip()}")
            break
        
        result = process
        if result.returncode != 0:
            print(f"exec error: Command exited with {result.returncode}")
            return False
        return True
    except Exception as e:
        print(f"exec error: {e}")
        return False

def main():
    layer_path = Path(os.path.expanduser("~")) / ".oomol-studio" / "oocana" / "layer.json"
    
    if layer_path.exists():
        with open(layer_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        print(f"Layer data: {json.dumps(data)}")
        rootfs = data.get("base_rootfs", [])
        
        if rootfs and "python_executor" in rootfs:
            print("Layer already contains python_executor")
            return
        
        create_executor()
        rootfs.append("python_executor")
        data["base_rootfs"] = rootfs
        print(f"Updated layer data: {json.dumps(data)}")
        
        with open(layer_path, "w", encoding="utf-8") as f:
            json.dump(data, f)
    else:
        print("Layer not found")
        create_executor()
        
        layer_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(layer_path, "w", encoding="utf-8") as f:
            json.dump({"base_rootfs": ["python_executor"]}, f)

if __name__ == "__main__":
    main()