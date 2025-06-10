import os
from pathlib import Path

import google.generativeai as genai
from dotenv import load_dotenv


def main():
    """Check available Gemini models for the configured API key"""

    print("Checking available Gemini models...")

    # Update paths to look for .env in the correct locations
    # when running from the llm directory
    env_paths = [
        Path(".env"),  # Current directory
        Path("../.env"),  # Parent directory
        Path("../../.env"),  # Grandparent directory
        Path("../streamlit-app/.env"),  # streamlit-app directory
    ]

    env_loaded = False
    for env_path in env_paths:
        if env_path.exists():
            load_dotenv(dotenv_path=str(env_path))
            print(f"Loaded environment from {env_path}")
            env_loaded = True
            break

    if not env_loaded:
        print("Warning: No .env file found")

    # Get API key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY not found in environment variables")
        return

    print(f"API Key found: {api_key[:5]}...{api_key[-3:]}")

    try:
        genai.configure(api_key=api_key)
        models = genai.list_models()

        print("\nAll available models:")
        for model in models:
            print(f"- {model.name}")

        print("\nGemini models:")
        gemini_models = [model for model in models if "gemini" in model.name.lower()]
        if gemini_models:
            for model in gemini_models:
                print(f"- {model.name}")
                print(f"  Supported methods: {model.supported_generation_methods}")
        else:
            print("No Gemini models available for your API key.")

        # Try each model
        print("\nTesting models:")
        for model in gemini_models:
            print(f"\nTesting model: {model.name}")
            try:
                if "generateContent" in model.supported_generation_methods:
                    gen_model = genai.GenerativeModel(model.name)
                    response = gen_model.generate_content("Hello, who are you?")
                    print(f"Response: {response.text[:50]}...")
                else:
                    print("Model does not support generateContent")
            except Exception as e:
                print(f"Error with {model.name}: {e}")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
