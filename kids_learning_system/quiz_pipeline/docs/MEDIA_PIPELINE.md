
# Media Pipeline

## TTS
- Preprocess text (see preprocess.py)
- Build spoken script (see script_builder.py)
- Adapter for TTS engine (see adapter.py)
- TTS engine integration (see engine_existing.py)
- Uses external Kokoro ONNX TTS (voice_agent.tts.external_adapter)
- See [TTS_INTEGRATION.md](TTS_INTEGRATION.md) for full details and configuration.

## Images
- SVG generator
- Spatial reasoning image support

See src/quiz_pipeline/media/ for stubs.
