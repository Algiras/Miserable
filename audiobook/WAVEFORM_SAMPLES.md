# Waveform Style Comparison

## Sample Videos Generated

I've created three 30-second sample videos so you can compare the different waveform styles:

### 📹 Sample Files

1. **`sample_gradient.mp4`** - Cyan to Magenta Gradient
   - Size: 5.2 MB
   - Style: Smooth two-color gradient (cyan → magenta)
   - Best for: Professional, clean look

2. **`sample_rainbow.mp4`** - Rainbow Spectrum
   - Size: 1.3 MB (smaller due to different visualization)
   - Style: Full rainbow spectrum based on audio frequency
   - Best for: Dynamic, colorful visualization

3. **`sample_neon.mp4`** - Neon Multi-Color
   - Size: 5.3 MB
   - Style: Vibrant cyan → magenta → yellow
   - Best for: Bold, eye-catching effect

---

## How to View Samples

Open the files in `audiobook/output/`:
- `sample_gradient.mp4`
- `sample_rainbow.mp4`
- `sample_neon.mp4`

Compare them side-by-side to see which style you prefer!

---

## Generate Full Video

Once you've chosen your favorite style, generate the full 3h48m video:

```bash
# Gradient (recommended for professional look)
python3 audiobook/generate_youtube_colorful.py --style gradient

# Rainbow (most colorful and dynamic)
python3 audiobook/generate_youtube_colorful.py --style rainbow

# Neon (bold and vibrant)
python3 audiobook/generate_youtube_colorful.py --style neon
```

---

## Style Recommendations

**For Audiobooks**: **Gradient** or **Neon**
- Clean, professional appearance
- Waveform clearly shows audio activity
- Not distracting from the content

**For Music Videos**: **Rainbow**
- More dynamic and colorful
- Frequency-based visualization
- Visually engaging

**For Maximum Impact**: **Neon**
- Bold, vibrant colors
- Eye-catching thumbnail potential
- Modern aesthetic

---

## Technical Details

All samples use:
- 1920x1080 resolution
- AAC 192kbps audio
- H.264 video codec
- YouTube-optimized settings
