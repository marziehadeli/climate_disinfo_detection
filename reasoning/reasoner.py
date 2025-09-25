# reasoning/reasoner.py
from config import client

class GPTReasoner:
    def __init__(self, model="gpt-4o"):
        self.model = model

    def build_prompt(self, claim: str, evidence: dict) -> str:
        parts = [f"CLAIM: \"{claim}\""]

        # === 1. GPT Web ===
        gpt_info = evidence.get("gpt_web")
        if gpt_info:
            parts.append(f"\n---\nEVIDENCE (from GPT Web Search):\n{gpt_info.strip()}")

        # === 2. Reverse Image ===
        reverse_info = evidence.get("reverse_image", [])
        if reverse_info:
            exacts = [r for r in reverse_info if r.get("label") == "[Exact match]"]
            abouts = [r for r in reverse_info if r.get("label") == "[About this image]"]
            visuals = [r for r in reverse_info if r.get("label") == "[Visual match]"]

            if exacts:
                r = exacts[0]
                parts.append(
                    f"\n---\nVISUAL CONTEXT [Exact match]:\n"
                    f"{r.get('title','')} ({r.get('href','')})\n{r.get('body','')}"
                )
            elif abouts:
                earliest = abouts[0]
                parts.append(
                    f"\n---\nABOUT THIS IMAGE (Earliest: {earliest.get('date','')}):\n"
                    f"{earliest.get('title','[No title]')} ({earliest.get('href','')})"
                )
            elif visuals:
                r = visuals[0]
                parts.append(
                    f"\n---\nVISUAL CONTEXT [Visual match]:\n"
                    f"{r.get('title','')} ({r.get('href','')})\n{r.get('body','')}"
                )

        # === 3. Google Search ===
        google_info = evidence.get("google_search", [])
        if google_info:
            snippets = [
                f"{r.get('title','')} ({r.get('link','')})\n{r.get('snippet','')}"
                for r in google_info
            ]
            parts.append("\n---\nGOOGLE SEARCH SNIPPETS (use carefully):\n" + "\n".join(snippets))

        # === 4. Fact-check Sites ===
        factcheck_info = evidence.get("fact_check", [])
        if factcheck_info:
            snippets = [
                f"{r.get('title','')} ({r.get('link','')})\n{r.get('snippet','')}"
                for r in factcheck_info
            ]
            parts.append("\n---\nFACT-CHECK EVIDENCE:\n" + "\n".join(snippets))

        # === Final reasoning instructions ===
        cod_steps = """
---
You are a fact-checking assistant. Analyze the claim and the provided image using the combined evidence.

Guidelines:
- Exact matches are strongest (high confidence).
- For "About this image", the earliest date usually indicates the original context.
- Be cautious with Visual matches (may be misleading).
- Fact-check sites are reliable.
- Google Search snippets vary in credibility — cross-check before relying.
- Also analyze the uploaded IMAGE directly (visual content matters).

**STEP 1: DRAFT**
Summarize in 5 words your interpretation using the strongest evidence.

**STEP 2: REFLECT**
Check for contradictions, gaps, or uncertainty.

**STEP 3: FINAL ANSWER**
Respond in this format:

VERDICT: [ACCURATE / DISINFORMATION]
EXPLANATION: [1–2 concise sentences based only on the provided evidence + the image]
""".strip()

        parts.append(cod_steps)
        return "\n\n".join(parts)

    def run(self, claim: str, evidence: dict, image_path: str = None) -> str:
        """Send prompt + evidence (+ image if provided) to GPT and return verdict safely"""
        try:
            prompt = self.build_prompt(claim, evidence)
        except Exception as e:
            return f"[Error building prompt: {e}]"

        try:
            # Prepare multimodal input
            content = [{"type": "text", "text": prompt}]
            if image_path:  # attach image if available
                import base64
                with open(image_path, "rb") as f:
                    img_b64 = base64.b64encode(f.read()).decode("utf-8")
                content.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}
                })

            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful fact-checking assistant."},
                    {"role": "user", "content": content},
                ],
                temperature=0,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"[Error during reasoning: {e}]"
