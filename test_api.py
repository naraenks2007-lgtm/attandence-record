import os
import requests
import math
import json

# use env var if set, otherwise default to localhost (good for local dev)
BASE_URL = os.environ.get("BASE_URL", "http://127.0.0.1:5000")

def test_leave_submission():
    print("Testing leave submission against:", BASE_URL)

    payload = {
        "name": "Jane Doe",
        "roll_no": "CS-TEST-001",
        "date": "2023-12-01",
        "reason": "Medical"
    }

    try:
        response = requests.post(f"{BASE_URL}/api/leave", json=payload, timeout=10)
    except Exception as e:
        print("ERROR: Request failed:", e)
        return

    print("HTTP status:", response.status_code)
    # print raw response body for debugging
    print("Response body:", response.text)

    # Accept any 2xx success status
    if not (200 <= response.status_code < 300):
        print("FAIL: expected 2xx status code, got", response.status_code)
        return

    try:
        data = response.json()
    except json.JSONDecodeError:
        print("FAIL: response not JSON")
        return

    # --- ADJUST THESE LINES to match your API's actual JSON structure ---
    # example server JSON could be: {"success": True, "new_percentage": 97.3}
    # or: {"success": {"new_percentage": 97.3}} — update these lines to match.
    # I handle both possibilities below:
    if isinstance(data.get("success"), dict):
        new_percentage = data["success"].get("new_percentage")
    else:
        new_percentage = data.get("new_percentage") or (data.get("success") and data.get("success") if isinstance(data.get("success"), (int,float)) else None)

    if new_percentage is None:
        # try common alternative keys
        new_percentage = data.get("data", {}).get("new_percentage") or data.get("new_percentage")

    if new_percentage is None:
        print("FAIL: could not find 'new_percentage' in response JSON. Keys:", list(data.keys()))
        return

    expected = 97.0 + 0.3  # 97.3
    # use math.isclose with a small tolerance to avoid floating errors
    if math.isclose(float(new_percentage), expected, rel_tol=1e-9, abs_tol=1e-6):
        print("PASS: Percentage increased to", new_percentage)
    else:
        print(f"FAIL: Expected ~{expected}, got {new_percentage}")

if _name_ == "_main_":
    test_leave_submission()
