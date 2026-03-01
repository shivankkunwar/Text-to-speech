#!/usr/bin/env python3
"""
Voice Preview Generator
Test different TTS voices before generating the full audiobook.

Usage:
    python test_voices.py
    
This generates sample MP3s with different voices so you can compare.
"""

import asyncio
from pathlib import Path
import edge_tts

# Sample technical text (contains tricky terms)
SAMPLE_TEXT = """
The inference pipeline leverages a high-performance GPU cluster, 
utilizing CUDA cores to accelerate the LLM computations within the 
Kubernetes architecture. The system integrates seamlessly with PyTorch,
enabling efficient batch processing through the API. For optimal performance,
we configure the KV cache with FP16 precision and deploy across multiple
nodes using container orchestration. The ASR module handles automatic
speech recognition, while the TTS engine provides text to speech output.
"""

# Top voices to test (from voice-research.md)
VOICES = [
    {
        "id": "en-US-AvaMultilingualNeural",
        "name": "Ava (Multilingual)",
        "desc": "Best overall - natural female, excellent for technical",
        "rate": "-5%",
        "pitch": "+0Hz"
    },
    {
        "id": "en-US-ChristopherNeural",
        "name": "Christopher",
        "desc": "Best male - deep, calm, audiobook narrator quality",
        "rate": "+8%",
        "pitch": "+0Hz"
    },
    {
        "id": "en-GB-SoniaNeural",
        "name": "Sonia (British)",
        "desc": "Crisp articulation, great for acronyms",
        "rate": "-2%",
        "pitch": "+0Hz"
    },
    {
        "id": "en-US-AndrewMultilingualNeural",
        "name": "Andrew (Multilingual)",
        "desc": "Professional male, broadcast quality",
        "rate": "-5%",
        "pitch": "+0Hz"
    },
    {
        "id": "en-US-EmmaMultilingualNeural",
        "name": "Emma (Multilingual)",
        "desc": "Conversational female, approachable",
        "rate": "+0%",
        "pitch": "+0Hz"
    },
    {
        "id": "en-IN-NeerjaNeural",
        "name": "Neerja (Indian)",
        "desc": "Original default - Indian English female",
        "rate": "+5%",
        "pitch": "+0Hz"
    },
]

async def generate_preview(voice_config):
    """Generate a preview MP3 for a given voice."""
    voice_id = voice_config["id"]
    rate = voice_config["rate"]
    pitch = voice_config["pitch"]
    
    output_path = Path("audiobook") / f"preview_{voice_id.split('-')[-1]}.mp3"
    output_path.parent.mkdir(exist_ok=True)
    
    print(f"Generating: {voice_config['name']}...")
    
    communicate = edge_tts.Communicate(
        text=SAMPLE_TEXT,
        voice=voice_id,
        rate=rate,
        pitch=pitch
    )
    
    await communicate.save(str(output_path))
    print(f"  [OK] Saved: {output_path.name}")
    
    return output_path

async def main():
    print("=" * 60)
    print("VOICE PREVIEW GENERATOR")
    print("=" * 60)
    print("\nGenerating sample audio with different voices...\n")
    
    generated = []
    for voice in VOICES:
        try:
            path = await generate_preview(voice)
            generated.append((voice, path))
        except Exception as e:
            print(f"  [FAIL] Failed: {e}")
    
    print("\n" + "=" * 60)
    print("GENERATED PREVIEWS")
    print("=" * 60)
    
    for voice, path in generated:
        print(f"\n[VOICE] {voice['name']}")
        print(f"   File: {path}")
        print(f"   Info: {voice['desc']}")
        print(f"   Settings: rate={voice['rate']}, pitch={voice['pitch']}")
    
    print("\n" + "=" * 60)
    print("Listen to the previews and choose your favorite!")
    print("\nTo use a voice in the full generation:")
    print("   python generate_audiobook.py --voice <voice-id> --rate <rate>")
    print("\nExample:")
    print("   python generate_audiobook.py --voice en-US-AvaMultilingualNeural --rate -5%")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
