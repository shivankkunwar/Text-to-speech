"""
Audiobook Generator for "Inference Engineering"
Converts TTS-ready text chapters into high-quality MP3 audiobook.

Usage:
    pip install edge-tts tqdm
    python generate_audiobook.py

Output:
    - audiobook/chapter_XX.mp3 - Individual chapter files
    - audiobook/full_audiobook.mp3 - Complete audiobook (if pydub available)
"""

import asyncio
from pathlib import Path
import edge_tts
from tqdm import tqdm
import sys
import argparse
import re

try:
    from pydub import AudioSegment
    HAS_PYDUB = True
except ImportError:
    HAS_PYDUB = False
    print("Note: pydub not available. Skipping full audiobook combination.")
    print("Individual chapter MP3s will still be generated.\n")

# Best voice for technical audiobooks (per voice-research.md)
# en-US-AvaMultilingualNeural is ranked #1 for long-form technical content
# - Superior phonetic normalization for terms like "Kubernetes", "CUDA", "PyTorch"
# - Natural pause structure (~350ms between clauses)
# - Balanced acoustic intensity prevents listener fatigue
VOICE = "en-US-AvaMultilingualNeural"

# Alternative top voices (from research):
# en-US-ChristopherNeural - Best male voice, deep & calm (add +8% rate)
# en-GB-SoniaNeural - Crisp British articulation, excellent for acronyms
# en-US-AndrewMultilingualNeural - Professional male, broadcast quality
# en-US-EmmaMultilingualNeural - Conversational female, approachable

# Speech rate: -5% for Ava (slower = better cognitive retention for dense material)
# Research shows 130-160 WPM is optimal for technical content
RATE = "-5%"

# Pitch adjustment (usually best at 0Hz for Multilingual voices)
PITCH = "+0Hz"

async def text_to_speech(input_txt: Path, output_mp3: Path, voice: str = VOICE, rate: str = RATE, pitch: str = PITCH) -> bool:
    """
    Convert a text file to speech using edge-tts.
    
    Args:
        input_txt: Path to input text file
        output_mp3: Path to output MP3 file
        voice: TTS voice to use
        rate: Speech rate adjustment (e.g., "-5%", "+10%")
        pitch: Pitch adjustment (e.g., "+0Hz", "-10Hz")
        
    Returns:
        True if successful, False otherwise
    """
    try:
        text = input_txt.read_text(encoding="utf-8").strip()
        if not text:
            print(f"  Warning: Empty file {input_txt}")
            return False
        
        communicate = edge_tts.Communicate(text=text, voice=voice, rate=rate, pitch=pitch)
        await communicate.save(str(output_mp3))
        return True
    except Exception as e:
        print(f"  Error processing {input_txt}: {e}")
        return False


async def main(voice: str = VOICE, rate: str = RATE, pitch: str = PITCH):
    """Main function to generate the complete audiobook.
    
    Args:
        voice: TTS voice to use
        rate: Speech rate adjustment
        pitch: Pitch adjustment
    """
    tts_dir = Path("tts_ready")
    audio_dir = Path("audiobook")
    
    # Create output directory
    audio_dir.mkdir(exist_ok=True)
    
    # Find all chapter files
    chapter_files = sorted(tts_dir.glob("chapter_*.txt"))

    if not chapter_files:
        print("Error: No chapter files found in tts_ready/")
        print("Please run process_book.py first to generate TTS-ready chapters.")
        sys.exit(1)

    print(f"Found {len(chapter_files)} chapters.")
    print(f"Starting TTS conversion with voice: {voice}")
    print(f"Rate: {rate} | Pitch: {pitch}")
    print(f"Output directory: {audio_dir.resolve()}")
    print()
    
    # Generate MP3 for each chapter
    mp3_files = []
    failed_chapters = []

    for txt_file in tqdm(chapter_files, desc="Generating MP3s", unit="chapter"):
        mp3_file = audio_dir / f"{txt_file.stem}.mp3"
        success = await text_to_speech(txt_file, mp3_file, voice=voice, rate=rate, pitch=pitch)
        
        if success:
            mp3_files.append(mp3_file)
        else:
            failed_chapters.append(txt_file.name)
    
    # Report any failures
    if failed_chapters:
        print(f"\nWarning: {len(failed_chapters)} chapter(s) failed to generate:")
        for name in failed_chapters:
            print(f"  - {name}")
    
    if not mp3_files:
        print("\nError: No MP3 files were generated.")
        sys.exit(1)
    
    print(f"\nSuccessfully generated {len(mp3_files)} chapter MP3s.")
    
    # Combine all chapters into full audiobook (if pydub available)
    if HAS_PYDUB:
        print("\nCombining all chapters into full_audiobook.mp3...")
        print("(This may take a few minutes)")
        
        combined = AudioSegment.empty()
        
        for i, mp3 in enumerate(tqdm(mp3_files, desc="Combining chapters", unit="chapter")):
            try:
                chapter_audio = AudioSegment.from_mp3(mp3)
                combined += chapter_audio
                
                # Add 2-second pause between chapters (except after the last one)
                if i < len(mp3_files) - 1:
                    combined += AudioSegment.silent(duration=2000)  # 2000ms = 2 seconds
            except Exception as e:
                print(f"  Error combining {mp3}: {e}")
        
        # Export the full audiobook
        full_path = audio_dir / "full_audiobook.mp3"
        
        print(f"\nExporting full audiobook (192kbps MP3)...")
        combined.export(
            full_path, 
            format="mp3", 
            bitrate="192k",
            parameters=["-ar", "44100"]  # 44.1kHz sample rate
        )
        
        # Calculate total duration
        total_duration_ms = len(combined)
        total_hours = total_duration_ms // 3600000
        total_minutes = (total_duration_ms % 3600000) // 60000
        total_seconds = (total_duration_ms % 60000) // 1000
        
        print()
        print("=" * 60)
        print("AUDIOBOOK GENERATION COMPLETE!")
        print("=" * 60)
        print()
        print(f"Total duration: {total_hours}h {total_minutes}m {total_seconds}s")
        print()
        print(f"Full audiobook:")
        print(f"   {full_path.resolve()}")
        print()
    else:
        print()
        print("=" * 60)
        print("CHAPTER MP3s GENERATED SUCCESSFULLY!")
        print("=" * 60)
        print()
        print("To combine into a single file, install pydub:")
        print("   pip install pydub")
        print("   python generate_audiobook.py")
        print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate audiobook from TTS-ready chapters using edge-tts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Top Voices for Technical Audiobooks (from voice-research.md):
  en-US-AvaMultilingualNeural     - Best overall, natural female (default)
  en-US-ChristopherNeural         - Best male, deep & calm (use --rate=+8%)
  en-GB-SoniaNeural               - Crisp British, great for acronyms
  en-US-AndrewMultilingualNeural  - Professional male, broadcast quality
  en-US-EmmaMultilingualNeural    - Conversational female, approachable

