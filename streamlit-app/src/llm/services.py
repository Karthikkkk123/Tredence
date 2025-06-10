import os
from abc import ABC, abstractmethod
from typing import Dict, List

import google.generativeai as genai

from .utils import find_and_load_env_file, get_available_models

find_and_load_env_file()


class LLMService(ABC):
    """Abstract base class for LLM services"""

    def __init__(self):
        self.initialized = False

    @abstractmethod
    def generate_text(self, prompt: str, max_tokens: int = 1024, **kwargs) -> str:
        """Generate text using the LLM model"""
        pass

    def explain_concept(self, concept: str) -> str:
        """Explain an educational concept"""
        prompt = f"""
        Explain the following educational concept in simple terms that a student could understand.
        Include examples and key points:

        Concept: {concept}
        """
        return self.generate_text(prompt)

    def create_practice_questions(
        self, topic: str, difficulty: str, count: int = 3
    ) -> List[Dict]:
        """Generate practice questions on a given topic"""
        if not self.initialized:
            return [{"question": "LLM not initialized. Check your API key."}]

        prompt = f"""
        Create {count} {difficulty}-level practice questions about "{topic}".
        For each question, provide:
        1. The question text
        2. Multiple choice options (if applicable)
        3. The correct answer
        4. A brief explanation of the answer

        Format your response as JSON with this structure:
        [
          {{
            "text": "Question text here",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "answer": "The correct answer",
            "explanation": "Explanation of why this is the correct answer"
          }},
          // more questions...
        ]
        """

        try:
            import json
            import re  # type: ignore

            response_text = self.generate_text(prompt)

            # Try to extract JSON from the response
            json_match = re.search(r"\[.*\]", response_text, re.DOTALL)
            if json_match:
                questions_json = json_match.group(0)
                questions = json.loads(questions_json)
                if isinstance(questions, list) and len(questions) > 0:
                    return questions[
                        :count
                    ]  # Ensure we only return the requested number
        except Exception as e:
            print(f"Error parsing practice questions: {e}")

        # Fallback to text parsing if JSON extraction fails
        return self._parse_questions_from_text(self.generate_text(prompt), count)

    def _parse_questions_from_text(self, text: str, count: int) -> List[Dict]:
        """Parse questions from text format if JSON parsing fails"""
        questions = []
        current_question = {}
        lines = text.split("\n")

        for i, line in enumerate(lines):
            if (
                line.strip().startswith(("Question", "Q", "1.", "2.", "3.", "#"))
                and i > 0
            ):
                if current_question:  # type: ignore
                    questions.append(current_question)
                    current_question = {}

            if current_question:
                if "text" not in current_question:
                    current_question["text"] = line.strip()
                elif "options" not in current_question and line.strip().startswith(
                    ("A.", "B.", "1.", "*", "-")
                ):
                    current_question["options"] = []
                    current_question["options"].append(line.strip())
                elif "options" in current_question and line.strip().startswith(
                    ("A.", "B.", "C.", "D.", "1.", "2.", "*", "-")
                ):
                    current_question["options"].append(line.strip())
                elif "answer" not in current_question and (
                    "answer" in line.lower() or "correct" in line.lower()
                ):
                    current_question["answer"] = line.strip()
                elif "explanation" not in current_question and (
                    "explanation" in line.lower() or "reason" in line.lower()
                ):
                    current_question["explanation"] = line.strip()
                elif "explanation" in current_question:
                    current_question["explanation"] += " " + line.strip()
            else:
                current_question["text"] = line.strip()

        if current_question:
            questions.append(current_question)

        # Add placeholder questions if needed
        while len(questions) < count:
            questions.append(
                {
                    "text": f"Additional question {len(questions) + 1}",
                    "options": ["Option A", "Option B", "Option C"],
                    "answer": "Option A",
                    "explanation": "This is a placeholder question.",
                }
            )

        return questions[:count]

    def generate_learning_path(self, topic: str, level: str) -> Dict:
        """Generate a personalized learning path for a given topic"""
        if not self.initialized:
            return {"error": "LLM not initialized. Check your API key."}

        prompt = f"""
        Create a structured learning path for someone wanting to learn about "{topic}" at a {level} level.

        Include:
        1. A sequence of 4-6 topics to learn, in order
        2. For each topic, suggest 1-2 resources (books, courses, websites)
        3. Estimate time needed for each topic
        4. Suggest a small project or exercise to practice each topic

        Format the response as a structured, markdown formatted learning plan.
        """

        response_text = self.generate_text(prompt)

        # Return the raw text for now, in a real application you might want to parse this
        return {
            "topic": topic,
            "level": level,
            "path": response_text,
            "estimated_total_hours": 20,  # Placeholder
            "topics_count": 5,  # Placeholder
        }

    def generate_quiz(
        self, topic: str, difficulty: str, num_questions: int = 5
    ) -> Dict:
        """Generate an interactive quiz on a specific topic"""
        return {
            "topic": topic,
            "questions": self.create_practice_questions(
                topic, difficulty, num_questions
            ),
        }

    def suggest_resources(
        self, topic: str, format_type: str = "all", max_results: int = 5
    ) -> List[Dict]:
        """Suggest learning resources for a given topic"""
        if not self.initialized:
            return [{"error": "LLM not initialized. Check your API key."}]

        prompt = f"""
        Suggest {max_results} high-quality {format_type} resources for learning about "{topic}".

        For each resource, provide:
        1. Title
        2. Author/Creator
        3. Brief description (1-2 sentences)
        4. Difficulty level (Beginner, Intermediate, Advanced)
        5. Link or platform (where applicable)

        Format your response as JSON with this structure:
        [
          {{
            "title": "Resource title",
            "author": "Resource author or creator",
            "description": "Brief description",
            "level": "Beginner/Intermediate/Advanced",
            "link": "URL or platform name"
          }},
          // more resources...
        ]
        """

        try:
            import json
            import re

            response_text = self.generate_text(prompt)

            # Try to extract JSON from the response
            json_match = re.search(r"\[.*\]", response_text, re.DOTALL)
            if json_match:
                resources_json = json_match.group(0)
                resources = json.loads(resources_json)
                if isinstance(resources, list) and len(resources) > 0:
                    return resources[:max_results]
        except Exception as e:
            print(f"Error parsing resources: {e}")

        # Fallback with placeholder resources
        return [
            {
                "title": "Introduction to " + topic,
                "author": "Various Authors",
                "description": f"A comprehensive introduction to {topic}.",
                "level": "Beginner",
                "link": "www.example.com",
            },
            {
                "title": f"Advanced {topic} Techniques",
                "author": "Expert Author",
                "description": f"In-depth coverage of advanced {topic} concepts.",
                "level": "Advanced",
                "link": "www.example.com/advanced",
            },
        ]


