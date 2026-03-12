
"""
Isolated test for QuizTTSAdapter (Kokoro TTS + ffmpeg integration).

This test verifies:
1. Call to external Kokoro TTS adapter
2. Temporary WAV generation
3. WAV to MP3 conversion via ffmpeg
4. Temporary WAV deletion
5. Return of final MP3 path

Run as pytest:
  pytest tests/test_tts_adapter.py -v -s

Run standalone:
  python tests/test_tts_adapter.py
"""

import sys
import logging
from pathlib import Path
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)

# Ensure src/ is in sys.path for imports
SRC_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

# Import QuizTTSAdapter
try:
    from quiz_pipeline.media.tts.tts_adapter import QuizTTSAdapter
    ADAPTER_AVAILABLE = True
except ImportError as e:
    ADAPTER_AVAILABLE = False
    IMPORT_ERROR = str(e)


def test_tts_adapter_kokoro_isolated():
    """
    Test QuizTTSAdapter end-to-end:
    1. Calls Kokoro TTS to generate WAV
    2. Converts WAV to MP3 using ffmpeg
    3. Deletes temp WAV
    4. Returns MP3 path
    """
    # Define output directory
    quiz_pipeline_dir = Path(__file__).parent.parent
    output_dir = quiz_pipeline_dir / 'work' / 'test_output'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save current working directory
    original_cwd = os.getcwd()
    
    text = "Spell the word: platform. Platform."
    filename = "test_tts"
    
    print("\n" + "="*70)
    print("TTS ADAPTER ISOLATED TEST")
    print("="*70)
    print(f"Text: {text}")
    print(f"Output dir: {output_dir}")
    print(f"Filename: {filename}")
    print("-"*70)
    
    # Check if adapter is available
    if not ADAPTER_AVAILABLE:
        print(f"FAIL: QuizTTSAdapter import failed")
        print(f"  Error: {IMPORT_ERROR}")
        return False
    
    mp3_path = None
    wav_path = output_dir / f"{filename}.wav"
    expected_mp3_path = output_dir / f"{filename}.mp3"
    
    try:
        # STEP 1: Initialize adapter and call Kokoro TTS
        print("1. Initializing QuizTTSAdapter...")
        
        # Find voice_agent directory
        voice_agent_dir = Path("C:/DEV/260305_ComplexVoiceAgent")
        if not voice_agent_dir.exists():
            # Fallback to parent navigation
            voice_agent_dir = Path(original_cwd).parent.parent.parent.parent / "260305_ComplexVoiceAgent"
        
        voice_agent_dir = voice_agent_dir.resolve()  # Resolve to absolute path
        print(f"   Voice agent directory: {voice_agent_dir}")
        
        if not voice_agent_dir.exists():
            print(f"   ✗ voice_agent directory not found")
            raise FileNotFoundError(f"voice_agent directory not found at {voice_agent_dir}")
        
        # Initialize adapter (just the object, not the TTS engine)
        adapter = QuizTTSAdapter()
        print("   ✓ Adapter initialized")
        
        print("2. Calling Kokoro TTS to generate WAV...")
        print(f"   Output directory: {output_dir}")
        
        # Change to voice_agent directory for TTS synthesis (lazy initialization)
        print(f"   Switching to voice_agent for TTS synthesis...")
        os.chdir(voice_agent_dir)
        
        try:
            mp3_path = adapter.synthesize_to_mp3(text, output_dir, filename)
        finally:
            # Always restore original directory
            os.chdir(original_cwd)
        
        print("   ✓ TTS synthesis completed")
        
        # STEP 2: Verify MP3 exists
        print("3. Verifying MP3 file exists...")
        if not mp3_path.exists():
            print(f"   ✗ MP3 file not created: {mp3_path}")
            return False
        print(f"   ✓ MP3 created: {mp3_path}")
        print(f"   ✓ MP3 size: {mp3_path.stat().st_size} bytes")
        
        # STEP 3: Verify WAV was deleted
        print("4. Verifying temporary WAV was deleted...")
        if wav_path.exists():
            print(f"   ✗ Temp WAV not deleted: {wav_path}")
            return False
        print(f"   ✓ Temp WAV deleted (not found at {wav_path})")
        
        # STEP 4: Verify returned path matches expected
        print("5. Verifying returned path matches expected...")
        if mp3_path != expected_mp3_path:
            print(f"   ✗ Path mismatch")
            print(f"     Expected: {expected_mp3_path}")
            print(f"     Got:      {mp3_path}")
            return False
        if not (mp3_path.parent == output_dir and mp3_path.name == f"{filename}.mp3"):
            print(f"   ✗ Path structure incorrect")
            return False
        print(f"   ✓ Path matches: {mp3_path}")
        
        print("-"*70)
        print("✓ ALL TESTS PASSED")
        print(f"✓ Final MP3 path: {mp3_path}")
        print("="*70)
        return True
        
    except ImportError as e:
        print(f"FAIL: Missing dependency")
        print(f"  Error: {e}")
        print(f"  Diagnostic: Ensure 'voice_agent' is installed and on PYTHONPATH")
        return False
    except FileNotFoundError as e:
        if "configs/app.yaml" in str(e):
            print(f"FAIL: Kokoro TTS config not found")
            print(f"  Error: {e}")
            print(f"  Diagnostic: Kokoro TTS requires 'configs/app.yaml' to be present")
            print(f"  Current working directory: {os.getcwd()}")
            print(f"  Expected: Run from directory containing 'configs/app.yaml'")
            print(f"  Solution: Ensure voice_agent config files are accessible")
        else:
            print(f"FAIL: File not found")
            print(f"  Error: {e}")
        return False
    except RuntimeError as e:
        print(f"FAIL: Runtime error during TTS/ffmpeg")
        print(f"  Error: {e}")
        if "ffmpeg" in str(e).lower():
            print(f"  Diagnostic: ffmpeg not found. Install ffmpeg and add to PATH")
        else:
            print(f"  Diagnostic: Check voice_agent Kokoro TTS installation")
        return False
    except Exception as e:
        print(f"FAIL: Unexpected error")
        print(f"  Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Restore original working directory
        os.chdir(original_cwd)


def test_tts_adapter_kokoro(tmp_path=None):
    """
    Pytest wrapper for test_tts_adapter_kokoro_isolated.
    Uses tmp_path fixture if running under pytest.
    """
    try:
        import pytest
    except ImportError:
        pytest = None
    
    # If pytest tmp_path is available, also test with it
    if tmp_path is not None:
        print("\nRunning with pytest tmp_path...")
        try:
            quiz_pipeline_dir = Path(__file__).parent.parent
            adapter = QuizTTSAdapter()
            mp3 = adapter.synthesize_to_mp3(
                "Spell the word: platform. Platform.",
                tmp_path,
                "pytest_test"
            )
            assert mp3.exists()
            assert not (tmp_path / "pytest_test.wav").exists()
            print("✓ pytest tmp_path test passed")
        except Exception as e:
            if pytest:
                pytest.fail(f"pytest tmp_path test failed: {e}")
            else:
                print(f"pytest tmp_path test failed: {e}")
    
    # Run the main test
    success = test_tts_adapter_kokoro_isolated()
    
    # pytest assertion
    try:
        import pytest
        assert success, "TTS adapter test failed"
    except ImportError:
        pass
    
    return success


if __name__ == "__main__":
    # Run standalone
    success = test_tts_adapter_kokoro_isolated()
    sys.exit(0 if success else 1)