Examples:
  python generate_audiobook.py
  python generate_audiobook.py --voice en-US-ChristopherNeural --rate +8%
  python generate_audiobook.py --preview  # Test voice with sample text
        """
    )
    
    parser.add_argument(
        "--voice", 
        default=VOICE,
        help=f"TTS voice to use (default: {VOICE})"
    )
    parser.add_argument(
        "--rate",
        default=RATE,
        help=f"Speech rate adjustment (default: {RATE}). Examples: -5%, +10%"
    )
    parser.add_argument(
        "--pitch",
        default=PITCH,
        help=f"Pitch adjustment (default: {PITCH}). Examples: +0Hz, -10Hz"
    )
    parser.add_argument(
        "--preview",
        action="store_true",
        help="Generate a 30-second voice preview instead of full audiobook"
    )
    parser.add_argument(
        "--list-voices",
        action="store_true",
        help="List all available English voices"
    )
    
    args = parser.parse_args()
    
    try:
        # Handle --list-voices
        if args.list_voices:
            print("\nAvailable English voices in edge-tts:\n")
            print("Locale          | Voice ID                              | Gender")
            print("-" * 70)
            voices = [
                ("en-US", "AvaMultilingualNeural", "Female", "⭐ Best for technical"),
                ("en-US", "ChristopherNeural", "Male", "⭐ Best male narrator"),
                ("en-US", "AndrewMultilingualNeural", "Male", "Professional broadcast"),
                ("en-US", "EmmaMultilingualNeural", "Female", "Conversational"),
                ("en-US", "JennyNeural", "Female", "Standard"),
                ("en-US", "GuyNeural", "Male", "Standard"),
                ("en-GB", "SoniaNeural", "Female", "⭐ Crisp British"),
                ("en-GB", "RyanNeural", "Male", "British"),
                ("en-GB", "ThomasNeural", "Male", "British"),
                ("en-IN", "NeerjaNeural", "Female", "Indian English"),
                ("en-IN", "PrabhatNeural", "Male", "Indian English"),
                ("en-AU", "NatashaNeural", "Female", "Australian"),
                ("en-AU", "WilliamNeural", "Male", "Australian"),
            ]
            for locale, voice_id, gender, note in voices:
                marker = "⭐" if "⭐" in note else "  "
                print(f"{locale:<15} | {voice_id:<35} | {gender:<6} {marker}")
            print("\nFull list: edge-tts --list-voices\n")
            sys.exit(0)
        
        # Handle --preview
        if args.preview:
            print(f"Generating voice preview with {args.voice}...")
            preview_text = """The inference pipeline leverages a high-performance GPU cluster, 
            utilizing CUDA cores to accelerate the LLM computations within the 
            Kubernetes architecture. The system integrates seamlessly with PyTorch."""
            
            preview_path = Path("audiobook") / "voice_preview.mp3"
            preview_path.parent.mkdir(exist_ok=True)
            
            communicate = edge_tts.Communicate(
                text=preview_text, 
                voice=args.voice, 
                rate=args.rate, 
                pitch=args.pitch
            )
            asyncio.run(communicate.save(str(preview_path)))
            print(f"\n✅ Preview saved to: {preview_path.resolve()}")
            print("Listen to it and compare with other voices before generating the full book.\n")
            sys.exit(0)
        
        # Run main generation with CLI args
        asyncio.run(main(args.voice, args.rate, args.pitch))
        
    except KeyboardInterrupt:
        print("\n\nGeneration cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nFatal error: {e}")
        sys.exit(1)
