# streamlit_strategy_agent.py (extendido con descarga de plantilla tipo Notion)

import streamlit as st
import openai
import os
import json
import re
from typing import List, Dict
from datetime import datetime
from io import StringIO

# Set OpenAI API key
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Load business questions
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
        "What's your monthly revenue (estimate is OK)?",
        "What’s your biggest bottleneck?",
        "What sets you apart (if anything)?",
        "What frustrates your customers the most?",
        "What’s something customers keep asking for?",
        "Who are your top competitors?",
        "What trends or changes are affecting your industry?",
        "What are your goals for the next 12 months?"
    ]

# Parse system components and generate strategy

def parse_system_components(answers: List[str], questions: List[str]) -> Dict:
    combined_input = "\n".join([f"Q{i+1}: {q}\nA{i+1}: {a}" for i, (q, a) in enumerate(zip(questions, answers))])

    prompt = f"""
You are a strategy consultant trained in Blue Ocean Strategy, Mental Models, and Systems Thinking.

Given the following business questionnaire, do the following:

1. Extract key insights and patterns from the answers.
2. Identify bottlenecks, opportunities, and reinforcing loops.
3. Suggest a strategic recommendation to stand out in the market.

Return a valid JSON in this format:
{
  "Stocks": {...},
  "Flows": {...},
  "Loops": {...},
  "Context": {...},
  "Insights": [...],
  "Bottlenecks": [...],
  "Opportunities": [...],
  "Strategic Recommendation": "..."
}

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
    return json.loads(response.choices[0].message.content)

# Generate markdown for Notion/Canvas

def generate_notion_markdown(data: dict) -> str:
    def section(title, content):
        return f"## {title}\n\n{content}\n"

    def list_block(items):
        return "\n".join([f"- {item}" for item in items])

    md = f"# Business Strategy Canvas\nGenerated on {datetime.now().strftime('%Y-%m-%d')}\n\n"

    md += section("📦 Stocks",
        f"**Cash:** {data['Stocks']['cash']}\n\n"
        f"**Assets:** {data['Stocks']['assets']}\n\n"
        f"**People:**\n{list_block(data['Stocks']['people'])}\n\n"
        f"**Partnerships:**\n{list_block(data['Stocks']['partnerships'])}"
    )

    md += section("🔁 Flows",
        f"**Revenue:** {data['Flows']['revenue']}\n\n"
        f"**Costs:**\n{list_block(data['Flows']['costs'])}\n\n"
        f"**Acquisition Channels:**\n{list_block(data['Flows']['acquisition channels'])}\n\n"
        f"**Operations Bottleneck:** {data['Flows']['ops']['bottleneck']}"
    )

    loops = data['Loops']['reinforcing patterns']
    md += section("🔄 Loops",
        "\n".join([f"**{k}** leads to:\n{list_block(v)}\n" for k, v in loops.items()])
    )

    context = data['Context']
    md += section("🌐 Context",
        f"**Trends:**\n{list_block(context['trends'])}\n\n"
        f"**Customer Needs:**\n{list_block(context['customer needs'])}\n\n"
        f"**Competition:**\n{list_block(context['competition'])}"
    )

    md += section("💡 Insights", list_block(data.get("Insights", [])))
    md += section("🧱 Bottlenecks", list_block(data.get("Bottlenecks", [])))
    md += section("📈 Opportunities", list_block(data.get("Opportunities", [])))
    md += section("🚀 Strategic Recommendation", data.get("Strategic Recommendation", "N/A"))

    return md

# Streamlit UI
st.set_page_config(page_title="Strategy Agent: Blue Ocean Generator")
st.title("🌊 Strategy Agent: Blue Ocean Generator")
st.write("Answer these 16 questions and get your custom strategy.")

questions = load_questions()
answers = []

with st.form("strategy_form"):
    for q in questions:
        answers.append(st.text_input(q))
    submitted = st.form_submit_button("Generate Strategy")

if submitted:
    if "" in answers:
        st.error("Please answer all the questions.")
    else:
        try:
            strategy_data = parse_system_components(answers, questions)
            st.success("Here's your strategy:")
            st.json(strategy_data)

            # Generate markdown and offer download
            md_content = generate_notion_markdown(strategy_data)
            md_file = StringIO(md_content)
            st.download_button(
                label="📥 Download Strategy Template (Notion/Markdown)",
                data=md_file,
                file_name="strategy_canvas.md",
                mime="text/markdown"
            )

        except Exception as e:
            st.error(f"Error: {e}")
