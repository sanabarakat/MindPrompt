# MindPrompt

MindPrompt is an AI-powered journaling platform designed to support self-reflection and emotional awareness. It gives users the option to journal using either structured, traditional prompts or personalized AI-generated reflections.
It was developed as part of a graduation thesis on the use of AI in mental health tools.


## Features

- Two journaling modes:
  - Traditional prompts tailored to user preferences
  - Personalized prompts generated from users’ emotional input
- Sentiment and topic analysis for each entry
- Progress tracking with emotion trends over time
- Automatically generated summaries after each session
- Secure account system and profile customization


## Technologies Used

- **Streamlit** for the user interface
- **Firebase** for backend (Firestore, Authentication)
- **Python** for backend logic and analysis
- **OpenAI API** for generating personalized prompts
- **Custom NLP** for emotion and topic classification

---

## Try it live: 
[mindprompt-sanabarakat.streamlit.app](https://mindprompt-sanabarakat.streamlit.app/)

## Main File Structure
- app.py – main app logic
- first_prompt.py – handles traditional prompt selection
- followup_prompt.py – generates personalized questions
- sentiment_analysis.py – emotion classification model
- topic_classification.py – topics classification model
- generate_summary.py – writes a summary after each journaling session
- firebase_utils.py – handles database read/write
