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
        
        if user_type == "admin":
            admin_workflow(content)
        else:
            normal_workflow(content)

def normal_workflow(content):
    sentences = split_sentences(content)
    response = call_openai_assistant(sentences)
    validated_results = validate_response(response, sentences)
    render_results(sentences, validated_results)
    generate_html_download(sentences, validated_results)

def admin_workflow(content):
    # Step 1: Split sentences
    sentences = split_sentences(content)
    with st.expander("Debug: Sentence Splitting", expanded=True):
        st.json(sentences)
    
    if st.button("Continue to API Call"):
        # Step 2: API Call
        response = call_openai_assistant(sentences)
        with st.expander("Debug: Assistant Response", expanded=True):
            st.json(response)
        
        if st.button("Continue to Validation"):
            # Step 3: Validation
            validated_results = validate_response(response, sentences)
            with st.expander("Debug: Validation Results", expanded=True):
                st.json(validated_results)
            
            if st.button("Continue to Rendering"):
                # Step 4: Render
                render_results(sentences, validated_results)
                generate_html_download(sentences, validated_results)

if __name__ == "__main__":
    main()
