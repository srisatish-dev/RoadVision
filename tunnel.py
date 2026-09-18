"""
RoadVision — Persistent Tunnel Keeper
Keeps localtunnel alive by auto-restarting on disconnect.
Run:  python tunnel.py
"""
import subprocess
import time
import re

print("[*] Starting RoadVision tunnel keeper...")

while True:
    print("[*] Launching localtunnel...")
    try:
        result = subprocess.run(
            ["npx", "-y", "localtunnel", "--port", "5000"],
            capture_output=True, text=True, timeout=3600,
            shell=True
        )
        output = result.stdout + result.stderr
        url_match = re.search(r'https://[a-z0-9\-]+\.loca\.lt', output)
        if url_match:
            url = url_match.group(0)
            print(f"\n{'='*60}")
            print(f" RoadVision PUBLIC URL: {url}")
            print(f" Bypass password: 121.200.55.39")
            print(f"{'='*60}\n")
        else:
            print("[!] Output:", output[:200])
    except subprocess.TimeoutExpired:
        print("[!] Tunnel timed out, restarting...")
    except KeyboardInterrupt:
        print("\n[*] Tunnel stopped.")
        break
    except Exception as e:
        print(f"[!] Error: {e}")

    print("[*] Reconnecting in 3 seconds...")
    time.sleep(3)
