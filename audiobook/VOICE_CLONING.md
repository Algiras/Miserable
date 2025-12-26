# Voice Options for Audiobook

## Default Voice (Recommended - Free!)

Chatterbox-Turbo includes a **built-in default male voice** that works great for audiobooks. No reference audio needed!

**To use the default voice:**
```bash
cd audiobook/
python generate_complete_audiobook.py
```

That's it! The default voice is:
- ✅ Male-sounding
- ✅ Clear and professional
- ✅ Completely free
- ✅ No setup required

## Custom Voice Cloning (Optional)

If you want a specific voice, you can provide reference audio:

### Option 1: Record Your Own
1. Record 15-30 seconds of clear speech (WAV format)
2. Save as `audiobook/reference_voice.wav`
3. Run: `python generate_complete_audiobook.py --reference-audio reference_voice.wav`

### Option 2: Use Public Domain Audio
1. Download a LibriVox audiobook sample (narrators like Bob Neufeld, Andy Minter)
2. Extract a 15-30 second clean clip
3. Convert to WAV format
4. Use as reference audio

## Comparison

| Option | Cost | Setup | Quality |
|--------|------|-------|---------|
| **Default Voice** | Free | None | Good |
| **Custom Voice** | Free | 5-10 min | Excellent |

**Recommendation:** Start with the default voice. If you want a different tone, then add custom voice cloning.

## Example Commands

```bash
# Use default voice (easiest)
python generate_complete_audiobook.py

# Use custom voice
python generate_complete_audiobook.py --reference-audio my_voice.wav

# Skip preprocessing if already done
python generate_complete_audiobook.py --skip-preprocessing
```
