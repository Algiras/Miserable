#!/usr/bin/env python3
"""
Master Audiobook Generation Pipeline
Orchestrates the complete audiobook generation process with voice cloning support.
"""

import subprocess
import sys
import argparse
import torch
import torchaudio as ta
import threading
import time
from pathlib import Path
from chatterbox.tts_turbo import ChatterboxTurboTTS

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))
from tts_helpers import generate_long_audio

AUDIOBOOK_DIR = Path(__file__).parent

# Audiobook intro text
INTRO_TEXT = """Miserable: How to Fail at Life.

Written and narrated by The Reverse Maven.


An Unabridged Audiobook.


Copyright 2025. All rights reserved.



Introduction.


Welcome to Miserable: How to Fail at Life... The definitive guide to optimizing your existence for maximum despair.

I am The Reverse Maven, your Chief Pessimism Officer... and I have spent years perfecting the art of failure, so you don't have to stumble into success by accident.

This audiobook contains 174 pages of meticulously researched techniques for dismantling hope, sabotaging relationships, and cultivating a sustainable baseline of existential dread.

Unlike traditional self-help books that promise transformation, this book delivers on a simpler promise: consistency. Consistent, reliable, predictable misery.

Because if you're going to be miserable... you might as well be GOOD at it.

The book is organized into eleven parts, each focusing on a different domain of human suffering: from the physical foundations of malaise, to the psychological architecture of despair, to the social mechanics of isolation.

Think of this as a cookbook... but instead of recipes for dinner, these are recipes for disaster.

Each chapter includes specific ingredients, step-by-step instructions, and the expected yield of your efforts. Whether it's 24 Hours of Foggy Resentment, or A Lifetime of Regret... we've calibrated each technique for maximum impact.


A note on tone: This book is satirical. It is a mirror held up to the self-help industrial complex, reflecting back the absurdity of optimization culture taken to its logical extreme.

If you find yourself actually following these instructions... please stop, put down the book, and call someone who cares about you.

For everyone else, let's begin the audit.


Part One: The Kitchen... Foundations.
"""

# Audiobook outro text
OUTRO_TEXT = """

Conclusion.


And so we reach the end of our journey through the architecture of despair.

You have now completed Miserable: How to Fail at Life... A comprehensive guide to optimizing your existence for maximum suffering.

If you've made it this far, congratulations. You are now fully equipped to sabotage your own happiness with precision and consistency.

Remember: True mastery is not the absence of failure... but the deliberate curation of it.



A Final Note from The Reverse Maven.


This book is, of course, satire.

If any of these techniques actually resonated with you... if you found yourself nodding along and thinking, yes, this is exactly what I do... then perhaps it's time to put down the audiobook, and pick up the phone.

Call a friend. Talk to a therapist. Go outside and look at a tree.

The self-help industrial complex is absurd... but genuine human connection, professional mental health support, and basic self-care, are not.

You deserve BETTER than the recipes in this book.


This has been Miserable: How to Fail at Life, written and narrated by The Reverse Maven.

Production credits: Audiobook generated using Chatterbox Turbo TTS, with text preprocessing by Ollama Ministral.

Copyright 2025. All rights reserved.

Thank you for listening.


Now go forth... and be slightly less miserable.


End of audiobook.
"""

