#!/usr/bin/env python3
"""
Audiobook Generator for "Miserable: How to Fail at Life"
Uses Chatterbox-Turbo TTS with silence insertion for pauses.
"""

import json
import torch
import torchaudio as ta
from pathlib import Path
from tqdm import tqdm
from chatterbox.tts_turbo import ChatterboxTurboTTS

# Paths
PREPROCESSED_DIR = Path(__file__).parent / "preprocessed"
OUTPUT_DIR = Path(__file__).parent / "output"

def generate_audiobook(reference_audio=None, device="cuda"):
    """Generate the complete audiobook from preprocessed chapters.
    
    Args:
        reference_audio: Path to reference audio file for voice cloning (WAV, 5-30 seconds)
        device: 'cuda' or 'cpu'
    """
    print("🎙️  Initializing Chatterbox-Turbo TTS...", flush=True)
    
    # Check for GPU
    if not torch.cuda.is_available():
        print("⚠️  CUDA not available, falling back to CPU (this will be slow)")
        device = "cpu"
    
    # Load model
    model = ChatterboxTurboTTS.from_pretrained(device=device)
    
    # Handle reference audio
    reference_path = None
    if reference_audio:
        reference_path = Path(reference_audio)
        if not reference_path.exists():
            print(f"⚠️  Reference audio not found: {reference_audio}")
            print("   Proceeding without voice cloning")
            reference_path = None
        else:
            print(f"🎤 Using reference audio: {reference_path.name}")
    
    # Load manifest
    manifest_path = PREPROCESSED_DIR / "manifest.json"
    if not manifest_path.exists():
        print(f"❌ Manifest not found: {manifest_path}")
        print("   Run Stage 1 (preprocessing) first!")
        return
    
    with open(manifest_path, 'r') as f:
        chapters = json.load(f)
    
    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    print(f"\n📚 Generating audiobook for {len(chapters)} chapters...")
    print("   Using silence insertion (0.5s per newline)\n")
    
    # Import silence helper
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from tts_helpers import generate_long_audio
    
    import time
    
    # We'll keep track of how many chapters are actually done
    completed_chapters = 0
    total_chapters = len(chapters)
    
    print(f"🎬 Starting audio generation loop (total {total_chapters} chapters)...", flush=True)
    
    while completed_chapters < total_chapters:
        any_new_generated = False
        
        for chapter_info in chapters:
            chapter_index = chapter_info['index']
            chapter_name = chapter_info['name']
            preprocessed_file = Path(chapter_info['file'])
            output_path = OUTPUT_DIR / f"{chapter_index:02d}_{chapter_name}.wav"
            
            # Check if audio already exists
            if output_path.exists():
                # If we haven't counted this as completed in this run, mark it
                # (Simple way to track progress without complex state)
                continue
                
            # Check if preprocessed text is ready
            if not preprocessed_file.exists() or preprocessed_file.stat().st_size < 10:
                continue
            
            # Load preprocessed text
            try:
                with open(preprocessed_file, 'r') as f:
                    text = f.read()
            except Exception as e:
                print(f"   ⚠️  Wait: {chapter_name} (error reading: {e})", flush=True)
                continue
            
            if not text or len(text) < 50:
                continue
            
            # Generate audio
            print(f"\n🎵 {chapter_name}", flush=True)
            try:
                generate_long_audio(
                    text, 
                    model, 
                    output_path, 
                    chunk_size=250,
                    silence_per_newline=0.3,
                    audio_prompt_path=reference_path
                )
                any_new_generated = True
            except Exception as e:
                print(f"   ❌ Error generating {chapter_name}: {e}", flush=True)
                continue
                
        # Update completion count
        current_wavs = list(OUTPUT_DIR.glob("*.wav"))
        completed_chapters = len([w for w in current_wavs if not w.name.startswith(('00_intro', '99_outro'))])
        
        if completed_chapters < total_chapters:
            if not any_new_generated:
                # Still waiting for preprocessing
                # Check if preprocessing is actually alive? (Hard to do here without more context)
                # For now, just print status and sleep
                print(f"🕒 Still waiting for {total_chapters - completed_chapters} chapters to be preprocessed...", end="\r", flush=True)
                time.sleep(10)
            else:
                # We just generated something, let's keep going Immediately
                pass
        else:
            print(f"\n✅ All {total_chapters} chapters processed!", flush=True)
    
    print("\n🎉 Audiobook generation complete!", flush=True)
    print(f"📁 Output directory: {OUTPUT_DIR}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate audiobook from preprocessed chapters")
    parser.add_argument("--device", default="cuda", choices=["cuda", "cpu"], 
                       help="Device to use for TTS generation")
    parser.add_argument("--reference-audio", type=str, default=None,
                       help="Path to reference audio file for voice cloning (WAV, 5-30 seconds)")
    args = parser.parse_args()
    
    generate_audiobook(reference_audio=args.reference_audio, device=args.device)
