import streamlit as st
import os
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama

# Load environment variables (for GROQ_API_KEY if placed in a .env file)
load_dotenv()


def generate_story_stream(name, story_theme, engine, groq_api_key=None):
    """
    Initializes the selected LLM (Groq or Ollama) and returns a streaming generator.
    """
    # 1. Initialize the chosen LLM
    if engine == "Groq (Cloud - Fast)":
        if not groq_api_key:
            raise ValueError("Groq API Key is missing!")
        llm = ChatGroq(
            api_key=groq_api_key,
            model="llama-3.1-8b-instant",
            temperature=0.7,
            streaming=True
        )
    else:
        # Ollama (Local)
        llm = ChatOllama(
            model="llama3.1",
            temperature=0.7,
        )

    # 2. Define the Prompt Template
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", (
            "You are a creative storyteller. Write an engaging and imaginative story with a clear "
            "beginning, middle, and end. Keep it suitable for all ages and strictly under 500 words."
        )),
        ("user", (
            "Write a {story_theme} story. The main character is named {name}, "
            "and they should face an interesting challenge or adventure. "
            "Include vivid descriptions, emotions, and a satisfying resolution."
        ))
    ])

    # 3. Create the LangChain LCEL Chain
    chain = prompt_template | llm | StrOutputParser()

    # 4. Return the stream
    return chain.stream({
        "name": name,
        "story_theme": story_theme
    })


# --- Frontend Streamlit UI ---
st.set_page_config(
    page_title='TheAdventure - Story Teller',
    page_icon='🧚',
    layout='centered',
    initial_sidebar_state='expanded'
)

# Sidebar for Configuration
with st.sidebar:
    st.header("⚙️ Settings")

    # Engine Selection
    engine = st.radio(
        "Choose AI Engine:",
        ["Groq (Cloud - Fast)", "Ollama (Local - Private)"]
    )

    # Groq API Key Input
    api_key = os.getenv("GROQ_API_KEY", "")
    if engine == "Groq (Cloud - Fast)":
        st.info("Groq provides blazing fast cloud inference.")
        #user_api_key = st.text_input("Groq API Key", value=api_key, type="password", placeholder="gsk_...")
        user_api_key = api_key
        if user_api_key:
            api_key = user_api_key
        if not api_key:
            st.warning("⚠️ Please enter a Groq API Key to proceed.")

    elif engine == "Ollama (Local - Private)":
        st.info(
            "Ollama runs locally on your machine. Ensure the Ollama app is running and the 'llama3' model is pulled.")

st.header("✨ Generate Your Story! Be the Main Character! ✨")

# Main User Inputs
name = st.text_input("Enter Your Name", placeholder="e.g., John Doe")
story_theme = st.selectbox(
    "Select Theme",
    ["Fun", "Horror", "Fantasy", "Fiction"],
    index=None,
    placeholder="Select Theme"
)

submit = st.button("🚀 Generate Story", use_container_width=True)

# Logic when submit button is pressed
if submit:
    if not name.strip() or not story_theme:
        st.warning("Please enter your name and select a theme!")
    elif engine == "Groq (Cloud - Fast)" and not api_key:
        st.error("GROQ_API_KEY is required to use Groq. Enter it in the sidebar or a .env file.")
    else:
        st.markdown("### 📝 Your Magical Story:")

        with st.spinner(f"Weaving your story using {engine.split()[0]}..."):
            story_placeholder = st.empty()

            try:
                # Stream the response
                response_stream = generate_story_stream(name, story_theme, engine, api_key)
                full_story = story_placeholder.write_stream(response_stream)

                # Download Button
                st.download_button(
                    label="💾 Download Story",
                    data=full_story,
                    file_name=f"{name}_{story_theme}_story.txt",
                    mime="text/plain"
                )
            except Exception as e:
                if "Ollama" in engine:
                    st.error(
                        f"Failed to connect to Ollama. Make sure Ollama is running and you ran `ollama pull llama3`. Error: {e}")
                else:
                    st.error(f"An error occurred with Groq: {e}")