def get_azure_credentials():
    import os
    from dotenv import load_dotenv

    load_dotenv()

    azure_api_key = os.getenv("AZURE_API_KEY")
    azure_endpoint = os.getenv("AZURE_ENDPOINT")

    if not azure_api_key or not azure_endpoint:
        raise ValueError("Azure API key and endpoint must be set in the .env file.")

    return azure_api_key, azure_endpoint

def call_azure_service(api_url, headers, data):
    import requests

    response = requests.post(api_url, headers=headers, json=data)

    if response.status_code != 200:
        raise Exception(f"Error calling Azure service: {response.text}")

    return response.json()