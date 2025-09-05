#gpt_web.py
from config import client

def gpt_web_retrieval(claim: str):
    # System message
    system_prompt = (
        "You are a web search assistant. Your only job is to retrieve factual information from trusted web sources. "
        "Do not use internal knowledge. Do not speculate. Only summarize the results of your web search. "
        "Use bullet points with hyperlinks to the sources."
    )

    # User message
    user_prompt = (
        f"Claim: '{claim}'\n\n"
        "Task: Provide a short summary of your findings in 3–5 concise bullet points.\n"
        "Each bullet must begin with 'Source X:' (e.g., 'Source 1:', 'Source 2:', etc.)\n"
        "Each bullet must include a hyperlink to the source in parentheses.\n"
        "Only use reliable sources such as news organizations, academic institutions, climate fact-checking websites, or government domains.\n"
        "Exclude any information for which a credible source was not found."
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o-search-preview",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        retrieved_info = response.choices[0].message.content
    except Exception as e:
        print(f"GPT search failed for claim: {e}")
        retrieved_info = "Search failed."

    return retrieved_info
