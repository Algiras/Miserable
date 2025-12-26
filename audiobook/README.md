# Audiobook Generation for "Miserable: How to Fail at Life"

This directory contains the complete pipeline for generating an audiobook using:
- **Chatterbox-Turbo TTS** (zero-shot voice cloning)
- **Ollama + Ministral-3:14b** (text preprocessing for natural narration)

## Quick Start (Using Default Voice)

The easiest way to generate the audiobook is with Chatterbox's built-in default male voice:

```bash
cd audiobook/
python generate_complete_audiobook.py
```

This will:
1. Generate intro with default voice
2. Process all chapters (uses cached preprocessing if available)
3. Generate all chapter audio with default voice
4. Generate outro with default voice
5. Concatenate everything into `output/Miserable_Audiobook_Complete.wav`

**No reference audio needed!** The default voice is professional and suitable for audiobooks.

## Custom Voice (Optional)

If you want a specific voice, provide reference audio (15-30 seconds, WAV format):

```bash
python generate_complete_audiobook.py --reference-audio your_voice.wav
```

See [VOICE_CLONING.md](VOICE_CLONING.md) for details.

## Pipeline Overview

- **Zero-Shot TTS**: Clone any voice with just a 10-second reference clip
- **Creative Controls**: Automatic insertion of paralinguistic tags:
  - `[sarcastic tone]` for Maven quotes
  - `[chuckle]` after ironic statements
  - `[pause]` for natural pacing
  - `[emphasis]` for bold text
- **Chapter-by-Chapter**: Generates separate audio files for each book chapter
- **GPU Accelerated**: Uses CUDA for fast inference (falls back to CPU if unavailable)

## Setup

### 1. Install Ollama (for text preprocessing)

```bash
# Install Ollama from https://ollama.ai
# Then pull the model:
ollama pull mistral-3:14b
```

### 2. Install Python Dependencies

```bash
cd audiobook
pip install -r requirements.txt
```

### 3. Prepare Reference Audio (Optional)

For voice cloning, place a 10-second audio clip of your desired narrator voice in:
```
audiobook/reference_audio/narrator_voice.wav
```

**Requirements**:
- Format: WAV
- Duration: ~10 seconds
- Quality: Clear speech, minimal background noise

If no reference audio is provided, the model will use its default voice.

## Usage

### Complete Pipeline (Recommended)

Run the entire 3-stage pipeline with a single command:

```bash
python generate_complete_audiobook.py
```

This will execute:
1. **Stage 1**: Text preprocessing with Ollama (Mistral-3:14b)
2. **Stage 2**: Audio generation with Chatterbox-Turbo TTS
3. **Stage 3**: Concatenation into final audiobook

**Output**: `Miserable_Audiobook_Complete.wav` (complete audiobook)

---

### Manual Stage-by-Stage Workflow

For more control or to resume from a specific stage:

**Stage 1: Text Preprocessing**
```bash
python 1_preprocess_with_ollama.py
```
- Transforms book chapters into natural narration
- Uses Mistral-3:14b via Ollama
- Outputs to `preprocessed/` directory
- Generates `manifest.json` for tracking

**Stage 2: Audio Generation**
```bash
python 2_generate_audio.py --reference-audio your_voice.wav
```
- Converts preprocessed text to speech
- Uses Chatterbox-Turbo TTS
- Outputs individual chapter WAV files to `output/`
- Supports voice cloning with reference audio

**Stage 3: Audio Concatenation**
```bash
python 3_concatenate_audio.py
```
- Combines all chapter WAV files
- Handles sample rate consistency
- Outputs `Miserable_Audiobook_Complete.wav`

---

### Options

**Custom Reference Audio (Stage 2)**:
```bash
python 2_generate_audio.py --reference-audio /path/to/voice.wav --device cuda
```

**CPU Mode (if no GPU)**:
```bash
python 2_generate_audio.py --device cpu
```

**Custom Ollama Model (Stage 1)**:
```bash
python 1_preprocess_with_ollama.py --model llama3:70b
```

## Output

### Stage 1: Preprocessed Text
```
audiobook/preprocessed/
├── 00_index.txt
├── 01_circadian-shuffle.txt
├── 02_nutritional-nihilism.txt
├── ...
└── manifest.json
```

### Stage 2: Individual Chapter Audio
```
audiobook/output/
├── 00_index.wav
├── 01_circadian-shuffle.wav
├── 02_nutritional-nihilism.wav
└── ...
```

### Stage 3: Final Audiobook
```
audiobook/Miserable_Audiobook_Complete.wav  (Complete audiobook, ~2-4 hours)
```

### ⚡ High-Performance Streaming Pipeline (New!)
Run the entire production with one command. It uses parallel queues to stream chapters through all stages simultaneously:
```bash
python generate_complete_audiobook.py --reference-audio reference_voice.wav
```
This is the fastest method, as it starts narration and captioning as soon as the first chapter is text-ready.

### Manual Stage-by-Stage Workflow (For QC)
1. **Stage 1 (Preprocessing)**: `1_preprocess_with_ollama.py` (Ollama + RAG Memory)
2. **Stage 2 (Narration)**: `2_generate_audio.py` (TTS Audio Generation)
3. **Stage 3 (Concatenation)**: `3_concatenate_audio.py` (Mastering & Normalization)
4. **Stage 4 (YouTube Video)**: `4_generate_youtube_video.py` (Captions + Ambiance)
5. **Stage 5 (Verification)**: `5_technical_validation.py` (ACX/Audible Compliance Audit)

## Pipeline Architecture

```mermaid
graph LR
    P[Ollama + RAG] -->|Queue| A[Chatterbox TTS]
    A -->|Queue| T[Whisper Captioning]
    T -->|Queue| V[Video & Ambiance]
    V -->|Final| Q[Tech Validation]
```
- **RAG Memory**: Chapter 50 "remembers" Chapter 1, ensuring deep narrative consistency.
- **Normalization**: Masters to EBU R128 (-14 LUFS) automatically.
- **Verification**: Built-in QC check for RMS loudness and peak levels.

## Creative Controls

The script automatically enhances the narration with:

1. **Sarcastic Tone**: Applied to all Maven quotes (blockquotes)
2. **Chuckles**: Added after mentions of "success", "optimism", "productive", etc.
3. **Pauses**: Inserted after sentences for natural pacing
4. **Emphasis**: Applied to bold text

Example transformation:
```
Input:  "**Success** is just failure that hasn't happened yet."
Output: "[emphasis] Success [chuckle] is just failure that hasn't happened yet. [pause]"
```

## Technical Details

- **Model**: Chatterbox-Turbo (ResembleAI)
- **Sample Rate**: 24kHz
- **Format**: WAV (uncompressed)
- **Processing**: Removes LaTeX, citations, and markdown formatting
- **Paralinguistic Tags**: Supports [chuckle], [sigh], [pause], [emphasis], [sarcastic tone]

## Troubleshooting

### CUDA Out of Memory
If you encounter OOM errors, try:
```bash
python generate_audiobook.py --device cpu
```

### Missing Dependencies
Ensure you have PyTorch with CUDA support:
```bash
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121
```

## License

This audiobook generation system is part of the "Miserable" project. The generated audio is for personal use only.
