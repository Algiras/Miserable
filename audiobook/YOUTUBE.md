# YouTube Video Generation for Audiobook

This directory contains tools to convert the audiobook into a YouTube video.

## Quick Start

### 1. Generate the Audiobook
```bash
python generate_complete_audiobook.py --reference-audio reference_voice.wav
```

### 2. Generate YouTube Video
```bash
python 4_generate_youtube_video.py
```

This creates:
- `Miserable_Audiobook_YouTube.mp4` - Video with static splash screen

### 3. (Optional) Add Captions
```bash
# Install faster-whisper (Turbo - much faster!)
pip install faster-whisper

# Generate video with captions (parallel by default - fastest!)
python 4_generate_youtube_video.py --captions

# Generate video with captions sequentially (if needed)
python 4_generate_youtube_video.py --captions --sequential
```

This creates:
- `Miserable_Audiobook_YouTube.mp4` - Video without captions
- `Miserable_Audiobook_YouTube.srt` - Caption file
- `Miserable_Audiobook_YouTube_captioned.mp4` - Video with burned-in captions

**Note**: 
- faster-whisper is 4-5x faster than openai-whisper
- Captions are generated in parallel by default (saves ~15-20 minutes!)
- Use `--sequential` only if you encounter issues with parallel processing

## What You Need

### Required Files
- ✅ `output/Miserable_Audiobook_Complete.wav` - The complete audiobook
- ✅ `audiobook_splash_screen.png` - Splash screen image (generated)

### Optional
- **faster-whisper** (for auto-generated captions - Turbo speed!): `pip install faster-whisper`
  - 4-5x faster than openai-whisper
  - Uses less GPU memory
  - Requires CUDA for best performance

## YouTube Upload Checklist

### Video Details
- **Title**: "MISERABLE: How to Fail at Life - Full Audiobook"
- **Description**:
  ```
  The complete unabridged audiobook of "Miserable: How to Fail at Life" 
  by The Reverse Maven.
  
  A satirical guide to optimizing your existence for maximum despair.
  
  ⚠️ DISCLAIMER: This is satire. If you find yourself actually following 
  these instructions, please seek help from a mental health professional.
  
  Chapters:
  00:00 - Introduction
  [Add chapter timestamps here]
  
  © 2025 All Rights Reserved
  ```

- **Tags**: audiobook, self-help satire, comedy, full audiobook, free audiobook
- **Category**: Education or Entertainment
- **Thumbnail**: Use the generated splash screen

### Captions
- Upload the `.srt` file as subtitles for accessibility
- Or use the `_captioned.mp4` version with burned-in captions

### Copyright
- Set to "Standard YouTube License"
- Mark as "Not made for kids"

## Advanced Options

### Custom Splash Screen
Replace `audiobook_splash_screen.png` with your own 1920x1080 image.

### Custom Audio
```bash
python 4_generate_youtube_video.py --audio path/to/your/audio.wav
```

### Custom Output
```bash
python 4_generate_youtube_video.py --output path/to/output.mp4
```

## ✨ New: Ambiance & Professional Mastering
The pipeline now automatically masters your audio and adds ambiance:
- **EBU R128 Normalization**: Audio is mastered to **-14 LUFS** (YouTube standard).
- **Background Music**: Place a `background.mp3` in the `audiobook/` folder and it will be mixed into the video automatically.
- **Auto-Timestamps**: A `output/timestamps.txt` file is generated automatically. Copy-paste this into your YouTube description for chapter navigation!

## Technical Details

**Video Specs**:
- Resolution: 1920x1080 (Full HD)
- Video Codec: H.264 (libx264)
- Audio Codec: AAC
- Audio Bitrate: 192 kbps
- Normalization: -14 LUFS (EBU R128)
- Ambiance: Subconscious mixing at -20dB

**Estimated File Size**: ~200-300 MB for a 2-hour audiobook

## Troubleshooting

### "ffmpeg not found"
Install ffmpeg:
```bash
brew install ffmpeg  # macOS
```

### "Audio file not found"
Generate the audiobook first:
```bash
python generate_complete_audiobook.py --reference-audio reference_voice.wav
```

### Captions not working
Install faster-whisper (recommended):
```bash
pip install faster-whisper
```

**Performance**: faster-whisper is 4-5x faster than openai-whisper!
- 2-hour audiobook: ~15-20 minutes (vs 60-90 minutes with openai-whisper)
- Requires GPU for best speed (CPU works but slower)
