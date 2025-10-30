import streamlit as st
from QAEngine import QAEngine
from PIL import Image
import base64

def render_logo():
    st.markdown("""
    <div style='text-align: center; padding-bottom: 2px;'>
        <img src='https://cdn-icons-png.flaticon.com/512/427/427735.png' width='45' style='margin-bottom:0;' alt='Project Samarth Logo'/>
    </div>
    """, unsafe_allow_html=True)

def get_suggestion_list():
    return [
        "Compare average rainfall between Gujarat and Maharashtra in 2022.",
        "What were the top crops in Karnataka last 3 years?",
        "Which state had the highest rainfall recently?",
        "Show rainfall and crop info for Andhra Pradesh in 2021.",
        "How does rainfall trend relate to rice production?"
    ]

def main():
    st.set_page_config(page_title="Project Samarth - Agri Insights", page_icon="🌱", layout="wide")
    st.markdown("""
        <style>
            body, .main, .stApp {
                background-color: #f7fff7 !important;
                margin: 0 !important;
                padding: 0 !important;
                box-sizing: border-box;
            }
            div[data-testid="stVerticalBlock"] > div > div {
                background: #fff;
                border-radius: 14px;
                box-shadow: 0 2px 18px rgba(54, 87, 73, 0.05);
                padding: clamp(0.6rem, 2vw, 1.5rem);
                margin-top: 1.3vh;
                width: 100% !important;
                min-width: 0 !important;
                max-width: 900px;
                margin-left: auto; margin-right: auto;
            }
            .info-box {
                background: linear-gradient(90deg, #cdeaff 0, #e0ffe2 100%);
                border-radius: 14px;
                padding: 1.2em 1.4em 1em 1.4em;
                margin-bottom: 1em;
                color: #29474d;
                font-size: 1.07rem;
                border-left: 8px solid #4eb8a9;
                font-family: inherit;
                line-height: 1.6;
            }
            .suggestions-row {
                display: flex; flex-wrap: wrap; gap: 0.8em 0.7em; margin: 8px 0 4px 0; justify-content: center;
            }
            .suggest-btn {
                background: #e0ffe2; border: none; color: #19774f; padding: 0.46em 1em;
                font-weight: 500; border-radius: 20px; cursor: pointer;
                transition: background 0.18s;
                font-size: 16px; margin: 2px 3px;
            }
            .suggest-btn:hover { background: #bafad6 !important; }
            .answer-box {
                background: #f1f8e9; border-left: 5px solid #348e63; padding: 1em 1.1em;
                border-radius:11px; margin-top:1.3vh; font-size:17px;
                max-width:100%; overflow-x:auto; color: #232323;
            }
            @media (max-width: 750px) {
                div[data-testid="stVerticalBlock"] > div > div { padding: 0.7em !important; max-width:99vw;}
                .answer-box { font-size:14px !important; }
                .suggest-btn { font-size: 13px !important; }
                .info-box { font-size: 15px !important; padding:0.6em !important; }
            }
        </style>
    """, unsafe_allow_html=True)

    render_logo()
    st.markdown("<h2 style='text-align:center; color:#2d4c3f; margin:0 0 10px 0;'>Project Samarth - Smart Agricultural Data Q&A</h2>", unsafe_allow_html=True)

    st.markdown('''<div class="info-box">
    <b>About this project:</b><br>
    Project Samarth is an interactive question-answering and analytics tool for exploring Indian agricultural trends. It enables farmers, analysts, and students to compare <b>state-wise rainfall</b> and <b>crop production</b> data from real datasets.<br><br>
    <b>How to use:</b> Enter a natural English question about rainfall, production, crops, or states (e.g., <i>"What are the top crops in Karnataka last 3 years?"</i> or <i>"Compare rainfall for Maharashtra and Gujarat in 2022"</i>). Click a suggestion or type your own!<br><br>
    <b>Data sources:</b> This demo uses sample data from open government resources and standard benchmarks, but you can connect it to your own district, state, or local CSVs.<br>
    </div>''', unsafe_allow_html=True)

    if 'question' not in st.session_state:
        st.session_state['question'] = ""
    if 'trigger_answer' not in st.session_state:
        st.session_state['trigger_answer'] = False

    st.markdown("<b>Examples you can try:</b>", unsafe_allow_html=True)
    sug_list = get_suggestion_list()
    st.markdown('<div class="suggestions-row">' +
        ''.join([f'<button class="suggest-btn" onclick="window.dispatchEvent(new CustomEvent(\'suggestion_click\',{{detail:\'{s}\'}}))">{s}</button>' for s in sug_list]) +
        '</div>', unsafe_allow_html=True)

    # JS to handle button clicks for seamless interactivity
    st.components.v1.html('''<script>
    window.addEventListener("suggestion_click", (e) => {
        const pycmd = `window.suggestedQ = "${e.detail.replace(/"/g, '\\"')}"`;
        eval(pycmd);  window.location.reload();
    });
    </script>''', height=0)
    # Prefill input with JS value if present
    import streamlit as stimpl
    import os
    if hasattr(st, "experimental_rerun"):
        try:
            if hasattr(os, "environ") and "suggestedQ" in os.environ:
                st.session_state['question'] = os.environ["suggestedQ"]
                st.session_state['trigger_answer'] = True
                del os.environ["suggestedQ"]
        except: pass

    # Question input and answer display
    st.session_state['question'] = st.text_input("Type your agricultural question:", value=st.session_state['question'], key="input_question", help="Ask in plain English about rainfall, crops, states, or years.")
    ask = st.button("Get Insights 🌾", use_container_width=True)

    if ask or st.session_state['trigger_answer']:
        st.session_state['trigger_answer'] = False
        if st.session_state['question'].strip():
            qa_engine = QAEngine()
            result = qa_engine.process_question(st.session_state['question'])
            answer = result[0] if isinstance(result, (list, tuple)) else result
            st.markdown('<div class="answer-box">' + str(answer).replace('\n','<br>') + '</div>', unsafe_allow_html=True)
            if isinstance(result, (list, tuple)) and len(result) > 1:
                if hasattr(result[1], 'head'):
                    st.markdown("<b>Rainfall Table:</b>", unsafe_allow_html=True)
                    st.dataframe(result[1], use_container_width=True, height=340)
                if len(result) > 2 and hasattr(result[2], 'head'):
                    st.markdown("<b>Top Crops Table:</b>", unsafe_allow_html=True)
                    st.dataframe(result[2], use_container_width=True, height=340)

if __name__ == "__main__":
    main()