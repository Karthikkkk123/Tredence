"""Tool to check available Gemini models."""

import os
import sys
from pathlib import Path
from typing import Optional, List

import google.generativeai as genai

# Add parent directory to path to allow importing utils
sys.path.append(str(Path(__file__).parent))
from utils import find_and_load_env_file


def clean_model_name(model_name: str) -> str:
    """Remove 'models/' prefix from model names if present"""
    if model_name.startswith("models/"):
        return model_name[len("models/") :]
    return model_name


def check_gemini_models(verbose: bool = True, test_models: bool = True) -> List[str]:
    """Check available Gemini models for the configured API key"""

    print("Checking available Gemini models...")

    # Find and load the nearest .env file
    env_path = find_and_load_env_file()
    if env_path:
        print(f"Loaded environment from {env_path}")
    else:
        print("Warning: No .env file found")

    # Get API key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY not found in environment variables")
        return []

    print(f"API Key found: {api_key[:5]}...{api_key[-3:]}")

    try:
        genai.configure(api_key=api_key)
        models = genai.list_models()

        if verbose:
            print("\nAll available models:")
            for model in models:
                clean_name = clean_model_name(model.name)
                print(f"- {clean_name}")

        print("\nGemini models:")
        gemini_models = [model for model in models if "gemini" in model.name.lower()]
        content_gen_models = []

        if gemini_models:
            for model in gemini_models:
                supported_methods = model.supported_generation_methods
                clean_name = clean_model_name(model.name)
                print(f"- {clean_name}")
                print(f"  Supported methods: {supported_methods}")

                if "generateContent" in supported_methods:
                    content_gen_models.append(clean_name)

            print("\nModels supporting content generation:")
            for model_name in content_gen_models:
                print(f"- {model_name}")
        else:
            print("No Gemini models available for your API key.")

        # Try each model
        if test_models and content_gen_models:
            print("\nTesting models:")
            for model_name in content_gen_models:
                print(f"\nTesting model: {model_name}")
                try:
                    gen_model = genai.GenerativeModel(model_name)
                    response = gen_model.generate_content("Hello, who are you?")
                    print(f"Response: {response.text[:50]}...")
                except Exception as e:
                    print(f"Error with {model_name}: {e}")

        # Return the models names that can be used for generation
        return content_gen_models

    except Exception as e:
        print(f"Error: {e}")
        return []


def get_recommended_model() -> Optional[str]:
    """Get the recommended model for use with the app"""
    models = check_gemini_models(verbose=False, test_models=False)

    # Preferred models in order of preference
    preferred_models = [
        "gemini-2.0-flash",  # Primary choice
        "gemini-1.5-pro",
        "gemini-1.0-pro",
        "gemini-1.5-flash",
        "gemini-1.0-flash",
    ]

    if models:
        for model in preferred_models:
            if model in models:
                print(f"Recommended model: {model}")
                return model

    # If we didn't find any of the preferred models, return the first available
    if models:
        print(f"Using available model: {models[0]}")
        return models[0]

    print("No compatible models found")
    return None


if __name__ == "__main__":
    print("Gemini Model Checker")
    print("===================")
    print("1. List available models")
    print("2. Get recommended model")
    print("3. Run full test")

    choice = input("\nEnter your choice (1-3): ")

    if choice == "1":
        check_gemini_models(test_models=False)
    elif choice == "2":
        get_recommended_model()
    else:
        check_gemini_models(test_models=True)
