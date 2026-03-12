
def preprocess_audio_short_answer(question: dict) -> dict:
    """
    Preprocesses an audio_short_answer question for TTS.
    Requires 'audioText'. Optionally supports 'ttsStyle'.
    Returns a normalized dict with keys: 'text', 'ttsStyle'.
    """
    if 'audioText' not in question or not question['audioText']:
        raise ValueError("audio_short_answer requires 'audioText' field.")
    text = question['audioText']
    tts_style = question.get('ttsStyle', 'default')
    return {
        'text': text,
        'ttsStyle': tts_style
    }
