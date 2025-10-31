import streamlit as st
from google import genai
import PyPDF2

st.title("Chat with PDF using Gemini 2.0 with Streamlit")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "pdf_text" not in st.session_state:
    st.session_state.pdf_text = ""
if "client" not in st.session_state:
    st.session_state.client = None
if "api_key_entered" not in st.session_state:
    st.session_state.api_key_entered = False

uploaded_file = st.file_uploader("Upload a PDF", type="pdf")

if uploaded_file is not None:
    # Show input box for user API key
    user_api_key = st.text_input("Enter your Gemini API Key to enable chat", type="password")
    st.write("You can create your API key by visiting https://aistudio.google.com/api-keys")
    
    if user_api_key:
        if not st.session_state.api_key_entered or st.session_state.api_key != user_api_key:
            # Save key and create new client
            st.session_state.api_key = user_api_key
            st.session_state.client = genai.Client(api_key=user_api_key)
            st.session_state.api_key_entered = True
            st.session_state.chat_history = []
            st.session_state.pdf_text = ""

        if st.session_state.pdf_text == "" or st.session_state.get("uploaded_pdf_name") != uploaded_file.name:
            # Extract text once and store in session
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            pdf_text = ""
            for page in pdf_reader.pages:
                pdf_text += page.extract_text() or ""
            st.session_state.pdf_text = pdf_text
            st.session_state.uploaded_pdf_name = uploaded_file.name
            st.session_state.chat_history = [("System", "PDF uploaded and text extracted.")]
            # Optionally reset chat history here

        def submit_question():
            user_question = st.session_state.user_question.strip()
            if not user_question:
                return

            # Add user question to history
            st.session_state.chat_history.append(("User", user_question))

            # Create chat for each question
            chat = st.session_state.client.chats.create(model="gemini-2.0-flash-exp")

            # Construct prompt with PDF text plus conversation history for context
            system_prompt = f"Here is the text extracted from the uploaded PDF:\n{st.session_state.pdf_text}"
            chat.send_message(system_prompt)

            for role, msg in st.session_state.chat_history:
                if role != "System":
                    prefix = "User" if role == "User" else "AI"
                    chat.send_message(f"{prefix}: {msg}")

            # Send current question and get response
            response = chat.send_message(user_question)

            # Add AI response to history
            st.session_state.chat_history.append(("AI", response.text))

            # Clear input box
            st.session_state.user_question = ""

        # Display chat messages
        for role, msg in st.session_state.chat_history:
            if role == "User":
                st.markdown(f"**You:** {msg}")
            elif role == "AI":
                st.markdown(f"**AI:** {msg}")
            else:
                st.markdown(f"*{msg}*")

        # Input box for questions
        st.text_input(
            "Ask questions about the PDF:",
            key="user_question",
            on_change=submit_question,
            placeholder="Type your question and press Enter"
        )

    else:
        st.warning("Please provide your Gemini API key to extract text and enable chat.")
