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

try:
    from pydub import AudioSegment
    HAS_PYDUB = True
except ImportError:
    HAS_PYDUB = False
    print("Note: pydub not available. Skipping full audiobook combination.")
    print("Individual chapter MP3s will still be generated.\n")

# Best natural Indian English female voice
VOICE = "en-IN-NeerjaNeural"
# Alternative male voice: "en-IN-RaviNeural"

# Speech rate adjustment (+5% for natural pacing)
RATE = "+5%"

async def text_to_speech(input_txt: Path, output_mp3: Path, voice: str = VOICE, rate: str = RATE) -> bool:
    """
    Convert a text file to speech using edge-tts.
    
    Args:
        input_txt: Path to input text file
        output_mp3: Path to output MP3 file
        voice: TTS voice to use
        rate: Speech rate adjustment
        
    Returns:
        True if successful, False otherwise
    """
    try:
        text = input_txt.read_text(encoding="utf-8").strip()
        if not text:
            print(f"  Warning: Empty file {input_txt}")
            return False
        
        communicate = edge_tts.Communicate(text=text, voice=voice, rate=rate)
        await communicate.save(str(output_mp3))
        return True
    except Exception as e:
        print(f"  Error processing {input_txt}: {e}")
        return False


async def main():
    """Main function to generate the complete audiobook."""
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
    print(f"Starting TTS conversion with voice: {VOICE}")
    print(f"Output directory: {audio_dir.resolve()}")
    print()
    
    # Generate MP3 for each chapter
    mp3_files = []
    failed_chapters = []
    
    for txt_file in tqdm(chapter_files, desc="Generating MP3s", unit="chapter"):
        mp3_file = audio_dir / f"{txt_file.stem}.mp3"
        success = await text_to_speech(txt_file, mp3_file)
        
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
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nGeneration cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nFatal error: {e}")
        sys.exit(1)
