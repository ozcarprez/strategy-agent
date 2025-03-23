import streamlit as st
import openai
import os
from typing import List, Dict

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
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a business strategist AI."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )
    return response['choices'][0]['message']['content'].strip()

# System parser
def parse_system_components(answers: List[str], questions: List[str]) -> Dict:
    combined_input = "\n".join([f"Q{i+1}: {q}\nA{i+1}: {a}" for i, (q, a) in enumerate(zip(questions, answers))])
    prompt = f"""
Given the following business questionnaire, extract and structure:
- Stocks (cash, assets, people, partnerships)
- Flows (revenue, costs, acquisition channels, ops)
- Loops (reinforcing patterns like more sales → more buzz)
- Context (trends, customer needs, competition)

Return as a JSON with those four categories.

{combined_input}
"""
    return eval(gpt_extract(prompt))

# BOS generator
def generate_bos_playbook(system_map: Dict) -> Dict:
    prompt = f"""
Based on the following business system map:

Stocks: {system_map['stocks']}
Flows: {system_map['flows']}
Loops: {system_map['loops']}
Context: {system_map['context']}

Apply the Blue Ocean Strategy framework. Propose:
- What to Eliminate (waste or low-value offerings)
- What to Reduce (overkill)
- What to Raise (key strengths)
- What to Create (new value innovations)

Respond as a JSON object with keys: Eliminate, Reduce, Raise, Create.
"""
    return eval(gpt_extract(prompt))

# Streamlit UI
st.title("🚀 Strategy Agent: Blue Ocean Generator")
st.write("Answer these 16 questions and get your custom strategy.")

questions = load_questions()
answers = []

with st.form("strategy_form"):
    for q in questions:
        answers.append(st.text_input(q, key=q))
    submitted = st.form_submit_button("Generate Strategy")

if submitted:
    with st.spinner("Analyzing your business and generating your strategy..."):
        try:
            system_map = parse_system_components(answers, questions)
            playbook = generate_bos_playbook(system_map)

            st.success("Here’s your Blue Ocean Strategy:")
            for section, ideas in playbook.items():
                st.subheader(section)
                for idea in ideas:
                    st.write(f"- {idea}")
        except Exception as e:
            st.error("Something went wrong. Check your API key and try again.")
            st.exception(e)
