import streamlit as st
import openai
import os
import json
import re
from typing import List, Dict

# Set your OpenAI API key\openai.api_key = os.getenv("OPENAI_API_KEY")

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
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a business strategist AI."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )
    return response['choices'][0]['message']['content'].strip()

# System parser
def parse_system_components(answers: List[str], questions: List[str]) -> str:
    combined_input = "\n".join([f"Q{i+1}: {q}\nA{i+1}: {a}" for i, (q, a) in enumerate(zip(questions, answers))])
    prompt = f"""
Given the following business questionnaire, extract and structure:
- Stocks (cash, assets, people, partnerships)
- Flows (revenue, costs, acquisition channels, ops)
- Loops (reinforcing patterns like more X leads to more Y)
- Context (trends, customer needs, competition)

Return only a valid JSON object with those four categories. Do not include any explanation or text outside the JSON.

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
            strategy_text = parse_system_components(answers, questions)
            cleaned = re.sub(r"```(?:json)?", "", strategy_text).replace("```", "").strip()
            strategy = json.loads(cleaned)
            st.success("Here's your strategy:")
            st.json(strategy)
        except json.JSONDecodeError as e:
            st.error(f"Error parsing strategy JSON: {e}")
        except Exception as e:
            st.error(f"Unexpected error: {e}")
