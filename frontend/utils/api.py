
import requests

API_URL = "http://127.0.0.1:8000"


def check_backend():

    try:
        response = requests.get(
            f"{API_URL}/",
            timeout=5
        )

        return response.status_code == 200

    except requests.RequestException:
        return False


def fetch_datasets():

    try:
        response = requests.get(
            f"{API_URL}/api/data/datasets",
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        return data.get("datasets", [])

    except requests.RequestException as error:
        return None


def fetch_analytics(endpoint, dataset_id, **params):

    try:
        response = requests.get(
            f"{API_URL}/api/analytics/{endpoint}",
            params={
                "dataset_id": dataset_id,
                **params
            },
            timeout=60
        )

        response.raise_for_status()

        return response.json()

    except requests.RequestException:
        return None


def ask_agent(dataset_id, question):

    try:
        response = requests.post(
            f"{API_URL}/api/agents/ask",
            json={
                "dataset_id": dataset_id,
                "question": question
            },
            timeout=180
        )

        response.raise_for_status()

        return response.json()

    except requests.RequestException as error:
        return {
            "error": str(error),
            "details": (
                response.text
                if "response" in locals()
                else None
            )
        }


def download_report(dataset_id):

    try:
        response = requests.get(
            f"{API_URL}/api/reports/download",
            params={"dataset_id": dataset_id},
            timeout=180
        )

        response.raise_for_status()

        return response.content

    except requests.RequestException:
        return None