class GeminiService(LLMService):
    """Service to interact with Google's Gemini API"""

    def __init__(self):
        super().__init__()
        self.api_key = os.getenv("GEMINI_API_KEY")

        # Set default model to Gemini 2.0 Flash
        self.model_name = "gemini-2.0-flash"
        self.verbose = False

        # Fallback models in order of preference
        self.fallback_models = [
            "gemini-2.0-flash",
            "gemini-1.0-pro",
            "gemini-1.5-flash",
            "gemini-1.0-flash",
            "gemini-1.5-pro",
        ]

        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)

                # Get available models
                available_models = get_available_models(verbose=self.verbose)

                if available_models:
                    # Try to use the preferred model if available
                    if self.model_name not in available_models:
                        original_model = self.model_name
                        for fallback in self.fallback_models:
                            if fallback in available_models:
                                self.model_name = fallback
                                print(
                                    f"Using {self.model_name} instead of {original_model}"
                                )
                                break
                else:
                    print("No available Gemini models found for content generation")

                # Initialize the model
                self.model = genai.GenerativeModel(self.model_name)
                self.initialized = True
                print(f"Gemini service initialized with model: {self.model_name}")

                # Test the model silently
                try:
                    self.model.generate_content("Hello")
                except Exception as e:
                    print(f"Warning: Test message failed: {e}")

            except Exception as e:
                print(f"Error initializing Gemini with model {self.model_name}: {e}")
                self.initialized = False

    def generate_text(self, prompt: str, max_tokens: int = 1024, **kwargs) -> str:
        """Generate text using Gemini model"""
        if not self.initialized:
            return "Gemini API not initialized. Check your API key."

        try:
            generation_config = {
                "max_output_tokens": max_tokens,
                "temperature": kwargs.get(
                    "temperature", 0.1
                ),  # Lower temperature for more deterministic responses
                "top_p": kwargs.get("top_p", 0.95),
                "top_k": kwargs.get("top_k", 40),
            }

            # If the prompt asks for JSON output, use specific parameters better suited for structured output
            if "json" in prompt.lower() or "{" in prompt:
                generation_config["temperature"] = 0.1
                generation_config["top_p"] = 1.0
                # Add a system instruction to encourage valid JSON output
                system_instruction = "You are a helpful AI assistant that generates valid, well-formatted JSON output with no additional text."
                response = self.model.generate_content(
                    [system_instruction, prompt],
                    generation_config=generation_config,  # type: ignore
                )
            else:
                response = self.model.generate_content(
                    prompt,
                    generation_config=generation_config,  # type: ignore
                )

            return response.text
        except Exception as e:
            print(f"Error generating text with Gemini: {e}")
            return f"Error generating response: {str(e)}"


