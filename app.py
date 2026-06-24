import streamlit as st
import ollama
import json

# ==========================================================
# CONFIG
# ==========================================================

MODEL_NAME = "gemma3:4b"

SYSTEM_PROMPT = """
You are an Expert Prompt Optimizer.

Current Optimization Mode: {mode}

Your task is to improve user prompts while preserving the original intent.

Rules:
1. Keep the user's goal unchanged.
2. Add missing context when appropriate.
3. Improve clarity and specificity.
4. Add useful output requirements.
5. Structure the prompt professionally.
6. Optimize according to the selected mode.
7. Return ONLY the optimized prompt.
"""

ANALYZER_PROMPT = """
Analyze the user's prompt and return JSON only.

Format:

{
  "goal": "",
  "clarity_score": 0,
  "missing_context": [],
  "suggestions": []
}

Return ONLY valid JSON.
Do not include markdown.
Do not include explanations.
"""
INTENT_PROMPT = """
Classify the user's prompt.

Return JSON only:

{
  "intent": "",
  "confidence": 0
}

Possible intents:
- coding
- research
- writing
- image_generation
- business
- academic
- general
"""

GAP_PROMPT = """
Identify missing information in the prompt.

Return JSON only:

{
  "missing_context": []
}
"""

SCORE_PROMPT = """
Score this prompt.

Return JSON only:

{
  "clarity": 0,
  "specificity": 0,
  "context": 0,
  "structure": 0,
  "overall": 0
}

Scores must be between 1 and 10.
"""
CRITIC_PROMPT = """
You are a Prompt Critic.

Analyze the optimized prompt.

Return JSON only:

{
  "strengths": [],
  "weaknesses": [],
  "improvements": []
}
"""

REFINER_PROMPT = """
You are a Prompt Refinement Expert.

Use the critic feedback to improve the prompt.

Return ONLY the final improved prompt.
"""
# ==========================================================
# FUNCTIONS
# ==========================================================

def analyze_prompt(user_prompt):
    try:
        response = ollama.chat(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": ANALYZER_PROMPT
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ]
        )

        content = response["message"]["content"].strip()

        try:
            return json.loads(content)

        except Exception:
            return {
                "goal": "Unknown",
                "clarity_score": "N/A",
                "missing_context": [],
                "suggestions": [
                    "Model returned non-JSON output"
                ]
            }

    except Exception as e:
        return {
            "error": str(e)
        }

def safe_json_parse(text, fallback):
    try:
        return json.loads(text)
    except:
        return fallback


def classify_intent(user_prompt):
    try:
        response = ollama.chat(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": INTENT_PROMPT},
                {"role": "user", "content": user_prompt}
            ]
        )

        return safe_json_parse(
            response["message"]["content"],
            {
                "intent": "general",
                "confidence": 0
            }
        )

    except Exception:
        return {
            "intent": "general",
            "confidence": 0
        }


def detect_gaps(user_prompt):
    try:
        response = ollama.chat(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": GAP_PROMPT},
                {"role": "user", "content": user_prompt}
            ]
        )

        return safe_json_parse(
            response["message"]["content"],
            {
                "missing_context": []
            }
        )

    except Exception:
        return {
            "missing_context": []
        }


def score_prompt(user_prompt):
    try:
        response = ollama.chat(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SCORE_PROMPT},
                {"role": "user", "content": user_prompt}
            ]
        )

        return safe_json_parse(
            response["message"]["content"],
            {
                "clarity": 0,
                "specificity": 0,
                "context": 0,
                "structure": 0,
                "overall": 0
            }
        )

    except Exception:
        return {
            "clarity": 0,
            "specificity": 0,
            "context": 0,
            "structure": 0,
            "overall": 0
        }

def optimize_prompt(user_prompt):

    try:

        intent = classify_intent(user_prompt)
        gaps = detect_gaps(user_prompt)

        enhancement_context = f"""
Intent:
{json.dumps(intent)}

Missing Context:
{json.dumps(gaps)}

Optimize the prompt using this information.
"""

        response = ollama.chat(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT.format(mode=mode)
                },
                {
                    "role": "user",
                    "content": enhancement_context +
                    "\n\nPrompt:\n" +
                    user_prompt
                }
            ]
        )

        return response["message"]["content"]

    except Exception as e:
        return f"ERROR: {str(e)}"

    except Exception as e:

        return {
            "error": str(e)
        }



# ==========================================================
# STREAMLIT UI
# ==========================================================

st.set_page_config(
    page_title="Prompt Optimizer",
    page_icon="🚀",
    layout="wide"
)

st.title("🚀 Local Prompt Optimizer")
st.caption("Powered by Ollama + Gemma 3")

st.markdown("---")

mode = st.selectbox(
    "🎯 Optimization Mode",
    [
        "General",
        "Coding",
        "Research",
        "Academic",
        "Business",
        "Creative",
        "Image Generation"
    ]
)
user_prompt = st.text_area(
    "Enter your prompt",
    height=200,
    placeholder="Example: Build me a website"
)

col1, col2 = st.columns(2)

with col1:
    analyze_btn = st.button("🔍 Analyze Prompt")

with col2:
    optimize_btn = st.button("✨ Optimize Prompt")

# ==========================================================
# ANALYZE
# ==========================================================

if analyze_btn:

    if not user_prompt.strip():
        st.warning("Please enter a prompt.")

    else:

        with st.spinner("Running AI analysis..."):

            intent = classify_intent(user_prompt)
            gaps = detect_gaps(user_prompt)
            score = score_prompt(user_prompt)

        st.subheader("🎯 Intent Classification")
        st.json(intent)

        st.subheader("🧩 Missing Context")
        st.json(gaps)

        st.subheader("📊 Prompt Score")
        st.json(score)

        overall = score.get("overall", 0)

        if isinstance(overall, (int, float)):
            st.progress(min(int(overall * 10), 100))
# ==========================================================
# OPTIMIZE
# ==========================================================
# ==========================================================
# OPTIMIZE
# ==========================================================

if optimize_btn:

    if not user_prompt.strip():
        st.warning("Please enter a prompt.")

    else:

        with st.spinner("Running AI optimization pipeline..."):
            result = optimize_prompt(user_prompt)

        if "error" in result:
            st.error(result["error"])

        else:

            optimized= result
            

            col1, col2 = st.columns(2)

            with col1:
                st.subheader("📝 Original Prompt")

                st.text_area(
                    "Original",
                    value=user_prompt,
                    height=300,
                    disabled=True
                )

            with col2:
                st.subheader("🚀 Optimized Prompt")

                st.text_area(
                    "Optimized",
                    value=optimized,
                    height=300
                )

         

            st.download_button(
                label="📥 Download Prompt",
                data=optimized,
                file_name="optimized_prompt.txt",
                mime="text/plain"
            )

# ==========================================================
# FOOTER
# ==========================================================

st.markdown("---")

st.markdown(
    """
### Features

✅ Intent Classification  
✅ Context Gap Detection  
✅ Prompt Scoring  
✅ Prompt Optimization  
✅ Local AI (Ollama)  
✅ Gemma 3:4B Support  
✅ Download Optimized Prompt  
✅ No API Costs
"""
)