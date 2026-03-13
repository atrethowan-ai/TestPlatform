
def build_tts_script(text: str, tts_style: str = 'default') -> str:
    """
    Build the spoken script for TTS based on style.
    Styles:
      - default: speak text naturally
      - clear_spelling: "Spell the word: ..."
    """
    # Always use audioText verbatim, regardless of tts_style
    return text
