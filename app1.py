# app.py
import streamlit as st
from QAEngine import answer_question

st.set_page_config(page_title="Project Samarth - Intelligent Q&A System", layout="centered")

st.title("🌾 Project Samarth — Agricultural + Climate Q&A")
st.markdown("Ask questions about India's **agricultural economy and climate patterns**, powered by live data from [data.gov.in](https://data.gov.in).")

question = st.text_input("🗣️ Ask your question here:", 
                         "Compare the average annual rainfall in State_Gujarat and State_Maharashtra for the last 5 years.")

if st.button("🔍 Get Answer"):
    with st.spinner("Fetching data and analyzing..."):
        try:
            answer, rainfall_df, crops_df, citations = answer_question(question)
            st.success("✅ Answer Generated Successfully!")
            st.markdown("### 🧠 Answer:")
            st.markdown(answer)

            st.markdown("### 🌧️ Rainfall Comparison")
            st.dataframe(rainfall_df)

            st.markdown("### 🌾 Top Crops by Production")
            st.dataframe(crops_df)

            st.markdown("### 📚 Data Sources & Citations")
            for cite in citations:
                st.markdown(f"- {cite}")

        except Exception as e:
            st.error(f"Error: {e}")
            st.info("Please check if your API key or resource IDs are correct.")
