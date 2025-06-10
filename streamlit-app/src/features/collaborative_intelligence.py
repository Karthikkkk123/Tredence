import os
from typing import Dict, List

# Azure imports
from azure.ai.textanalytics import TextAnalyticsClient
from azure.cognitiveservices.personalizer.models import RankableAction, RankRequest
from azure.communication.chat import ChatClient, CommunicationTokenCredential
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class CollaborativeIntelligence:
    def __init__(self):
        self.text_analytics_endpoint = os.getenv("TEXT_ANALYTICS_ENDPOINT")
        self.text_analytics_key = os.getenv("TEXT_ANALYTICS_KEY")
        self.personalizer_endpoint = os.getenv("PERSONALIZER_ENDPOINT")
        self.personalizer_key = os.getenv("PERSONALIZER_KEY")
        self.comm_endpoint = os.getenv("COMMUNICATION_ENDPOINT")
        self.comm_key = os.getenv("COMMUNICATION_KEY")

        # Initialize clients only if credentials are available
        self.text_analytics_client = None
        self.personalizer_client = None
        self.chat_client = None

        if self.text_analytics_endpoint and self.text_analytics_key:
            self.text_analytics_client = TextAnalyticsClient(
                endpoint=self.text_analytics_endpoint,
                credential=AzureKeyCredential(self.text_analytics_key),
            )

        # Communication services need a proper token, not just a key
        # For testing purposes, we'll skip initialization if key isn't properly formatted
        if self.comm_endpoint and self.comm_key:
            try:
                self.chat_client = ChatClient(
                    endpoint=self.comm_endpoint,
                    credential=CommunicationTokenCredential(self.comm_key),
                )
            except ValueError:
                print(
                    "Warning: Invalid Communication Services token format. Chat features will be disabled."
                )
                self.chat_client = None

    def analyze_speech(self, audio_file: str) -> Dict:
        """Analyze speech audio to extract sentiment and insights"""
        # Placeholder for speech recognition and analysis
        # Process the audio file and extract transcribed text
        transcribed_text = f"Transcription from {audio_file}"

        # For demonstration, return dummy data
        return {
            "transcript": transcribed_text,
            "sentiment": "positive",
            "key_phrases": ["learning", "collaboration", "progress"],
        }

    def get_personalized_recommendations(self, context: Dict) -> List[str]:
        """Get personalized recommendations using the Personalizer service"""
        if not self.personalizer_client:
            return ["No personalizer client available"]

        try:
            # Define actions that can be recommended
            actions = [
                RankableAction(id="action1", features=[{"topic": "math"}]),
                RankableAction(id="action2", features=[{"topic": "science"}]),
                RankableAction(id="action3", features=[{"topic": "programming"}]),
            ]

            # Create rank request
            request = RankRequest(actions=actions, context_features=[context])

            # Get recommendations
            response = self.personalizer_client.rank(rank_request=request)

            return [response.reward_action_id]
        except Exception as e:
            print(f"Error getting recommendations: {e}")
            return ["Error in recommendation engine"]

    def chat_with_expert(self, message: str) -> str:
        """Chat with an AI expert on the topic"""
        if not self.chat_client:
            return "Chat service not available"

        try:
            # This is a placeholder - real implementation would create a chat thread
            # and send a message to it
            # For demo purposes
            return f"Expert response to: {message}"
        except Exception as e:
            print(f"Error in chat service: {e}")
            return "Unable to connect to expert chat"

    def create_learning_profile(self, user_data: Dict) -> Dict:
        """Create a learning profile based on user data"""
        # Placeholder for learning profile creation
        profile = {
            "id": user_data.get("id", "unknown"),
            "learning_style": "visual",
            "interests": ["AI", "Machine Learning", "Python"],
            "strengths": ["problem-solving", "critical thinking"],
            "areas_for_improvement": ["time management"],
            "recommended_paths": ["AI Fundamentals", "Python Advanced"],
        }

        return profile


def recommend_content(user_id: str, preferences: Dict) -> List[Dict]:
    """Recommend content based on user preferences"""
    ci = CollaborativeIntelligence()
    # Pass only the preferences to the recommendation function
    ci.get_personalized_recommendations(preferences)

    # Placeholder for content recommendations
    content_items = [
        {"id": "content1", "title": "Introduction to AI", "type": "video"},
        {"id": "content2", "title": "Python for Data Science", "type": "course"},
        {"id": "content3", "title": "Machine Learning Basics", "type": "article"},
    ]

    return content_items
