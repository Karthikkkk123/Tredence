from typing import Dict, List

import streamlit as st
from llm.services import get_llm_service, list_available_services


class AITutor:
    """AI Tutor class that uses LLM services to provide educational assistance"""

    def __init__(self, llm_service_name: str = "gemini"):
        """Initialize the AI Tutor with a specific LLM service"""
        self.llm_service = get_llm_service(llm_service_name)
        self.available_services = list_available_services()

    def change_llm_service(self, service_name: str) -> None:
        """Change the LLM service being used"""
        self.llm_service = get_llm_service(service_name)

    def explain_concept(self, concept: str) -> str:
        """Explain an educational concept"""
        return self.llm_service.explain_concept(concept)

    def create_practice_questions(
        self, topic: str, difficulty: str, count: int = 3
    ) -> List[Dict]:
        """Generate practice questions on a topic"""
        return self.llm_service.create_practice_questions(topic, difficulty, count)

    def generate_learning_path(self, topic: str, level: str) -> Dict:
        """Generate a personalized learning path"""
        return self.llm_service.generate_learning_path(topic, level)

    def generate_quiz(self, topic: str, difficulty: str, count: int = 5) -> Dict:
        """Generate an interactive quiz"""
        return self.llm_service.generate_quiz(topic, difficulty, count)

    def suggest_resources(
        self, topic: str, format_type: str = "all", count: int = 5
    ) -> List[Dict]:
        """Suggest learning resources for a topic"""
        return self.llm_service.suggest_resources(topic, format_type, count)

    def get_current_service_info(self) -> Dict:
        """Get information about the currently selected service"""
        for service in self.available_services:
            if self.llm_service.__class__.__name__.lower().startswith(service["id"]):
                return service
        return {"id": "unknown", "name": "Unknown", "description": "Unknown service"}


