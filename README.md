=======
# 🌍 Climate Disinformation Detection

This repository contains a prototype system designed to detect and classify climate-related **misinformation / disinformation** claims using a multimodal approach. The system integrates:

- **Textual retrieval** (Google Search, GPT-based web search, fact-check sites)  
- **Reverse image search** (Google Images via Selenium)  
- **Multimodal reasoning** (GPT-based reasoning over claim + image + retrieved evidence)  

It produces a structured **final report** that includes:  
- The original claim  
- Evidence collected from all retrieval sources  
- A verdict: `ACCURATE` or `DISINFORMATION`  
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
├──reasoning/
│   └── reasoner.py          # GPT reasoning engine
├── tests/
│ └── test_classifier.py # Unit tests (no real API calls)
└── README.md

## ⚙️ Setup for Running with APIs

### 1. Clone repository
```bash
git clone https://github.com/marziehadeli/climate_disinfo_detection.git
cd climate_disinfo_detection
```
### 2. Configure API Keys
Edit `config.py` and add your API credentials:
- Google API key and Custom Search Engine (CSE) ID
- OpenAI API key

### 3. Run the Classifier
The main.ipynb is entry point of classifier.py


## ⚙️ Testing (without APIs)

### 1. Clone repository
```bash
git clone https://github.com/marziehadeli/climate_disinfo_detection.git
cd climate_disinfo_detection
```
### 2. Tests are fully mocked (no API calls). Run them with:
python -m pytest -v
