# Streamlit Application for Emotional Intelligence and Collaborative Learning

This project is a Streamlit application that combines three key features: the Emotional Intelligence Learning Tracker, the Collaborative Intelligence Platform, and the Personalized Cognitive-Emotional Learning Profile. The application leverages Azure Cognitive Services and open-source libraries to provide a comprehensive tool for emotional and collaborative learning.

## Features

### 1. Emotional Intelligence Learning Tracker
- **Facial Expression Recognition**: Utilizes Azure Cognitive Services to analyze facial expressions.
- **Voice Analysis**: Implements voice analysis using Azure Speech Service.
- **Text Sentiment Analysis**: Analyzes text sentiment with Azure Text Analytics API.

### 2. Collaborative Intelligence Platform
- **Recommendation Systems**: Provides personalized recommendations using Azure Personalizer.
- **Collaborative Tools**: Facilitates collaboration through shared workspaces and communication tools.
- **Social Network Analysis**: Analyzes user interactions and relationships using graph-based tools.

### 3. Personalized Cognitive-Emotional Learning Profile
- **Data Aggregation**: Combines data from the Emotional Intelligence and Collaborative Intelligence features.
- **Visualization**: Offers visual insights into the cognitive-emotional learning profile using Power BI and Streamlit.

## Setup Instructions

1. **Clone the Repository**
   ```
   git clone <repository-url>
   cd streamlit-app
   ```

2. **Create a Virtual Environment**
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install Dependencies**
   ```
   pip install -r requirements.txt
   ```

4. **Set Up Environment Variables**
   - Create a `.env` file in the root directory and add your Azure API keys and other sensitive information.

5. **Run the Application**
   ```
   streamlit run src/app.py
   ```

## Usage

- Access the application through the provided local URL after running the Streamlit command.
- Navigate through the features to explore emotional intelligence tracking, collaborative tools, and personalized learning profiles.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.