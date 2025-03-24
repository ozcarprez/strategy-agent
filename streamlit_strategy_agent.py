import streamlit as st
import openai
import os
import json
from typing import List, Dict

# Cargar clave API desde variable de entorno
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Preguntas con enfoque de systems thinking
def load_questions() -> List[str]:
    return [
        # STOCKS
        "¿Con cuánto capital cuentas actualmente para operar?",
        "¿Qué activos físicos, relaciones o conocimientos clave ya tienes?",
        "¿A quiénes sirves hoy? (clientes principales)",
        "¿Qué relaciones o alianzas tienes con otros actores (proveedores, socios)?",

        # FLOWS
        "¿Cómo entra dinero a tu sistema actualmente? (ventas, inversión, etc.)",
        "¿En qué se te va la mayoría del dinero o recursos?",
        "¿Qué canales usas para conseguir clientes nuevos?",
        "¿Qué operaciones necesitas hacer cada semana para entregar valor?",

        # LOOPS
        "¿Qué hábito o proceso repetitivo parece estar frenando tu crecimiento?",
        "¿Qué cosas haces que, cuando las haces más, generan más resultados?",
        "¿Qué efecto tiene tu falta de recursos sobre el resto de tu sistema?",
        "¿Qué errores o ciclos negativos se repiten y vuelven a aparecer?",

        # CONTEXTO
        "¿Qué cambios grandes están ocurriendo en tu industria o mercado?",
        "¿Qué tendencias, leyes o tecnologías están cambiando las reglas del juego?",
        "¿Qué es lo que tus clientes más te piden o necesitan con urgencia?",
        "¿Quién es tu competencia invisible (la opción que nadie ve pero que gana)?"
    ]

# Función para generar el sistema desde GPT
def parse_system_components(answers: List[str], questions: List[str]) -> Dict:
    combined_input = "\n".join([f"Q{i+1}: {q}\nA{i+1}: {a}" for i, (q, a) in enumerate(zip(questions, answers))])

    prompt = f"""
You are a strategy expert using Systems Thinking.
Given the following business questionnaire, extract and structure:
- Stocks (what the business has: cash, assets, people, partnerships)
- Flows (how value moves: revenue, costs, acquisition, operations)
- Loops (feedback patterns: reinforcing or limiting loops)
- Context (external forces, market trends, customer needs, competitors)

Return a JSON with the structure:
{{
  "Stocks": {{ ... }},
  "Flows": {{ ... }},
  "Loops": {{ ... }},
  "Context": {{ ... }},
  "Summary": {{
    "Insights": [...],
    "Bottlenecks": [...],
    "Opportunities": [...],
    "Strategic Recommendation": "..."
  }}
}}

Also include a Mermaid diagram code block to visualize the system. Use `graph TD` format to represent key relationships between Stocks, Flows, and Loops.

Questionnaire:
{combined_input}
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4
    )

    return json.loads(response.choices[0].message.content)

def generate_notion_template(strategy_data: Dict) -> str:
    template = """# Business System Map (Systems Thinking)

## 🧱 Stocks
{stocks}

## 🔁 Flows
{flows}

## 🔄 Loops
{loops}

## 🌍 Context
{context}

---

## 💡 Insights
{insights}

## ❌ Bottlenecks
{bottlenecks}

## 🚀 Opportunities
{opportunities}

## 🎯 Strategic Recommendation
{recommendation}

## 📊 Visualización del sistema (Mermaid)
```mermaid
{mermaid}
```
"""

    return template.format(
        stocks=json.dumps(strategy_data["Stocks"], indent=2),
        flows=json.dumps(strategy_data["Flows"], indent=2),
        loops=json.dumps(strategy_data["Loops"], indent=2),
        context=json.dumps(strategy_data["Context"], indent=2),
        insights="\n- " + "\n- ".join(strategy_data["Summary"]["Insights"] if isinstance(strategy_data["Summary"]["Insights"], list) else [strategy_data["Summary"]["Insights"]]),
        bottlenecks="\n- " + "\n- ".join(strategy_data["Summary"]["Bottlenecks"] if isinstance(strategy_data["Summary"]["Bottlenecks"], list) else [strategy_data["Summary"]["Bottlenecks"]]),
        opportunities="\n- " + "\n- ".join(strategy_data["Summary"]["Opportunities"] if isinstance(strategy_data["Summary"]["Opportunities"], list) else [strategy_data["Summary"]["Opportunities"]]),
        recommendation=strategy_data["Summary"]["Strategic Recommendation"],
        mermaid=strategy_data.get("Mermaid", "graph TD\n    A[Missing diagram]")
    )

# Streamlit UI
st.set_page_config(page_title="🧠 Strategy Agent: Systems Thinking")
st.title("🧠 Strategy Agent: Systems Thinking")
st.write("Responde estas 16 preguntas para mapear tu negocio como un sistema.")

questions = load_questions()
answers = []

with st.form("strategy_form"):
    for q in questions:
        answers.append(st.text_input(q))
    submitted = st.form_submit_button("Generar Estrategia")

if submitted:
    if "" in answers:
        st.error("Por favor responde todas las preguntas.")
    else:
        with st.spinner("Analizando tu sistema de negocio..."):
            try:
                strategy_data = parse_system_components(answers, questions)
                st.success("🚀 Estrategia generada")
                st.subheader("Resumen")
                st.json(strategy_data)

                # Descargar plantilla para Notion
                notion_text = generate_notion_template(strategy_data)
                safe_text = notion_text.encode("utf-8", "ignore").decode("utf-8")
                st.download_button("Descargar Plantilla para Notion", data=safe_text, file_name="business_system.md")

            except Exception as e:
                st.error(f"Error: {e}")
