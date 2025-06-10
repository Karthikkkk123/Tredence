"""Utility functions for LLM module."""

import os
from pathlib import Path
from typing import List, Optional

from dotenv import load_dotenv


def find_and_load_env_file() -> Optional[Path]:
    """Find and load the nearest .env file."""
    env_paths = [
        Path(".env"),  # Current directory
        Path("../.env"),  # Parent directory
        Path("../../.env"),  # Grandparent directory
        Path("../../../.env"),  # Great-grandparent directory
        Path("../streamlit-app/.env"),  # streamlit-app directory
    ]

    for env_path in env_paths:
        if env_path.exists():
            load_dotenv(dotenv_path=str(env_path.absolute()))
            return env_path.absolute()

    return None


def clean_model_name(model_name: str) -> str:
    """Remove 'models/' prefix from model names if present"""
    if model_name.startswith("models/"):
        return model_name[len("models/") :]
    return model_name


def get_available_models(verbose: bool = False) -> List[str]:
    """Get a list of available Gemini models."""
    try:
        import google.generativeai as genai

        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            if verbose:
                print("No GEMINI_API_KEY found in environment variables.")
            return []

        genai.configure(api_key=api_key)
        models = genai.list_models()

        available_models = []
        for model in models:
            if "gemini" in model.name.lower():
                if "generateContent" in model.supported_generation_methods:
                    # Clean model name by removing 'models/' prefix if present
                    clean_name = clean_model_name(model.name)
                    available_models.append(clean_name)

        return available_models

    except Exception as e:
        if verbose:
            print(f"Error listing models: {e}")
        return []
