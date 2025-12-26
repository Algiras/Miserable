#!/usr/bin/env python3
"""
Helper functions for TTS chunking
"""

import torch
import torchaudio as ta

def chunk_text(text, max_chars=250):
    """Split text into chunks at natural boundaries (paragraphs/sentences)."""
    chunks = []
    paragraphs = text.split('\n\n')
    
    current_chunk = []
    current_size = 0
    
    for para in paragraphs:
        para_size = len(para)
        
        # If single paragraph is too long, split by sentences
        if para_size > max_chars:
            sentences = para.split('. ')
            for sentence in sentences:
                sentence = sentence.strip()
                if not sentence:
                    continue
                    
                # Add period back if it was removed
                if not sentence.endswith('.') and not sentence.endswith('[pause]'):
                    sentence += '.'
                
                sent_size = len(sentence)
                
                if current_size + sent_size > max_chars and current_chunk:
                    chunks.append('\n\n'.join(current_chunk))
                    current_chunk = [sentence]
                    current_size = sent_size
                else:
                    current_chunk.append(sentence)
                    current_size += sent_size
        else:
            if current_size + para_size > max_chars and current_chunk:
                chunks.append('\n\n'.join(current_chunk))
                current_chunk = [para]
                current_size = para_size
            else:
                current_chunk.append(para)
                current_size += para_size
    
    if current_chunk:
        chunks.append('\n\n'.join(current_chunk))
    
    return chunks

def generate_long_audio(text, model, output_path, chunk_size=250, silence_per_newline=0.3, audio_prompt_path=None):
    """Generate audio for long text by chunking and concatenating, with explicit silence for newlines.
    
    Args:
        text: Text to generate audio for
        model: ChatterboxTurboTTS model
        output_path: Path to save output WAV file
        chunk_size: Maximum characters per chunk
        silence_per_newline: Seconds of silence per newline
        audio_prompt_path: Optional path to reference audio for voice cloning
    """
    import torch
    import torchaudio as ta
    
    # Split text by newlines to insert silence
    lines = text.split('\n')
    
    print(f"   Processing {len(lines)} lines with silence insertion")
    
    all_audio = []
    sample_rate = model.sr
    
    # Create silence tensor (0.5s per newline by default)
    silence_samples = int(sample_rate * silence_per_newline)
    silence = torch.zeros(1, silence_samples)
    
    for i, line in enumerate(lines):
        line = line.strip()
        
        # Skip empty lines but add silence for them
        if not line:
            if i > 0:  # Don't add silence at the very beginning
                all_audio.append(silence)
            continue
        
        # Process non-empty line
        # If line is too long, chunk it
        if len(line) > chunk_size:
            chunks = chunk_text(line, max_chars=chunk_size)
            print(f"   Line {i+1}: {len(chunks)} chunks ({len(line)} chars)")
            
            for j, chunk in enumerate(chunks):
                try:
                    if audio_prompt_path:
                        wav = model.generate(chunk, audio_prompt_path=str(audio_prompt_path))
                    else:
                        wav = model.generate(chunk)
                    all_audio.append(wav)
                except Exception as e:
                    print(f"   ⚠️  Error on line {i+1}, chunk {j+1}: {e}")
                    continue
        else:
            # Generate audio for the line
            try:
                if audio_prompt_path:
                    wav = model.generate(line, audio_prompt_path=str(audio_prompt_path))
                else:
                    wav = model.generate(line)
                all_audio.append(wav)
            except Exception as e:
                print(f"   ⚠️  Error on line {i+1}: {e}")
                continue
        
        # Add silence after each line (except the last one)
        if i < len(lines) - 1:
            all_audio.append(silence)
    
    if not all_audio:
        raise Exception("No audio segments were generated successfully")
    
    # Concatenate all audio segments
    final_audio = torch.cat(all_audio, dim=1)
    
    ta.save(str(output_path), final_audio, sample_rate)
    
    duration = final_audio.shape[1] / sample_rate
    print(f"   ✅ Generated {duration:.1f}s of audio with {len(all_audio)} segments")
    
    return final_audio
