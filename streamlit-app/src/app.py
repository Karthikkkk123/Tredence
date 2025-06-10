from pathlib import Path

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

# Import custom features
from features.collaborative_intelligence import (
    CollaborativeIntelligence,
    recommend_content,
)
from features.emotional_intelligence import analyze_emotions
from llm.tutor import render_ai_tutor_ui

# Load environment variables
# Try to find .env file in different locations
env_paths = [
    Path(".env"),  # Current directory
    Path("../.env"),  # Parent directory
    Path("../../.env"),  # Grandparent directory
]

for env_path in env_paths:
    if env_path.exists():
        load_dotenv(dotenv_path=str(env_path))
        print(f"Loaded environment from {env_path}")
        break

# Configure the app
st.set_page_config(
    page_title="AI Education Assistant",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Sidebar
st.sidebar.title("AI Education Assistant")
st.sidebar.info(
    "This application demonstrates the use of Azure Cognitive Services "
    "to create an intelligent education assistant."
)

# Create tabs for different features
tabs = st.tabs(
    ["Emotional Analysis", "Content Recommendations", "Learning Profile", "AI Tutor"]
)

# Tab 1: Emotional Analysis
with tabs[0]:
    st.header("Emotional Intelligence")
    st.write("Analyze emotions from text, images, or audio.")

    input_type = st.selectbox("Select input type:", ["text", "image", "audio"])

    if input_type == "text":
        text_input = st.text_area(
            "Enter text to analyze:",
            "I'm excited to learn about artificial intelligence!",
        )
        if st.button("Analyze Text"):
            with st.spinner("Analyzing..."):
                results = analyze_emotions(text_input, "text")
                st.subheader("Analysis Results:")
                if "error" in results:
                    st.error(results["error"])
                else:
                    emotions = results["emotions"]
                    provider = results.get("provider", "unknown")
                    st.write(f"Overall sentiment: {emotions['overall']}")
                    st.write(f"Analysis provided by: {provider.upper()}")

                    # Create a bar chart of emotions
                    chart_data = pd.DataFrame(
                        {
                            "Emotion": ["Positive", "Neutral", "Negative"],
                            "Score": [
                                emotions["positive"],
                                emotions["neutral"],
                                emotions["negative"],
                            ],
                        }
                    )
                    st.bar_chart(chart_data.set_index("Emotion"))

    elif input_type == "image":
        st.write("Upload an image to analyze facial emotions.")
        uploaded_file = st.file_uploader(
            "Choose an image...", type=["jpg", "jpeg", "png"]
        )

        if uploaded_file is not None:
            # Display the image
            st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)

            if st.button("Analyze Image"):
                with st.spinner("Analyzing emotions in image..."):
                    try:
                        # Reset file pointer and analyze
                        uploaded_file.seek(0)
                        results = analyze_emotions(uploaded_file, "image")

                        st.subheader("Emotion Analysis Results:")
                        if "error" in results:
                            st.error(results["error"])
                        elif "message" in results and "No faces" in results["message"]:
                            st.warning(results["message"])
                        else:
                            # Show which service provided the analysis
                            provider = results.get("provider", "unknown")
                            st.info(f"Analysis provided by: {provider.upper()}")

                            # Display detected face count if available
                            if "face_count" in results:
                                face_count = results["face_count"]
                                st.write(
                                    f"Detected {face_count} {'face' if face_count == 1 else 'faces'} in the image"
                                )

                            # Create column layout
                            col1, col2 = st.columns(2)

                            # Basic Sentiment Section
                            with col1:
                                st.subheader("Basic Sentiment")
                                if "dominant_sentiment" in results:
                                    st.success(
                                        f"Dominant Sentiment: {results['dominant_sentiment'].upper()}"
                                    )

                                # Get basic sentiment scores
                                sentiment = results.get("sentiment", {})
                                if sentiment:
                                    chart_data = pd.DataFrame(
                                        {
                                            "Sentiment": list(sentiment.keys()),
                                            "Score": list(sentiment.values()),
                                        }
                                    )
                                    st.bar_chart(chart_data.set_index("Sentiment"))

                            # Specific Emotions Section
                            with col2:
                                st.subheader("Specific Emotions")
                                if "dominant_emotion" in results:
                                    st.success(
                                        f"Dominant Emotion: {results['dominant_emotion'].upper()}"
                                    )

                                # Get specific emotions
                                emotions = results.get("emotions", {})
                                if emotions:
                                    chart_data = pd.DataFrame(
                                        {
                                            "Emotion": list(emotions.keys()),
                                            "Score": list(emotions.values()),
                                        }
                                    )
                                    chart_data = chart_data.sort_values(
                                        "Score", ascending=False
                                    )
                                    st.bar_chart(chart_data.set_index("Emotion"))
                    except Exception as e:
                        st.error(f"An error occurred during analysis: {str(e)}")
                        st.info("Using fallback emotion analysis...")

                        # Provide a fallback analysis with placeholder data
                        st.subheader("Emotion Analysis Results (Placeholder):")
                        st.warning(
                            "Could not analyze the uploaded image. Using placeholder data instead."
                        )

                        # Create placeholder data
                        emotions = {
                            "happiness": 0.1,
                            "sadness": 0.1,
                            "neutral": 0.5,
                            "anger": 0.05,
                            "fear": 0.05,
                            "surprise": 0.1,
                            "contempt": 0.05,
                            "disgust": 0.05,
                        }

                        sentiment = {"positive": 0.2, "neutral": 0.5, "negative": 0.3}

                        # Display placeholder results
                        col1, col2 = st.columns(2)

                        with col1:
                            st.subheader("Basic Sentiment")
                            chart_data = pd.DataFrame(
                                {
                                    "Sentiment": list(sentiment.keys()),
                                    "Score": list(sentiment.values()),
                                }
                            )
                            st.bar_chart(chart_data.set_index("Sentiment"))

                        with col2:
                            st.subheader("Specific Emotions")
                            chart_data = pd.DataFrame(
                                {
                                    "Emotion": list(emotions.keys()),
                                    "Score": list(emotions.values()),
                                }
                            )
                            chart_data = chart_data.sort_values(
                                "Score", ascending=False
                            )
                            st.bar_chart(chart_data.set_index("Emotion"))

    elif input_type == "audio":
        st.write("Audio upload feature is under development.")
        uploaded_file = st.file_uploader("Choose an audio file...", type=["mp3", "wav"])
        if uploaded_file is not None and st.button("Analyze Audio"):
            st.audio(uploaded_file, format="audio/wav")
            st.write("Audio analysis feature is under development.")

