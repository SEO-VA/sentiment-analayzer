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
            
        # Step 1: Split sentences
        sentences = split_sentences(content)
        if user_type == "admin":
            with st.expander("Debug: Sentence Splitting"):
                st.json(sentences)
                if not st.button("Continue to API Call", key="step1"):
                    return
        
        # Step 2: Call OpenAI Assistant
        response = call_openai_assistant(sentences)
        if user_type == "admin":
            with st.expander("Debug: Assistant Response"):
                st.json(response)
                if not st.button("Continue to Validation", key="step2"):
                    return
        
        # Step 3: Validate response
        validated_results = validate_response(response, sentences)
        if user_type == "admin":
            with st.expander("Debug: Validation Results"):
                st.json(validated_results)
                if not st.button("Continue to Rendering", key="step3"):
                    return
        
        # Step 4: Render results
        render_results(sentences, validated_results)
        generate_html_download(sentences, validated_results)

if __name__ == "__main__":
    main()
