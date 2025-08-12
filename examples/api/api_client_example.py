#!/usr/bin/env python3
"""
Advanced Research API Client Example

This script demonstrates how to interact with the Advanced Research API
using httpx for making HTTP requests. It shows various API endpoints
and how to handle responses.

Prerequisites:
1. Start the API server first by running: python api_demo.py
2. Install httpx: pip install httpx
"""

import asyncio
from typing import Dict, Any, List
import httpx

# API Configuration
API_BASE_URL = "http://127.0.0.1:8000"
TIMEOUT = 300.0  # 5 minutes timeout for research tasks


class AdvancedResearchAPIClient:
    """Client for interacting with the Advanced Research API."""

    def __init__(
        self, base_url: str = API_BASE_URL, timeout: float = TIMEOUT
    ):
        """
        Initialize the API client.

        Args:
            base_url: Base URL of the API server
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    async def health_check(self) -> Dict[str, Any]:
        """Check API health status."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(f"{self.base_url}/health")
            response.raise_for_status()
            return response.json()

    async def get_api_info(self) -> Dict[str, Any]:
        """Get basic API information."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(f"{self.base_url}/")
            response.raise_for_status()
            return response.json()

    async def get_system_info(self) -> Dict[str, Any]:
        """Get research system configuration information."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.base_url}/system/info"
            )
            response.raise_for_status()
            return response.json()

    async def get_output_methods(self) -> Dict[str, Any]:
        """Get available output formatting methods."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.base_url}/research/methods"
            )
            response.raise_for_status()
            return response.json()

    async def conduct_research(
        self,
        task: str,
        img: str = None,
        export_on: bool = False,
        output_type: str = "final",
    ) -> Dict[str, Any]:
        """
        Conduct a single research task.

        Args:
            task: The research question or task
            img: Optional image input (base64 or URL)
            export_on: Whether to export results to JSON file
            output_type: Output format type

        Returns:
            Research response containing results
        """
        payload = {
            "task": task,
            "export_on": export_on,
            "output_type": output_type,
        }
        if img:
            payload["img"] = img

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/research",
                json=payload,
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()
            return response.json()

    async def conduct_batch_research(
        self,
        tasks: List[str],
        export_on: bool = False,
        output_type: str = "final",
    ) -> Dict[str, Any]:
        """
        Conduct multiple research tasks in batch.

        Args:
            tasks: List of research questions or tasks
            export_on: Whether to export results to JSON files
            output_type: Output format type

        Returns:
            Batch research response containing all results
        """
        payload = {
            "tasks": tasks,
            "export_on": export_on,
            "output_type": output_type,
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/research/batch",
                json=payload,
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()
            return response.json()


def sync_request_example():
    """Example using synchronous httpx requests."""
    print("🔄 Synchronous API Example")
    print("=" * 50)

    try:
        # Health check
        with httpx.Client(timeout=TIMEOUT) as client:
            response = client.get(f"{API_BASE_URL}/health")
            response.raise_for_status()
            health = response.json()
            print(f"✅ API Health: {health['status']}")

            # Single research request
            research_payload = {
                "task": "What are the latest developments in renewable energy technology?",
                "export_on": False,
                "output_type": "final",
            }

            print("🔬 Conducting research...")
            response = client.post(
                f"{API_BASE_URL}/research",
                json=research_payload,
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()
            result = response.json()

            print(f"📋 Research ID: {result['id']}")
            print(f"❓ Task: {result['task']}")
            print(f"🕐 Timestamp: {result['timestamp']}")
            print(
                f"📄 Result: {result['result'][:200]}..."
            )  # First 200 chars

    except httpx.RequestError as e:
        print(f"❌ Request error: {e}")
    except httpx.HTTPStatusError as e:
        print(
            f"❌ HTTP error: {e.response.status_code} - {e.response.text}"
        )
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


async def async_examples():
    """Examples using the async API client."""
    print("\n🚀 Async API Client Examples")
    print("=" * 50)

    client = AdvancedResearchAPIClient()

    try:
        # 1. Health check
        print("1️⃣ Health Check")
        health = await client.health_check()
        print(f"   Status: {health['status']}")
        print(f"   Timestamp: {health['timestamp']}")

        # 2. Get API info
        print("\n2️⃣ API Information")
        api_info = await client.get_api_info()
        print(f"   Status: {api_info['status']}")
        print(f"   Version: {api_info['version']}")

        # 3. Get system info
        print("\n3️⃣ System Configuration")
        sys_info = await client.get_system_info()
        print(f"   Name: {sys_info['name']}")
        print(f"   Model: {sys_info['director_model_name']}")
        print(f"   Max Tokens: {sys_info['director_max_tokens']}")

        # 4. Get output methods
        print("\n4️⃣ Available Output Methods")
        methods = await client.get_output_methods()
        print(f"   Methods: {methods['output_methods']}")

        # 5. Single research task
        print("\n5️⃣ Single Research Task")
        research_task = "What are the most promising treatments for Alzheimer's disease in 2024?"
        print(f"   Task: {research_task}")

        result = await client.conduct_research(
            task=research_task, output_type="final"
        )

        print(f"   ID: {result['id']}")
        print(f"   Timestamp: {result['timestamp']}")
        print(f"   Result Preview: {result['result'][:150]}...")

        # 6. Batch research tasks
        print("\n6️⃣ Batch Research Tasks")
        batch_tasks = [
            "What are the latest AI safety research findings?",
            "How is quantum computing being applied in drug discovery?",
            "What are the current trends in sustainable transportation?",
        ]

        print(f"   Tasks: {len(batch_tasks)} research questions")
        batch_result = await client.conduct_batch_research(
            tasks=batch_tasks, output_type="final"
        )

        print(f"   Batch ID: {batch_result['batch_id']}")
        print(f"   Total Tasks: {batch_result['total_tasks']}")
        print(f"   Completed: {len(batch_result['results'])}")

        for i, res in enumerate(batch_result["results"], 1):
            print(f"     {i}. ID: {res['id']}")
            print(f"        Task: {res['task'][:60]}...")
            print(f"        Result: {res['result'][:100]}...")

    except httpx.RequestError as e:
        print(f"❌ Request error: {e}")
    except httpx.HTTPStatusError as e:
        print(f"❌ HTTP error: {e.response.status_code}")
        if hasattr(e.response, "json"):
            try:
                error_detail = e.response.json()
                print(
                    f"   Detail: {error_detail.get('detail', 'No details available')}"
                )
            except:
                print(f"   Response: {e.response.text}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


async def error_handling_example():
    """Example of proper error handling with the API."""
    print("\n🛡️ Error Handling Example")
    print("=" * 50)

    client = AdvancedResearchAPIClient()

    # Test with invalid endpoint
    try:
        async with httpx.AsyncClient(timeout=30) as http_client:
            response = await http_client.get(
                f"{API_BASE_URL}/invalid-endpoint"
            )
            response.raise_for_status()
    except httpx.HTTPStatusError as e:
        print(
            f"✅ Properly caught 404 error: {e.response.status_code}"
        )

    # Test with invalid request data
    try:
        await client.conduct_research(task="")  # Empty task
    except httpx.HTTPStatusError as e:
        print(
            f"✅ Properly caught validation error: {e.response.status_code}"
        )
    except Exception as e:
        print(f"✅ Caught other error: {type(e).__name__}: {e}")


def main():
    """Main function demonstrating various API usage patterns."""
    print("🔬 Advanced Research API Client Examples")
    print(
        "📡 Make sure the API server is running on http://127.0.0.1:8000"
    )
    print("🚀 Start it with: python api_demo.py")
    print("\n" + "=" * 60)

    # Run synchronous example
    sync_request_example()

    # Run async examples
    asyncio.run(async_examples())

    # Run error handling example
    asyncio.run(error_handling_example())

    print("\n" + "=" * 60)
    print("✅ API Client Examples Complete!")
    print(
        "💡 Try modifying the tasks and parameters to test different scenarios"
    )


if __name__ == "__main__":
    main()
