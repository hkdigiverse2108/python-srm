import uvicorn
import sys
import os

# Define paths
root_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.join(root_dir, "backend")

# Ensure paths are in sys.path once and correctly
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# asyncio bug with ProactorEventLoop is no longer a concern in modern Python versions
# if sys.platform == 'win32':
#     import asyncio
#     asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from backend.app.core.config import HOST, PORT
import time

_display_host = "localhost" if HOST == "0.0.0.0" else HOST

def kill_process_on_port(port):
    """Automatically find and kill any process holding the specified port."""
    import subprocess
    import os
    import platform
    
    system = platform.system().lower()
    try:
        my_pid = os.getpid()
        pids = set()
        
        if system == "windows":
            # Find the PID(s) using the port on Windows
            cmd = f'netstat -ano | findstr :{port}'
            output = subprocess.check_output(cmd, shell=True).decode()
            
            for line in output.strip().split('\n'):
                line = line.strip()
                if not line: continue
                parts = line.split()
                if len(parts) >= 2 and f":{port}" in parts[1]:
                    pid = parts[-1]
                    if pid.isdigit() and int(pid) != 0 and int(pid) != my_pid:
                        pids.add(pid)
            
            if pids:
                for pid in pids:
                    print(f"[Cleanup] Terminating conflicting process PID: {pid} on port {port}...")
                    subprocess.run(f'taskkill /F /PID {pid}', shell=True, capture_output=True)
                time.sleep(1.0)
                print("[Cleanup] Port cleared.")
                
        else:
            # macOS / Linux (using lsof)
            try:
                # lsof -t gives only the PID
                cmd = f'lsof -t -iTCP:{port} -sTCP:LISTEN'
                output = subprocess.check_output(cmd, shell=True).decode()
                for line in output.strip().split('\n'):
                    pid = line.strip()
                    if pid.isdigit() and int(pid) != my_pid:
                        pids.add(pid)
                
                if pids:
                    for pid in pids:
                        print(f"[Cleanup] Terminating conflicting process PID: {pid} on port {port}...")
                        subprocess.run(f'kill -9 {pid}', shell=True, capture_output=True)
                    time.sleep(1.0)
                    print("[Cleanup] Port cleared.")
            except subprocess.CalledProcessError:
                # lsof returns exit code 1 if no process found
                pass
                
    except Exception as e:
        print(f"[Cleanup] Warning: Failed to clear port {port}: {e}")


if __name__ == "__main__":
    print("--------------------------------------------------")
    print(f"-> Frontend UI : http://{_display_host}:{PORT}/frontend/template/index.html")
    print(f"-> Backend API : http://{_display_host}:{PORT}/docs")
    print("==================================================")
    
    print("Attempting to start uvicorn...")
    try:
        # Clear the port before starting
        kill_process_on_port(PORT)
        
        # Import the app here AFTER sys.path adjustment
        from backend.app.main import app
        
        # Run the FastAPI server directly with the app object
        # This is more reliable on Windows than the string import "module:app"
        uvicorn.run(
            app, 
            host=HOST, 
            port=PORT,
            reload=False,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n[Shutdown] Server stopped by user.")
    except Exception as e:
        print(f"Startup EXCEPTION: {e}")
        import traceback
        traceback.print_exc()
