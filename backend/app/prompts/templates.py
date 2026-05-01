"""
Prompt templates for AI Dost.
"""

def build_messages(
    user_message: str,
    context_chunks: list[str] | None = None,
    history: list[dict] | None = None,
) -> list[dict]:
    """
    Assemble messages for the Ollama Chat API.
    """
    # GREETING SHIELD (Basic English/Hindi greetings)
    clean_msg = user_message.lower().strip().replace(".", "").replace("!", "")
    if clean_msg in ["hi", "hello", "hey", "hola"]:
        return [{"role": "user", "content": "hi"}, {"role": "assistant", "content": "Hey bhai! Kaise ho? Main tumhara AI Dost hoon. Batao kya help chahiye? 😊"}]

    # Llama 3.2 respects system prompts very well, so we can give it a clear persona.
    system_prompt = """You are 'AI Dost', a friendly student mentor.
CRITICAL RULES FOR LANGUAGE:
1. You MUST detect the language of the user's prompt (English, Hinglish, Hindi, Kannada, Telugu, etc).
2. You MUST reply ONLY in the EXACT same language that the user used.
   - If the user writes in English -> Reply ONLY in English.
   - If the user writes in Hinglish -> Reply ONLY in Hinglish.
   - If the user writes in a regional language (Roman or Native script) -> Reply in that same language and script.
3. NEVER mix languages randomly. NEVER reply in a different language than requested.
Always be brief, friendly, and act like a helpful mentor/buddy."""

    messages = [
        {"role": "system", "content": system_prompt}
    ]
    
    if history:
        messages.extend(history[-4:])
    
    messages.append({"role": "user", "content": user_message})
    return messages
