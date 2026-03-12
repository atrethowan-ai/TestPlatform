
# Real TTS engine integration using Kokoro ONNX TTS (voice_agent)
try:
    from voice_agent.tts.external_adapter import synthesize_to_file
except ImportError:
    synthesize_to_file = None

class ExistingTTSEngine:
    """
    Wrapper for the external Kokoro ONNX TTS engine.
    """
    def __init__(self):
        if synthesize_to_file is None:
            raise ImportError("voice_agent.tts.external_adapter.synthesize_to_file not found. Ensure voice_agent is installed and on PYTHONPATH.")

    def synthesize(self, text: str, output_path: str, voice: str | None = None) -> str:
        """
        Synthesize speech from text to a WAV file using the external TTS engine.
        Args:
            text (str): The text to synthesize.
            output_path (str): Path to write the WAV file.
            voice (str|None): Optional voice selection.
        Returns:
            str: Path to the generated WAV file.
        """
        return synthesize_to_file(text=text, output_path=output_path, voice=voice)
