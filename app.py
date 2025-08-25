import streamlit as st
from modules.auth import check_auth, get_user_type
from modules.processing import split_sentences, call_openai_assistant
from modules.validation import validate_response
from modules.rendering import render_results, generate_html_download

def main():
    st.set_page_config(page_title="Content Classifier", layout="wide")
    
    if not check_auth():
        return
    
    user_type = get_user_type()
    st.title("Content Classifier")
    
    content = st.text_area("Paste content here:", height=200)
    
    if st.button("Classify"):
        if not content.strip():
            st.error("Please enter content")
            return
        
        # Initialize session state for admin workflow
        if user_type == "admin":
            st.session_state.admin_content = content
            st.session_state.admin_step = 1
        
        process_content(content, user_type)

def process_content(content, user_type):
    # Step 1: Split sentences
    if user_type == "admin" and st.session_state.get('admin_step', 1) >= 1:
        sentences = split_sentences(content)
        with st.expander("Debug: Sentence Splitting", expanded=True):
            st.json(sentences)
            if st.button("Continue to API Call", key="step1"):
                st.session_state.admin_step = 2
                st.rerun()
            return
    else:
        sentences = split_sentences(content)
    
    # Step 2: Call OpenAI Assistant
    if user_type == "admin" and st.session_state.get('admin_step', 1) >= 2:
        sentences = split_sentences(st.session_state.admin_content)
        response = call_openai_assistant(sentences)
        with st.expander("Debug: Assistant Response", expanded=True):
            st.json(response)
            if st.button("Continue to Validation", key="step2"):
                st.session_state.admin_step = 3
                st.session_state.admin_response = response
                st.rerun()
            return
    else:
        response = call_openai_assistant(sentences)
    
    # Step 3: Validate response
    if user_type == "admin" and st.session_state.get('admin_step', 1) >= 3:
        sentences = split_sentences(st.session_state.admin_content)
        response = st.session_state.admin_response
        validated_results = validate_response(response, sentences)
        with st.expander("Debug: Validation Results", expanded=True):
            st.json(validated_results)
            if st.button("Continue to Rendering", key="step3"):
                st.session_state.admin_step = 4
                st.session_state.admin_validated = validated_results
                st.rerun()
            return
    else:
        validated_results = validate_response(response, sentences)
    
    # Step 4: Render results
    if user_type == "admin":
        sentences = split_sentences(st.session_state.admin_content)
        validated_results = st.session_state.admin_validated
    
    render_results(sentences, validated_results)
    generate_html_download(sentences, validated_results)

if __name__ == "__main__":
    main()
