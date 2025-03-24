import streamlit as st
import openai
import os
import json
from typing import List, Dict

# Configurar clave de API
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Preguntas para construir el Flywheel
def load_flywheel_questions() -> List[str]:
    return [
        "🔍 ¿Qué actividad en tu negocio, cuando la haces consistentemente, genera resultados positivos?",
        "⚖️ ¿Qué resultados te dan energía o recursos para seguir impulsando el sistema?",
        "🚀 ¿Qué aspecto de tu negocio ya tiene tracción natural (crece sin mucho esfuerzo)?",
        "🤝 ¿Qué valor entregas que hace que los clientes regresen o recomienden tu producto?",
        "🦾 ¿Qué fortalezas o capacidades únicas tienes que podrías aprovechar más?",
        "🔁 ¿Qué acciones tienen un efecto compuesto si las haces repetidamente?",
        "👍 ¿Qué es lo que tus clientes más valoran y te reconocen?",
        "▶️ Paso 1: ¿Cuál es el primer paso clave que detona todo lo demás?",
        "⏳ Paso 2: ¿Qué ocurre después que genera valor y satisfacción?",
        "📈 Paso 3: ¿Qué pasa que hace más probable que los clientes regresen o que tú reinviertas?",
        "💪 Paso 4: ¿Qué haces con ese impulso para hacerlo crecer aún más?",
        "🔄 Paso 5: ¿Qué parte se repite o se automatiza para mantener el ciclo?",
        "❌ ¿Qué parte de tu sistema actual detiene el impulso?",
        "💡 ¿Qué harías si tuvieras que duplicar resultados sin duplicar esfuerzo?",
        "❓ ¿Qué no estás haciendo hoy que, si lo hicieras, haría una gran diferencia?"
    ]

# Procesar respuestas para generar flywheel
def parse_flywheel(answers: List[str], questions: List[str]) -> Dict:
    combined_input = "\n".join([f"Q{i+1}: {q}\nA{i+1}: {a}" for i, (q, a) in enumerate(zip(questions, answers))])

    prompt = f"""
Eres un consultor experto en estrategia con enfoque en Flywheel (modelo de Jim Collins).
Dado el siguiente cuestionario, construye lo siguiente:
1. Un resumen de impulso del negocio (FlywheelSummary).
2. Los pasos del flywheel en secuencia.
3. Un roadmap por fases: corto, mediano y largo plazo.

Responde SOLO en formato JSON con estas claves:
- FlywheelSummary
- FlywheelSteps
- Roadmap

Cuestionario:
{combined_input}
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5
    )

    return json.loads(response.choices[0].message.content)

# Interfaz de usuario
st.set_page_config(page_title="Flywheel Generator")
st.title("🌬️ Generador de Flywheel")
st.write("Responde estas preguntas para mapear tu rueda impulsora según el modelo de Jim Collins.")

questions = load_flywheel_questions()
answers = []

with st.form("flywheel_form"):
    for q in questions:
        answers.append(st.text_area(q))
    submitted = st.form_submit_button("Generar Flywheel")

if submitted:
    if "" in answers:
        st.error("Por favor responde todas las preguntas.")
    else:
        with st.spinner("Analizando tu sistema de impulso..."):
            try:
                result = parse_flywheel(answers, questions)
                st.success("✅ Flywheel generado")

                st.subheader("Resumen del Flywheel")
                st.markdown(result["FlywheelSummary"])

                st.subheader("🔄 Pasos del Flywheel")
                for i, step in enumerate(result["FlywheelSteps"], 1):
                    st.markdown(f"**Paso {i}:** {step}")

                st.subheader("📅 Roadmap")
                for phase, items in result["Roadmap"].items():
                    st.markdown(f"### {phase}")
                    if isinstance(items, list):
                        for item in items:
                            st.markdown(f"- {item}")
                    else:
                        st.markdown(f"- {items}")

            except Exception as e:
                st.error(f"Error: {e}")
