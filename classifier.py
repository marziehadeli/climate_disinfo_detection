from retrievers.gpt_web import gpt_web_retrieval
from retrievers.google_search import google_search
from retrievers.google_reverse_image import google_reverse_image
from retrievers.factcheck_search import search_fact_check
from reasoning.reasoner import GPTReasoner
from config import GOOGLE_API_KEY, GOOGLE_CSE_ID

class ClaimClassifier:
    def __init__(self):
        self.reasoner = GPTReasoner()

    def classify(self, input_data):
        image, text = input_data

        # Collect evidence
        evidence = {
            "gpt_web": gpt_web_retrieval(text),
            "google_search": google_search(text, api_key=GOOGLE_API_KEY, cse_id=GOOGLE_CSE_ID),
            "reverse_image": google_reverse_image(image),
            "fact_check": search_fact_check(text, api_key=GOOGLE_API_KEY, cse_id=GOOGLE_CSE_ID),
        }

        # Run reasoning
        verdict = self.reasoner.run(text, evidence, image)

        return {
            "claim": text,
            "evidence": evidence,
            "verdict": verdict,
        }