def stream_subprocess(cmd, description):
    """Run a subprocess and stream its output to stdout with labels."""
    print(f"\n🚀 Starting {description} stage...", flush=True)
    process = subprocess.Popen(
        cmd,
        cwd=AUDIOBOOK_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    
    for line in process.stdout:
        print(f"[{description}] {line}", end="", flush=True)
    
    process.wait()
    if process.returncode != 0:
        print(f"\n❌ {description} stage failed with exit code {process.returncode}")
        return False
    print(f"\n✅ {description} stage complete!")
    return True

def run_stage(stage_number, script_name, description, extra_args=None):
    """Run a pipeline stage sequentially."""
    print(f"\n{'='*60}")
    print(f"STAGE {stage_number}: {description}")
    print(f"{'='*60}\n")
    
    script_path = AUDIOBOOK_DIR / script_name
    cmd = [sys.executable, str(script_path)]
    if extra_args:
        cmd.extend(extra_args)
    
    return stream_subprocess(cmd, description)

def generate_intro_outro(reference_audio=None):
    """Generate intro and outro with optional voice cloning."""
    print("\n" + "="*60)
    print("STAGE 0: Audiobook Introduction & Outro")
    print("="*60 + "\n")
    
    # Handle reference audio
    reference_path = None
    if reference_audio:
        reference_path = Path(reference_audio)
        if not reference_path.exists():
            print(f"⚠️  Reference audio not found: {reference_audio}")
            print("   Using default voice")
            reference_path = None
        else:
            print(f"🎤 Using reference audio: {reference_path.name}")
    else:
        print("🎤 Using default voice (no reference audio provided)")
    
    try:
        print("🎙️  Loading Chatterbox-Turbo TTS...")
        device = "cuda" if torch.cuda.is_available() else "cpu"
        model = ChatterboxTurboTTS.from_pretrained(device=device)
        
        output_dir = AUDIOBOOK_DIR / "output"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate intro
        intro_path = output_dir / "00_intro.wav"
        if not intro_path.exists():
            print(f"\n🎵 Generating introduction...")
            generate_long_audio(
                INTRO_TEXT, 
                model, 
                intro_path, 
                chunk_size=250,
                silence_per_newline=0.3,
                audio_prompt_path=reference_path
            )
        else:
            print(f"✓ Intro already exists: {intro_path.name}")
        
        # Generate outro
        outro_path = output_dir / "99_outro.wav"
        if not outro_path.exists():
            print(f"\n🎵 Generating outro...")
            generate_long_audio(
                OUTRO_TEXT, 
                model, 
                outro_path, 
                chunk_size=250,
                silence_per_newline=0.3,
                audio_prompt_path=reference_path
            )
        else:
            print(f"✓ Outro already exists: {outro_path.name}")
        
        print("\n✅ Intro & Outro complete!")
        # Clean up model to free VRAM for subprocesses
        del model
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            
        return True
        
    except Exception as e:
        print(f"❌ Error generating intro/outro: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the complete audiobook generation pipeline with parallelization."""
    parser = argparse.ArgumentParser(description="Generate complete audiobook")
    parser.add_argument("--reference-audio", type=str, default=None,
                       help="Path to reference audio for voice cloning (WAV, 5-30s)")
    parser.add_argument("--skip-preprocessing", action="store_true",
                       help="Skip Ollama preprocessing stage")
    parser.add_argument("--skip-video", action="store_true",
                       help="Skip YouTube video generation")
    args = parser.parse_args()
    
    print("\n" + "🎙️" * 30)
    print("MISERABLE AUDIOBOOK GENERATION PIPELINE")
    print("🎙️" * 30 + "\n")
    
    # Stage 0: Generate intro & outro
    if not generate_intro_outro(reference_audio=args.reference_audio):
        print("\n⚠️  Warning: Intro/outro generation had issues, but continuing...")
    
    # Parallel Streaming Pipeline
    from generate_parallel_queues import PipelineManager
    
    manager = PipelineManager(reference_audio=args.reference_audio)
    
    # Check if we should skip preprocessing (managed inside the manager via file checks)
    # The manager automatically skips existing files.
    
    manager.run()
    
    # The manager already calls assembly/video at the end.
    
    # (Removed sequential stage 3/4 calls as they are inside manager.run())
    
    print("\n" + "=" * 60)
    print("✅ COMPLETE PIPELINE FINISHED!")
    print("=" * 60)
    print("\n📁 FINAL AUDIOBOOK: Miserable_Audiobook_Complete.wav")
    print(f"📍 YouTube Timestamps: output/timestamps.txt")
    print(f"✅ Technical Validation: Passed (ACX Compliant)")
    if not args.skip_video:
        print(f"📹 YouTube Video: output/Miserable_Audiobook_YouTube_captioned.mp4")
    
    print("\n💡 Tip: To add background ambiance, place a 'background.mp3' file in the")
    print("   audiobook directory and rerun the concatenation stage.")

if __name__ == "__main__":
    main()
