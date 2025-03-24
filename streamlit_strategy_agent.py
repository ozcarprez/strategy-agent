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
        # Fundamentos
        "\U0001F50D ¿Qué actividad en tu negocio, cuando la haces consistentemente, genera resultados positivos?",
        "\u2696️ ¿Qué resultados te dan energía o recursos para seguir impulsando el sistema?",
        "\U0001F680 ¿Qué aspecto de tu negocio ya tiene tracción natural (crece sin mucho esfuerzo)?",
        "\U0001F91D ¿Qué valor entregas que hace que los clientes regresen o recomienden tu producto?",
        "\U0001F9BE ¿Qué fortalezas o capacidades únicas tienes que podrías aprovechar más?",
        "\U0001F501 ¿Qué acciones tienen un efecto compuesto si las haces repetidamente?",
        "\U0001F44D ¿Qué es lo que tus clientes más valoran y te reconocen?",

        # Secuencia del Flywheel
        "\u25B6️ Paso 1: ¿Cuál es el primer paso clave que detona todo lo demás?",
        "\u23F3 Paso 2: ¿Qué ocurre después que genera valor y satisfacción?",
        "\U0001F4C8 Paso 3: ¿Qué pasa que hace más probable que los clientes regresen o que tú reinviertas?",
        "\U0001F4AA Paso 4: ¿Qué haces con ese impulso para hacerlo crecer aún más?",
        "\U0001F504 Paso 5: ¿Qué parte se repite o se automatiza para mantener el ciclo?",

        # Obstáculos y claridad
        "\u274C ¿Qué parte de tu sistema actual detiene el impulso?",
        "\U0001F4A1 ¿Qué harías si tuvieras que duplicar resultados sin duplicar esfuerzo?",
        "\u2753 ¿Qué no estás haciendo hoy que, si lo hicieras, haría una gran diferencia?"
    ]

# Procesar respuestas para generar flywheel

def parse_flywheel(answers: List[str], questions: List[str]) -> Dict:
    combined_input = "\n".join([f"Q{i+1}: {q}\nA{i+1}: {a}" for i, (q, a) in enumerate(zip(questions, answers))])

    prompt = f"""
Eres un consultor experto en estrategia con enfoque en Flywheel (modelo de Jim Collins).
Dado el siguiente cuestionario, construye lo siguiente:
1. Un resumen de impulso del negocio (Flywheel Summary).
2. Los pasos del flywheel en secuencia.
3. Un roadmap por fases: corto, mediano y largo plazo.
4. Código Mermaid para visualizar el flywheel como diagrama.

Responde SOLO en formato JSON con estas claves:
- FlywheelSummary
- FlywheelSteps
- Roadmap
- MermaidDiagram

Cuestionario:
{combined_input}
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5
    )

    return json.loads(response.choices[0].message.content)

# UI
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
                st.success("Flywheel generado")

                st.subheader("Resumen del Flywheel")
                st.markdown(result["FlywheelSummary"])

                st.subheader("🔄 Pasos del Flywheel")
                for i, step in enumerate(result["FlywheelSteps"], 1):
                    st.markdown(f"**Paso {i}:** {step}")

                st.subheader("📅 Roadmap")
                for phase, items in result["Roadmap"].items():
                    st.markdown(f"### {phase}")
                    for item in items:
                        st.markdown(f"- {item}")

                st.subheader("🎭 Visualización (Mermaid)")
                st.code(result["MermaidDiagram"], language="mermaid")

            except Exception as e:
                st.error(f"Error: {e}")
