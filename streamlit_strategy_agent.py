import streamlit as st
import openai
import os
import json
from typing import List, Dict

# Set OpenAI key securely (recommended via environment variable)
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Redesigned system thinking questions
def load_system_questions() -> List[str]:
    return [
        "What flows through your business? (e.g., money, products, info)",
        "What gets stuck or accumulates in your business? (e.g., inventory, debt)",
        "What loops (repetitive patterns) do you notice happening again and again?",
        "What causes delays or friction?",
        "What changes when a part of the system changes?",
        "What is something you do that creates more of the same result, good or bad?",
        "Where do small changes seem to have a big effect?",
        "Who are the main actors (internal or external) moving the system?",
        "What parts of the system depend on each other?",
        "If you stepped away, what would keep working and what would stop?"
    ]

# Generate system-based strategy

def generate_system_strategy(answers: List[str], questions: List[str]) -> Dict:
    combined = "\n".join([f"Q{i+1}: {q}\nA{i+1}: {a}" for i, (q, a) in enumerate(zip(questions, answers))])

    prompt = f"""
Given the business insights below, analyze them using systems thinking.
1. Identify stocks, flows, delays, and loops.
2. Highlight any reinforcing or balancing feedback loops.
3. Identify key bottlenecks and points of leverage.
4. Give a brutally honest summary of how the system is working.
5. Offer 2-3 high-leverage strategic recommendations.

Respond in this JSON format:
{{
  "Loops": [],
  "Stocks": [],
  "Flows": [],
  "Delays": [],
  "Bottlenecks": [],
  "LeveragePoints": [],
  "HonestSummary": "...",
  "StrategicRecommendations": ["...", "..."]
}}

Business context:
{combined}
"""
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return json.loads(response.choices[0].message.content)

# Streamlit UI
st.set_page_config(page_title="Systems Thinking Strategy App")
st.title("🧠 Systems Thinking Strategy Generator")
st.write("Answer these reflective questions to analyze your business as a system.")

questions = load_system_questions()
answers = []

with st.form("sys_form"):
    for q in questions:
        answers.append(st.text_input(q))
    submitted = st.form_submit_button("Generate System Strategy")

if submitted:
    if any(a.strip() == "" for a in answers):
        st.error("Please answer all questions.")
    else:
        try:
            strategy = generate_system_strategy(answers, questions)
            st.success("Here is your systems-based strategy:")
            st.json(strategy)
        except Exception as e:
            st.error(f"Error generating strategy: {e}")
