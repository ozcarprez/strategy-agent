import streamlit as st
import openai
import os
from typing import List

# Set your OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Load questions
def load_questions() -> List[str]:
    return [
        "What does your business sell?",
        "Who is your target customer?",
        "How do you currently acquire customers?",
        "What are your top 3 costs?",
        "What are your top 3 revenue sources?",
        "How much cash do you have on hand?",
        "What assets or equipment do you own?",
        "Who are your partners or suppliers?",
        "What’s your monthly revenue (estimate is OK)?",
        "What’s your biggest bottleneck?",
        "What sets you apart (if anything)?",
        "What frustrates your customers the most?",
        "What’s something customers keep asking for?",
        "Who are your top competitors?",
        "What trends or changes are affecting your industry?",
        "What are your goals for the next 12 months?"
    ]

# GPT call
def gpt_extract(prompt: str) -> str:
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # Usa "gpt-4" si tienes acceso
        messages=[
            {"role": "system", "content": "You are a business strategist AI."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )
    return response['choices'][0]['message']['content'].strip()

# System parser
def parse_system_components(answers: List[str], questions: List[str]) -> str:
    combined_input = "\n".join([f"{i+1}: {q}\nA{i+1}: {a}" for i, (q, a) in enumerate(zip(questions, answers))])
    prompt = f"""
You are a business strategist specializing in Blue Ocean Strategy and lean startup principles.

Given the following business questionnaire, provide a strategic analysis. Focus on:
- Key insights and business patterns
- Strategic recommendations (eliminate, reduce, raise, create)
- Opportunities for differentiation and growth

Format your answer clearly using bullet points and sections. Do NOT return JSON.

Questionnaire:
{combined_input}
"""
    return gpt_extract(prompt)

# Streamlit app
st.set_page_config(page_title="Strategy Agent: Blue Ocean Generator")
st.title("🚀 Strategy Agent: Blue Ocean Generator")
st.write("Answer these 16 questions and get your custom strategy.")

questions = load_questions()
answers = []

with st.form("strategy_form"):
    for q in questions:
        answer = st.text_input(q)
        answers.append(answer)
    submitted = st.form_submit_button("Generate Strategy")

if submitted:
    if "" in answers:
        st.error("Please answer all the questions.")
    else:
        try:
            strategy = parse_system_components(answers, questions)
            st.success("Here's your strategy:")
            st.markdown(strategy)
        except Exception as e:
            st.error(f"Something went wrong: {e}")

