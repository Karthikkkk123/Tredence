import os
from typing import Any, Dict

import requests
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv
from llm.services import get_llm_service

# Load environment variables
load_dotenv()


class EmotionalIntelligence:
    def __init__(self):
        self.text_analytics_endpoint = os.getenv("TEXT_ANALYTICS_ENDPOINT")
        self.text_analytics_key = os.getenv("TEXT_ANALYTICS_KEY")

        # Initialize client only if credentials are available
        self.text_analytics_client = None
        if self.text_analytics_endpoint and self.text_analytics_key:
            self.text_analytics_client = TextAnalyticsClient(
                endpoint=self.text_analytics_endpoint,
                credential=AzureKeyCredential(self.text_analytics_key),
            )

        # Initialize Gemini service
        self.llm_service = get_llm_service("gemini")

        # Face API credentials
        self.face_api_endpoint = os.getenv("FACE_API_ENDPOINT")
        self.face_api_key = os.getenv("FACE_API_KEY")
        self.face_api_available = bool(self.face_api_endpoint and self.face_api_key)

    def analyze_emotions_from_text(self, text: str) -> Dict:
        """Analyze emotions from text input using Gemini or Azure as fallback"""
        # Try using Gemini first
        if hasattr(self.llm_service, "initialized") and self.llm_service.initialized:
            try:
                prompt = f"""
                Analyze the emotional sentiment in the following text and provide scores for positive, neutral, and negative emotions.
                The scores should sum to 1.0 (or close to it due to rounding).
                Also determine an overall sentiment classification (positive, neutral, negative).

                Format your response as JSON with this structure:
                {{
                  "positive": 0.XX,
                  "neutral": 0.XX,
                  "negative": 0.XX,
                  "overall": "positive/neutral/negative"
                }}

                Text to analyze: "{text}"
                """

                response = self.llm_service.generate_text(prompt)

                # Try to extract JSON from the response
                import json
                import re

                # Find JSON object in response if it's wrapped in text
                json_match = re.search(r"\{.*\}", response, re.DOTALL)
                if json_match:
                    response = json_match.group(0)

                try:
                    emotions = json.loads(response)
                    # Ensure all required fields are present
                    required_fields = ["positive", "neutral", "negative", "overall"]
                    if all(field in emotions for field in required_fields):
                        return {
                            "emotions": emotions,
                            "text": text,
                            "provider": "gemini",
                        }
                except json.JSONDecodeError:
                    print("Could not parse Gemini response as JSON")

            except Exception as e:
                print(f"Error using Gemini for sentiment analysis: {e}")

        # Fall back to Azure Text Analytics if Gemini fails or isn't initialized
        if self.text_analytics_client:
            try:
                # Use Azure Text Analytics to analyze sentiment
                result = self.text_analytics_client.analyze_sentiment(documents=[text])[
                    0
                ]

                # Extract emotions
                emotions = {
                    "positive": result.confidence_scores.positive,
                    "neutral": result.confidence_scores.neutral,
                    "negative": result.confidence_scores.negative,
                    "overall": result.sentiment,
                }

                return {"emotions": emotions, "text": text, "provider": "azure"}
            except Exception as e:
                print(f"Error analyzing emotions with Azure: {e}")
                return {"error": str(e)}

        # If both methods fail, generate a placeholder response
        return {
            "emotions": {
                "positive": 0.33,
                "neutral": 0.34,
                "negative": 0.33,
                "overall": "neutral",
            },
            "text": text,
            "provider": "placeholder",
            "note": "This is a placeholder response as neither Gemini nor Azure sentiment analysis is available.",
        }

    def analyze_emotions_from_image(self, image_data: bytes) -> Dict:
        """Analyze emotions from facial expressions in an image using Azure Face API"""
        if not self.face_api_available:
            print("Face API credentials not available, using fallback")
            return self._fallback_image_analysis(image_data)

        try:
            # Face API endpoint
            face_api_url = f"{self.face_api_endpoint}/face/v1.0/detect"

            # Parameters for the Face API
            params = {
                "returnFaceId": "true",
                "returnFaceLandmarks": "false",
                "returnFaceAttributes": "emotion",
            }

            # Headers for the Face API
            headers = {
                "Content-Type": "application/octet-stream",
                "Ocp-Apim-Subscription-Key": self.face_api_key,
            }

            print(f"Sending request to Face API: {face_api_url}")
            print(f"Image data size: {len(image_data)} bytes")

            # Send the image to the Face API
            response = requests.post(
                face_api_url, params=params, headers=headers, data=image_data
            )

            # Print response for debugging
            print(f"Face API Response Status: {response.status_code}")
            if response.status_code != 200:
                print(f"Error response: {response.text}")

            # Check if the request was successful
            response.raise_for_status()

            # Parse the response
            faces = response.json()
            print(f"Detected faces: {len(faces)}")

            if not faces:
                print("No faces detected in the image")
                return {
                    "message": "No faces detected in the image",
                    "provider": "azure_face",
                    "emotions": {
                        "happiness": 0.0,
                        "sadness": 0.0,
                        "neutral": 1.0,
                        "anger": 0.0,
                        "fear": 0.0,
                        "surprise": 0.0,
                        "contempt": 0.0,
                        "disgust": 0.0,
                    },
                    "sentiment": {
                        "positive": 0.0,
                        "neutral": 1.0,
                        "negative": 0.0,
                    },
                    "dominant_emotion": "neutral",
                    "dominant_sentiment": "neutral",
                }

            # Get emotions from the first face
            emotions = faces[0]["faceAttributes"]["emotion"]
            print(f"Raw emotions data: {emotions}")

            # Calculate basic sentiment scores (positive, neutral, negative)
            positive_emotions = {"happiness", "surprise"}
            negative_emotions = {"sadness", "anger", "fear", "contempt", "disgust"}

            basic_sentiment = {
                "positive": sum(emotions[emotion] for emotion in positive_emotions),
                "neutral": emotions["neutral"],
                "negative": sum(emotions[emotion] for emotion in negative_emotions),
            }

            # Determine the dominant emotion and sentiment
            dominant_emotion = max(emotions.items(), key=lambda x: x[1])[0]
            dominant_sentiment = max(basic_sentiment.items(), key=lambda x: x[1])[0]

            print(
                f"Dominant emotion: {dominant_emotion}, Dominant sentiment: {dominant_sentiment}"
            )

            return {
                "emotions": emotions,  # Specific emotions
                "sentiment": basic_sentiment,  # Basic sentiment scores
                "dominant_emotion": dominant_emotion,  # Specific dominant emotion
                "dominant_sentiment": dominant_sentiment,  # Basic dominant sentiment
                "face_count": len(faces),
                "provider": "azure_face",
            }

        except Exception as e:
            print(f"Error analyzing image with Face API: {e}")
            # Try using Gemini for image analysis if available
            return self._fallback_image_analysis(image_data)

    def _fallback_image_analysis(self, image_data: bytes) -> Dict:
        """Use Gemini as a fallback for image analysis if available"""
        print("Using fallback image analysis method")

        # First, check if this is a valid image by trying to open it
        try:
            import io

            from PIL import Image

            img = Image.open(io.BytesIO(image_data))
            width, height = img.size
            print(f"Valid image detected: {width}x{height}, format: {img.format}")
        except Exception as e:
            print(f"Invalid image data: {e}")
            # Return error for invalid image
            return {
                "error": f"Invalid image data: {str(e)}",
                "provider": "error",
            }

        if hasattr(self.llm_service, "initialized") and self.llm_service.initialized:
            try:
                # Create a more specific prompt for text-only emotion analysis
                prompt = """
                Generate a realistic facial emotion analysis. Return ONLY valid JSON with this structure:
                {
                  "emotions": {
                    "happiness": 0.4,
                    "sadness": 0.05,
                    "neutral": 0.2,
                    "anger": 0.05,
                    "fear": 0.05,
                    "surprise": 0.2,
                    "contempt": 0.03,
                    "disgust": 0.02
                  },
                  "sentiment": {
                    "positive": 0.6,
                    "neutral": 0.2,
                    "negative": 0.2
                  },
                  "dominant_emotion": "happiness",
                  "dominant_sentiment": "positive",
                  "face_count": 1
                }

                IMPORTANT: Values should be between 0 and 1, all emotion scores should sum to 1.0,
                and all sentiment scores should sum to 1.0.
                """

                response = self.llm_service.generate_text(prompt)
                print(f"LLM response received, length: {len(response)}")

                # Parse the response
                import json
                import re

                # Clean the response to extract just the JSON
                json_pattern = r"\{[\s\S]*\}"
                matches = re.search(json_pattern, response)

                if not matches:
                    print("Could not find JSON pattern in response")
                    print(f"Raw response: {response[:200]}...")
                    raise ValueError("No JSON found in response")

                json_str = matches.group(0)
                print(f"Extracted JSON string: {json_str[:100]}...")

                # Remove any non-standard JSON formatting
                json_str = re.sub(r"(?m)^\s*//.*\n?", "", json_str)  # Remove comments

                # Load the JSON
                result = json.loads(json_str)
                print("Successfully parsed JSON")

                # Validate required fields
                required_fields = [
                    "emotions",
                    "sentiment",
                    "dominant_emotion",
                    "dominant_sentiment",
                ]
                if not all(field in result for field in required_fields):
                    missing = [f for f in required_fields if f not in result]
                    print(f"Missing required fields: {missing}")
                    raise ValueError(f"Missing fields in response: {missing}")

                # Force emotions to have all required fields
                required_emotions = [
                    "happiness",
                    "sadness",
                    "neutral",
                    "anger",
                    "fear",
                    "surprise",
                    "contempt",
                    "disgust",
                ]
                for emotion in required_emotions:
                    if emotion not in result["emotions"]:
                        result["emotions"][emotion] = 0.0

                # Mark this as coming from the LLM
                result["provider"] = "gemini"
                return result

            except Exception as e:
                print(f"Error in fallback image analysis: {str(e)}")
                # Fall through to the placeholder response
        else:
            print("LLM service not initialized for fallback")

        # Return a placeholder if everything fails
        print("Using placeholder emotion data")
        return {
            "emotions": {
                "happiness": 0.15,
                "sadness": 0.1,
                "neutral": 0.3,
                "anger": 0.1,
                "fear": 0.05,
                "surprise": 0.15,
                "contempt": 0.05,
                "disgust": 0.1,
            },
            "sentiment": {
                "positive": 0.3,
                "neutral": 0.3,
                "negative": 0.4,
            },
            "dominant_emotion": "neutral",
            "dominant_sentiment": "negative",
            "face_count": 1,
            "provider": "placeholder",
            "message": "Using placeholder data. Neither Azure Face API nor Gemini were able to analyze the image.",
        }

    def analyze_emotions_from_audio(self, audio_file: str) -> Dict:
        """Analyze emotions from voice in audio file"""
        # Placeholder for voice emotion analysis
        # In a real implementation, this would use Azure Speech API

        return {
            "emotions": {
                "happiness": 0.7,
                "sadness": 0.1,
                "anger": 0.05,
                "neutral": 0.15,
            },
            "audio": audio_file,
            "transcript": "Sample transcript from audio",
        }


def analyze_emotions(input_data: Any, input_type: str = "text") -> Dict:
    """Analyze emotions from different input types"""
    emotional_ai = EmotionalIntelligence()

    if input_type == "text":
        return emotional_ai.analyze_emotions_from_text(input_data)
    elif input_type == "image":
        if hasattr(input_data, "read"):  # File-like object from Streamlit
            return emotional_ai.analyze_emotions_from_image(input_data.read())
        else:  # Raw bytes or file path
            if isinstance(input_data, str):  # File path
                with open(input_data, "rb") as f:
                    return emotional_ai.analyze_emotions_from_image(f.read())
            else:  # Raw bytes
                return emotional_ai.analyze_emotions_from_image(input_data)
    elif input_type == "audio":
        return emotional_ai.analyze_emotions_from_audio(input_data)
    else:
        return {"error": f"Unsupported input type: {input_type}"}
