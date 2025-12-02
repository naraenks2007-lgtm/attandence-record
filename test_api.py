import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_leave_submission():
    print("Testing Leave Submission...")
    payload = {
        "name": "Jane Doe",
        "roll_no": "CS-TEST-001",
        "date": "2023-12-01",
        "reason": "Medical"
    }
    try:
        response = requests.post(f"{BASE_URL}/api/leave", json=payload)
        if response.status_code == 200:
            data = response.json()
            print(f"Success: {data}")
            if data['new_percentage'] == 97.0:
                print("PASS: Percentage dropped to 97.0%")
            else:
                print(f"FAIL: Expected 97.0%, got {data['new_percentage']}%")
        else:
            print(f"FAIL: Status Code {response.status_code}, {response.text}")
    except Exception as e:
        print(f"FAIL: Exception {e}")

def test_attendance_mark():
    print("\nTesting Attendance Mark...")
    payload = {
        "roll_no": "CS-TEST-001"
    }
    try:
        response = requests.post(f"{BASE_URL}/api/attend", json=payload)
        if response.status_code == 200:
            data = response.json()
            print(f"Success: {data}")
            # 97.0 + 0.3 = 97.3
            if data['new_percentage'] == 97.3:
                print("PASS: Percentage increased to 97.3%")
            else:
                print(f"FAIL: Expected 97.3%, got {data['new_percentage']}%")
        else:
            print(f"FAIL: Status Code {response.status_code}, {response.text}")
    except Exception as e:
        print(f"FAIL: Exception {e}")

if __name__ == "__main__":
    test_leave_submission()
    test_attendance_mark()