# Tab 2: Content Recommendations
with tabs[1]:
    st.header("Content Recommendations")
    st.write("Get personalized learning content recommendations.")

    # User ID input
    user_id = st.text_input("Enter User ID:", "user123")

    # Preferences
    st.subheader("Your Preferences")
    col1, col2 = st.columns(2)

    with col1:
        topic = st.selectbox(
            "Preferred Topic:", ["AI", "Machine Learning", "Python", "Data Science"]
        )
        level = st.select_slider(
            "Experience Level:", options=["Beginner", "Intermediate", "Advanced"]
        )

    with col2:
        format_pref = st.multiselect(
            "Preferred Format:",
            ["Video", "Article", "Interactive", "Course"],
            default=["Video"],
        )
        time_available = st.slider(
            "Time Available (minutes):", min_value=5, max_value=120, value=30, step=5
        )

    # Get recommendations
    if st.button("Get Recommendations"):
        with st.spinner("Fetching recommendations..."):
            preferences = {
                "topic": topic,
                "level": level,
                "format": format_pref,
                "time": time_available,
            }

            recommendations = recommend_content(user_id, preferences)

            st.subheader("Recommended Content:")
            for item in recommendations:
                with st.expander(f"{item['title']} ({item['type']})"):
                    st.write(f"ID: {item['id']}")
                    st.write(f"Type: {item['type']}")
                    st.write("This is a placeholder for content details.")

# Tab 3: Learning Profile
with tabs[2]:
    st.header("Learning Profile")
    st.write("Create and view your personalized learning profile.")

    # User information form
    with st.form("profile_form"):
        st.subheader("Your Information")

        user_name = st.text_input("Name:", "John Doe")
        user_age = st.slider("Age:", min_value=10, max_value=100, value=30)
        education = st.selectbox(
            "Highest Education:", ["High School", "Bachelor's", "Master's", "PhD"]
        )

        interests = st.multiselect(
            "Interests:",
            [
                "AI",
                "Machine Learning",
                "Web Development",
                "Mobile Apps",
                "Data Science",
                "Cybersecurity",
                "Game Development",
                "Cloud Computing",
            ],
            default=["AI", "Data Science"],
        )

        goals = st.text_area(
            "Learning Goals:", "I want to become proficient in using AI for education."
        )

        submitted = st.form_submit_button("Create Profile")

        if submitted:
            with st.spinner("Creating your learning profile..."):
                user_data = {
                    "id": "user123",  # In a real app, this would be dynamic
                    "name": user_name,
                    "age": user_age,
                    "education": education,
                    "interests": interests,
                    "goals": goals,
                }

                ci = CollaborativeIntelligence()
                profile = ci.create_learning_profile(user_data)

                st.success("Learning profile created!")

                st.subheader("Your Learning Profile")

                col1, col2 = st.columns(2)

                with col1:
                    st.write("**Learning Style:**", profile["learning_style"])
                    st.write("**Strengths:**")
                    for strength in profile["strengths"]:
                        st.write(f"- {strength}")

                with col2:
                    st.write("**Areas for Improvement:**")
                    for area in profile["areas_for_improvement"]:
                        st.write(f"- {area}")

                    st.write("**Recommended Learning Paths:**")
                    for path in profile["recommended_paths"]:
                        st.write(f"- {path}")

# Tab 4: AI Tutor with abstracted LLM interface
with tabs[3]:
    render_ai_tutor_ui()

if __name__ == "__main__":
    # This will execute when the script is run directly
    pass
