=======
# 🌍 Climate Disinformation Classifier
This project was specifically created at Marc’s request for a quick test of the n-to-n framework, that detects and classifies climate-related (mis/dis)information claims by combining:
- **Textual retrieval** (Google Search, GPT web search, fact-check sites)
- **Reverse image search** (Google Images)
- **Multimodal reasoning** (GPT-based reasoning over claim + image + retrieved evidence)

The system outputs a structured **FINAL REPORT** including the claim, evidence from all retrieval sources, and a verdict (`ACCURATE` or `DISINFORMATION`).

---

📂 Project Structure

├── config.py                # API keys, trusted/untrusted sources
├── classifier.py            # Core classifier class
├── main.py                  # Example entry point
├── retrievers/
│   ├── gpt_web.py           # GPT-based web retrieval
│   ├── google_search.py     # Google CSE text search
│   ├── google_reverse_image.py # Reverse image search (Selenium)
│   └── factcheck_search.py  # Fact-check site search
└── reasoning/
    └── reasoner.py          # GPT reasoning engine


## ⚙️ Setup

### 1. Clone repository
```bash
git clone https://github.com/yourusername/patr-desinf06.git
cd climate-disinformation-classifier
```
### 2. Configure API Keys
Edit `config.py` and add your API credentials:
- Google API key and Custom Search Engine (CSE) ID
- OpenAI API key

### 3. Run the Classifier
The main.ipynb is entry point of classifier.py