def render_ai_tutor_ui():
    """Render the AI Tutor UI in Streamlit"""
    # Initialize the tutor in session state if not already there
    if "ai_tutor" not in st.session_state:
        st.session_state.ai_tutor = AITutor()

    tutor = st.session_state.ai_tutor

    # Sidebar for LLM service selection
    with st.sidebar:
        st.subheader("AI Service")
        current_service = tutor.get_current_service_info()

        # Create a dictionary of service names for the selectbox
        service_options = {s["name"]: s["id"] for s in tutor.available_services}
        selected_service_name = st.selectbox(
            "Select AI Service:",
            options=list(service_options.keys()),
            index=list(service_options.keys()).index(current_service["name"])
            if current_service["name"] in service_options.keys()
            else 0,
        )

        selected_service_id = service_options[selected_service_name]

        # Change service if different from current
        if selected_service_id != current_service["id"]:
            tutor.change_llm_service(selected_service_id)
            st.success(f"Switched to {selected_service_name}")

        st.caption(f"Using: {selected_service_name}")
        for s in tutor.available_services:
            if s["id"] == selected_service_id:
                st.caption(s["description"])

    # Create tabs for different tutor features
    tutor_tabs = st.tabs(
        [
            "Concept Explanation",
            "Practice Questions",
            "Learning Path",
            "Resource Finder",
            "Interactive Quiz",
        ]
    )

    # Concept Explanation tab
    with tutor_tabs[0]:
        st.subheader("Explain a Concept")
        concept = st.text_input(
            "Enter an educational concept or topic:", "Machine Learning Backpropagation"
        )

        if st.button("Explain Concept"):
            with st.spinner("Generating explanation..."):
                explanation = tutor.explain_concept(concept)
                st.markdown(explanation)

    # Practice Questions tab
    with tutor_tabs[1]:
        st.subheader("Generate Practice Questions")

        col1, col2 = st.columns(2)
        with col1:
            topic = st.text_input("Topic:", "Python programming basics")
        with col2:
            difficulty = st.select_slider(
                "Difficulty:",
                options=["Beginner", "Intermediate", "Advanced"],
                value="Intermediate",
            )

        num_questions = st.slider(
            "Number of questions:", min_value=1, max_value=5, value=3
        )

        if st.button("Generate Questions"):
            with st.spinner("Creating practice questions..."):
                questions = tutor.create_practice_questions(
                    topic, difficulty, num_questions
                )

                for i, q in enumerate(questions):
                    with st.expander(f"Question {i+1}"):
                        st.markdown("**Question:**")
                        st.markdown(q.get("text", "No question text"))

                        if "options" in q and q["options"]:
                            st.markdown("**Options:**")
                            for opt in q["options"]:
                                st.markdown(f"- {opt}")

                        # Use a unique key for each button
                        reveal_key = f"reveal_answer_{i}"
                        if reveal_key not in st.session_state:
                            st.session_state[reveal_key] = False

                        if st.button(
                            "Reveal Answer"
                            if not st.session_state[reveal_key]
                            else "Hide Answer",
                            key=f"answer_btn_{i}",
                        ):
                            st.session_state[reveal_key] = not st.session_state[
                                reveal_key
                            ]

                        if st.session_state[reveal_key]:
                            st.markdown("**Answer:**")
                            st.markdown(q.get("answer", "No answer provided"))

                            st.markdown("**Explanation:**")
                            st.markdown(q.get("explanation", "No explanation provided"))

    # Learning Path tab
    with tutor_tabs[2]:
        st.subheader("Generate Learning Path")

        col1, col2 = st.columns(2)
        with col1:
            learning_topic = st.text_input(
                "Topic:", "Data Science", key="learning_path_topic"
            )
        with col2:
            learning_level = st.select_slider(
                "Your level:",
                options=["Beginner", "Intermediate", "Advanced"],
                value="Beginner",
            )

        if st.button("Create Learning Path"):
            with st.spinner("Generating your personalized learning path..."):
                path = tutor.generate_learning_path(learning_topic, learning_level)

                if "error" in path:
                    st.error(path["error"])
                else:
                    st.success(
                        f"Learning path created for {path['level']} {path['topic']}"
                    )
                    st.markdown(path["path"])

    # Resource Finder tab
    with tutor_tabs[3]:
        st.subheader("Find Learning Resources")

        col1, col2 = st.columns(2)
        with col1:
            resource_topic = st.text_input(
                "Topic:", "Machine Learning", key="resource_topic"
            )
        with col2:
            resource_type = st.selectbox(
                "Type of Resource:",
                ["all", "books", "courses", "videos", "websites", "articles"],
            )

        resource_count = st.slider(
            "Number of resources:", min_value=1, max_value=8, value=4
        )

        if st.button("Find Resources"):
            with st.spinner("Searching for resources..."):
                resources = tutor.suggest_resources(
                    resource_topic, resource_type, resource_count
                )

                if "error" in resources[0]:
                    st.error(resources[0]["error"])
                else:
                    st.success(f"Found {len(resources)} resources for {resource_topic}")

                    for i, res in enumerate(resources):
                        with st.expander(
                            f"{i+1}. {res.get('title', 'Resource')} ({res.get('level', 'Unknown level')})"
                        ):
                            st.markdown(f"**Author:** {res.get('author', 'Unknown')}")
                            st.markdown(
                                f"**Description:** {res.get('description', 'No description available')}"
                            )
                            if "link" in res:
                                st.markdown(f"**Where to find:** {res.get('link')}")

    # Interactive Quiz tab
    with tutor_tabs[4]:
        st.subheader("Interactive Quiz")

        col1, col2 = st.columns(2)
        with col1:
            quiz_topic = st.text_input("Quiz Topic:", "World History", key="quiz_topic")
        with col2:
            quiz_difficulty = st.select_slider(
                "Difficulty:",
                options=["Beginner", "Intermediate", "Advanced"],
                value="Beginner",
                key="quiz_difficulty",
            )

        quiz_questions = st.slider(
            "Number of questions:",
            min_value=2,
            max_value=10,
            value=5,
            key="quiz_questions",
        )

        if st.button("Generate Quiz"):
            with st.spinner("Creating your quiz..."):
                # Initialize or clear the quiz state
                if "quiz_data" not in st.session_state:
                    st.session_state.quiz_data = {}
                if "quiz_responses" not in st.session_state:
                    st.session_state.quiz_responses = {}
                if "quiz_checked" not in st.session_state:
                    st.session_state.quiz_checked = False

                # Get quiz questions
                quiz = tutor.generate_quiz(quiz_topic, quiz_difficulty, quiz_questions)
                st.session_state.quiz_data = quiz
                st.session_state.quiz_responses = {}
                st.session_state.quiz_checked = False

                st.success(f"Quiz on {quiz_topic} is ready! Scroll down to take it.")
                st.markdown(f"### {quiz_topic} Quiz ({quiz_difficulty})")

                st.rerun()  # Force a rerun to show the quiz

        # Display the quiz if it exists in session state
        if "quiz_data" in st.session_state and st.session_state.quiz_data:
            quiz = st.session_state.quiz_data
            questions = quiz.get("questions", [])

            if questions:
                for i, q in enumerate(questions):
                    st.markdown(f"**Question {i+1}:** {q.get('text', '')}")

                    # For multiple choice questions
                    if "options" in q and q["options"]:
                        options = q["options"]
                        # Clean up options to remove prefixes
                        clean_options = []
                        for opt in options:
                            # Remove A., B., etc. prefixes
                            opt_text = opt
                            if opt.strip()[0].isalpha() and opt.strip()[1:3] in [
                                ". ",
                                ") ",
                            ]:
                                opt_text = opt.strip()[3:]
                            clean_options.append(opt_text)

                        # Use radio button for selection
                        response = st.radio(
                            f"Select your answer for Question {i+1}:",
                            options=clean_options,
                            key=f"quiz_q{i}",
                        )
                        st.session_state.quiz_responses[i] = response
                    else:
                        # For open-ended questions
                        response = st.text_input(
                            f"Your answer for Question {i+1}:", key=f"quiz_q{i}"
                        )
                        st.session_state.quiz_responses[i] = response

                    st.markdown("---")

                # Submit quiz button
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Submit Quiz"):
                        st.session_state.quiz_checked = True
                        st.success("Quiz submitted! Scroll down to see results.")
                        st.rerun()  # Force a rerun to show results

                with col2:
                    if st.button("Clear Responses"):
                        st.session_state.quiz_responses = {}
                        st.session_state.quiz_checked = False
                        st.success("Responses cleared!")
                        st.rerun()

                # Show results if quiz has been submitted
                if st.session_state.quiz_checked:
                    st.markdown("### Quiz Results")
                    correct_count = 0

                    for i, q in enumerate(questions):
                        user_answer = st.session_state.quiz_responses.get(i, "")
                        correct_answer = q.get("answer", "")

                        # Simple check if the user answer contains the correct answer text
                        is_correct = False
                        if user_answer and correct_answer:
                            if isinstance(correct_answer, str) and isinstance(
                                user_answer, str
                            ):
                                # Remove any prefixes like "A. " from the correct answer
                                if correct_answer.strip()[
                                    0
                                ].isalpha() and correct_answer.strip()[1:3] in [
                                    ". ",
                                    ") ",
                                ]:
                                    clean_correct = correct_answer.strip()[3:]
                                else:
                                    clean_correct = correct_answer

                                is_correct = (
                                    clean_correct.lower() in user_answer.lower()
                                    or user_answer.lower() in clean_correct.lower()
                                )

                        if is_correct:
                            correct_count += 1

                        with st.expander(
                            f"Question {i+1} - {'✅ Correct' if is_correct else '❌ Incorrect'}"
                        ):
                            st.markdown(f"**Question:** {q.get('text', '')}")
                            st.markdown(f"**Your answer:** {user_answer}")
                            st.markdown(f"**Correct answer:** {correct_answer}")
                            st.markdown(
                                f"**Explanation:** {q.get('explanation', 'No explanation available')}"
                            )

                    # Show final score
                    score_percentage = (
                        (correct_count / len(questions)) * 100 if questions else 0
                    )
                    st.markdown(
                        f"### Your Score: {correct_count}/{len(questions)} ({score_percentage:.1f}%)"
                    )

                    if score_percentage >= 80:
                        st.success(
                            "Great job! You have a strong understanding of this topic!"
                        )
                    elif score_percentage >= 60:
                        st.info("Good effort! You understand most of this topic.")
                    else:
                        st.warning("Keep studying! This topic might need more review.")
