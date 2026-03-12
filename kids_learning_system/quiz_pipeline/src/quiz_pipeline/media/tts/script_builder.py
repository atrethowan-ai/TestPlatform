
def build_tts_script(text: str, tts_style: str = 'default') -> str:
    """
    Build the spoken script for TTS based on style.
    Styles:
      - default: speak text naturally
      - clear_spelling: "Spell the word: ..."
    """
    if tts_style == 'default':
        return text
    elif tts_style == 'clear_spelling':
        # Example: "Spell the word: platform. Platform."
        return f"Spell the word: {text}. {text.capitalize()}."
    else:
        # Fallback to default
        return text
