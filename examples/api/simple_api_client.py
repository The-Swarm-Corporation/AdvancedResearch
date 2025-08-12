#!/usr/bin/env python3
"""
Simple Advanced Research API Client

A straightforward example showing how to call the Advanced Research API
using httpx with synchronous requests. Perfect for quick testing and
simple integrations.

Prerequisites:
1. Start the API server: python api_demo.py
2. Install httpx: pip install httpx
"""

import httpx
import json
from typing import Dict, Any

# API Configuration
API_BASE_URL = "http://127.0.0.1:8000"
TIMEOUT = 300.0  # 5 minutes


def call_api(
    method: str, endpoint: str, data: Dict = None
) -> Dict[str, Any]:
    """
    Make a simple API call with error handling.

    Args:
        method: HTTP method (GET, POST, etc.)
        endpoint: API endpoint (e.g., "/health")
        data: Request data for POST requests

    Returns:
        JSON response from the API
    """
    url = f"{API_BASE_URL}{endpoint}"

    try:
        with httpx.Client(timeout=TIMEOUT) as client:
            if method.upper() == "GET":
                response = client.get(url)
            elif method.upper() == "POST":
                response = client.post(
                    url,
                    json=data,
                    headers={"Content-Type": "application/json"},
                )
            else:
                raise ValueError(f"Unsupported method: {method}")

            response.raise_for_status()
            return response.json()

    except httpx.ConnectError:
        return None
    except httpx.HTTPStatusError:
        return None
    except Exception:
        return None


def check_api_health():
    """Check if the API is running and healthy."""
    result = call_api("GET", "/health")
    if result:
        return True
    return False


def get_system_info():
    """Get information about the research system."""
    result = call_api("GET", "/system/info")
    return result


def conduct_single_research():
    """Conduct a single research task."""
    task = "What are the latest breakthrough treatments for diabetes?"

    data = {"task": task, "export_on": False, "output_type": "final"}

    result = call_api("POST", "/research", data)
    if result:
        filename = f"research_result_{result['id'][:8]}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"Research Task: {result['task']}\n")
            f.write(f"Timestamp: {result['timestamp']}\n")
            f.write(f"Research ID: {result['id']}\n")
            f.write("\n" + "=" * 50 + "\n")
            f.write(result["result"])


def conduct_batch_research():
    """Conduct multiple research tasks in batch."""
    tasks = [
        "What are the most effective renewable energy technologies in 2024?",
        "How is artificial intelligence being used in healthcare?",
        "What are the latest developments in space exploration?",
    ]

    data = {
        "tasks": tasks,
        "export_on": False,
        "output_type": "final",
    }

    result = call_api("POST", "/research/batch", data)
    if result:
        filename = f"batch_results_{result['batch_id'][:8]}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)


def test_error_handling():
    """Test API error handling."""
    # Test invalid endpoint
    call_api("GET", "/invalid-endpoint")

    # Test invalid data
    call_api("POST", "/research", {"invalid": "data"})


def main():
    """Main function demonstrating API usage."""
    # 1. Check API health
    if not check_api_health():
        return

    # 2. Get system information
    get_system_info()

    # 3. Conduct single research
    conduct_single_research()

    # 4. Conduct batch research
    conduct_batch_research()

    # 5. Test error handling
    test_error_handling()


if __name__ == "__main__":
    main()
