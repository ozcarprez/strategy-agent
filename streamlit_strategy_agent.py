import streamlit as st
import openai
import os
import json
from typing import List, Dict

# Set your OpenAI API key
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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

# Generate prompt and ask OpenAI
def parse_system_components(answers: List[str], questions: List[str]) -> Dict:
    combined_input = "\n".join([f"Q{i+1}: {q}\nA{i+1}: {a}" for i, (q, a) in enumerate(zip(questions, answers))])
    prompt = f"""
You are a strategy consultant trained in Blue Ocean Strategy, Mental Models, and Systems Thinking.

Given the following business questionnaire, do the following:

1. Extract key insights and patterns from the answers.
2. Identify bottlenecks, opportunities, and reinforcing loops.
3. Suggest a *strategic recommendation* to stand out in the market.

Return a valid JSON in this format:

{{
  "Insights": ["..."],
  "Bottlenecks": ["..."],
  "Opportunities": ["..."],
  "Loops": ["..."],
  "Strategic Recommendation": "..."
}}

Here is the questionnaire:
{combined_input}
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a strategic business analyst."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )
    return response.choices[0].message.content

# Streamlit App
st.set_page_config(page_title="Strategy Agent: Blue Ocean Generator")
st.title("🌊 Strategy Agent: Blue Ocean Generator")
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
            import re
            strategy_text = parse_system_components(answers, questions)

            # Clean output (remove triple backticks if they appear)
            cleaned = re.sub(r"```(json)?", "", strategy_text).strip()
            strategy = json.loads(cleaned)

            st.success("Here's your strategy:")
            st.json(strategy)

        except Exception as e:
            st.error(f"Error parsing strategy JSON: {e}")