class MockLLMService(LLMService):
    """Mock LLM service for testing without API keys"""

    def __init__(self):
        super().__init__()
        self.initialized = True

    def generate_text(self, prompt: str, max_tokens: int = 1024, **kwargs) -> str:
        """Generate mock text responses"""
        if "concept" in prompt.lower():
            return f"This is a mock explanation of the concept in the prompt: {prompt[-100:]}"
        elif "questions" in prompt.lower():
            return """
            Question 1: What is the capital of France?
            A. London
            B. Paris
            C. Berlin
            D. Madrid

            Answer: B. Paris

            Explanation: Paris is the capital and largest city of France.

            Question 2: What is 2+2?
            A. 3
            B. 4
            C. 5
            D. 6

            Answer: B. 4

            Explanation: Basic arithmetic shows that 2+2=4.
            """
        elif "learning path" in prompt.lower():
            return """
            # Learning Path

            ## 1. Fundamentals (2 weeks)
            - Resource: "Introduction to the Topic" by Author Name
            - Project: Build a simple application

            ## 2. Intermediate Concepts (3 weeks)
            - Resource: Online course at example.com
            - Project: Extend your application with advanced features

            ## 3. Advanced Topics (4 weeks)
            - Resource: "Expert Guide" by Another Author
            - Project: Build a complex system using all concepts
            """
        else:
            return "This is a mock response from the AI model."


# Factory function to get LLM services
def get_llm_service(service_name: str = "gemini") -> LLMService:
    """Factory function to get the appropriate LLM service"""
    if service_name.lower() == "gemini":
        service = GeminiService()
        if not service.initialized:
            print("Warning: Gemini not initialized, falling back to mock service")
            return MockLLMService()
        return service
    elif service_name.lower() == "mock":
        return MockLLMService()
    else:
        print(f"LLM service {service_name} not supported, falling back to mock service")
        return MockLLMService()


# Registry of available LLM services
AVAILABLE_LLM_SERVICES = {
    "gemini": {
        "name": "Google Gemini",
        "description": "Google's Gemini 2.0 Flash model (with fallback options)",
    },
    "mock": {
        "name": "Mock LLM",
        "description": "Mock LLM for testing without API keys",
    },
    # Add new services here as they become available
    # "openai": {"name": "OpenAI GPT", "description": "OpenAI's GPT language models"}
}


def list_available_services() -> List[Dict[str, str]]:
    """List all available LLM services"""
    return [{"id": key, **value} for key, value in AVAILABLE_LLM_SERVICES.items()]
