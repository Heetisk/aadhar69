import requests
import time

API_BASE_URL = "http://127.0.0.1:8000"

def test_sync_local(dataset_type):
    print(f"\nTesting sync-local for: {dataset_type}")
    try:
        # Clear existing data first
        requests.delete(f"{API_BASE_URL}/clear-data", params={"dataset_type": dataset_type})
        
        # Sync local data
        response = requests.post(f"{API_BASE_URL}/sync-local", params={"dataset_type": dataset_type})
        print(f"Sync Result: {response.json()}")
        
        # Check summary
        summary = requests.get(f"{API_BASE_URL}/summary", params={"dataset_type": dataset_type}).json()
        print(f"Summary: {summary}")
        
    except Exception as e:
        print(f"Error testing {dataset_type}: {e}")

if __name__ == "__main__":
    datasets = ["enrolment", "demographic", "biometric"]
    for ds in datasets:
        test_sync_local(ds)
