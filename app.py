# app.py
import streamlit as st
import json
from core.splitter import split_into_items
from services.openai_client import classify_items
from utils.helpers import clean_text

# -----------------------------
# 🔐 Authentication
# -----------------------------

def check_password():
    """Simple password check using Streamlit secrets."""
    def login_form():
        st.sidebar.header("🔐 Login")
        username = st.sidebar.text_input("Username", key="login_username")
        password = st.sidebar.text_input("Password", type="password", key="login_password")
        return username, password

    if "authenticated" not in st.session_state:
        username, password = login_form()
        if st.sidebar.button("Login"):
            users = st.secrets.get("auth", {}).get("users", {})
            if username in users and users[username] == password:
                st.session_state.authenticated = True
                st.session_state.username = username
                st.session_state.role = "admin" if username == "admin" else "user"
                st.rerun()
            else:
                st.sidebar.error("Invalid credentials")
        return False
    return True

if not check_password():
    st.stop()

# -----------------------------
# 🎯 Main App (after login)
# -----------------------------

st.set_page_config(page_title="Content Classifier", layout="wide")

role = st.session_state.role
username = st.session_state.username

st.title("🔍 Content Type Classifier")
st.caption(f"Role: **{role.upper()}**")

# =============================
# 🧑‍💼 USER VIEW (Simple One-Step)
# =============================

if role == "user":
    input_text = st.text_area("Paste your content:", height=300, placeholder="Enter text to classify...")

    if st.button("🚀 Classify Content"):
        if not input_text.strip():
            st.warning("Please enter some text.")
        else:
            with st.spinner("Processing..."):

                # Step 1: Clean & Split
                cleaned = clean_text(input_text)
                items = split_into_items(cleaned, mode="paragraph")

                if not items:
                    st.warning("No valid content to process.")
                else:
                    try:
                        # Step 2: Call Assistant
                        result = classify_items(
                            items=items,
                            assistant_id=st.secrets["assistant_step_1_id"],
                            api_key=st.secrets["openai_api_key"]
                        )

                        # Step 3: Render result
                        html_out = render_classification_html(items, result)
                        st.session_state.html_result = html_out

                        st.markdown("### ✅ Classified Output")
                        st.components.v1.html(html_out, height=600, scrolling=True)

                        st.download_button(
                            "💾 Download HTML",
                            html_out,
                            file_name="classified_content.html",
                            mime="text/html"
                        )
                    except Exception as e:
                        st.error(f"Classification failed: {str(e)}")

# =============================
# 👨‍💻 ADMIN VIEW (Debug + Step-by-Step)
# =============================

elif role == "admin":
    input_text = st.text_area("📝 Input Text", height=200, key="admin_input")

    steps = ["Clean & Split", "Call Assistant", "Validate & Render"]
    progress = st.progress(0)
    status_text = st.empty()

    if st.button("▶️ Run Pipeline"):
        if not input_text.strip():
            st.warning("Input is empty.")
        else:
            result_items = None
            raw_result = None
            html_output = None

            # ----- Step 1: Clean & Split -----
            status_text.text("Step 1/3: Cleaning and splitting text...")
            progress.progress(33)

            cleaned = clean_text(input_text)
            items = split_into_items(cleaned, mode="paragraph")

            with st.expander("🔍 Step 1: Items after splitting", expanded=True):
                st.json(items)

            if not items:
                st.error("No items to process.")
            else:
                # ----- Step 2: Call Assistant -----
                status_text.text("Step 2/3: Calling OpenAI Assistant...")
                progress.progress(66)

                try:
                    raw_result = classify_items(
                        items=items,
                        assistant_id=st.secrets["assistant_step_1_id"],
                        api_key=st.secrets["openai_api_key"]
                    )
                    with st.expander("🔍 Step 2: Raw Assistant Response", expanded=True):
                        st.json(raw_result)
                except Exception as e:
                    st.error(f"API call failed: {e}")
                    st.stop()

                # ----- Step 3: Validate & Render -----
                status_text.text("Step 3/3: Validating and rendering...")
                progress.progress(100)

                try:
                    html_output = render_classification_html(items, raw_result)
                    st.session_state.html_result = html_output

                    st.markdown("### 🎨 Final Output")
                    st.components.v1.html(html_output, height=600, scrolling=True)

                    st.download_button(
                        "💾 Download HTML",
                        html_output,
                        file_name="classified_content.html",
                        mime="text/html"
                    )
                except Exception as e:
                    st.error(f"Rendering failed: {e}")

    # Logs in sidebar
    with st.sidebar.expander("📋 Session Logs"):
        st.write("Last raw result:", st.session_state.get('raw_result', 'None'))
        st.write("Last HTML size:", len(st.session_state.get('html_result', '')))

# -----------------------------
# 🎨 Shared: HTML Renderer
# -----------------------------

def render_classification_html(items, raw_result):
    """Generate HTML with color highlights."""
    css = """
    <style>
    body { font-family: sans-serif; line-height: 1.6; margin: 15px; }
    .item { margin: 8px 0; padding: 4px 0; }
    .info { background-color: #d4edff; }
    .promo { background-color: #fff3cd; }
    .risk { background-color: #f8d7da; }
    .legend { margin: 15px 0; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }
    .legend-item { margin: 5px; }
    .legend-color { display: inline-block; width: 12px; height: 12px; margin-right: 6px; }
    .info-bg { background-color: #d4edff; }
    .promo-bg { background-color: #fff3cd; }
    .risk-bg { background-color: #f8d7da; }
    </style>
    """

    legend = """
    <div class="legend">
        <div class="legend-item"><span class="legend-color info-bg"></span> <strong>Informational</strong></div>
        <div class="legend-item"><span class="legend-color promo-bg"></span> <strong>Promotional</strong></div>
        <div class="legend-item"><span class="legend-color risk-bg"></span> <strong>Risk Warning</strong></div>
    </div>
    """

    content_html = ""
    item_dict = {item["idx"]: item["content"] for item in items}

    for item in raw_result:
        idx = item.get("idx")
        if idx not in item_dict:
            continue
        text = item_dict[idx]

        if "spans" in item:
            parts = []
            last_end = 0
            for span in sorted(item["spans"], key=lambda x: x["start"]):
                start, end, label = span["start"], span["end"], span["label"]
                if start > last_end:
                    parts.append(text[last_end:start])
                parts.append(f'<span class="{label}">{text[start:end]}</span>')
                last_end = end
            if last_end < len(text):
                parts.append(text[last_end:])
            line = "".join(parts)
        else:
            label = item["label"]
            line = f'<span class="{label}">{text}</span>'

        content_html += f'<div class="item">{line}</div>'

    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="UTF-8">{css}</head>
    <body>
        <div>
            <h1>Classified Content</h1>
            {legend}
            {content_html}
            <footer><small>Generated by Content Classifier • Role: {role.upper()}</small></footer>
        </div>
    </body>
    </html>
    """
    return full_html
