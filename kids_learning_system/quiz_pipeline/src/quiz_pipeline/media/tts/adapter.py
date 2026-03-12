
from .preprocess import preprocess_audio_short_answer
from .script_builder import build_tts_script
from .engine_existing import ExistingTTSEngine
import os

def generate_audio_for_question(question: dict, output_path: str, voice: str = None) -> str:
    """
    Generate TTS audio for an audio_short_answer question.
    Args:
        question (dict): Authoring question dict.
        output_path (str): Path to write the WAV file.
        voice (str|None): Optional voice selection.
    Returns:
        str: Path to the generated WAV file.
    """
    # Validate and preprocess
    norm = preprocess_audio_short_answer(question)
    # Build script
    script = build_tts_script(norm['text'], norm.get('ttsStyle', 'default'))
    # Synthesize
    engine = ExistingTTSEngine()
    wav_path = output_path
    # Ensure output directory exists
    os.makedirs(os.path.dirname(wav_path), exist_ok=True)
    result_path = engine.synthesize(script, wav_path, voice=voice)
    return result_path
