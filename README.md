# Miserable: How to Fail at Life

> *A 174-page curriculum in expertly curated self-sabotage.*

[![License: CC BY-SA 4.0](https://img.shields.io/badge/License-CC%20BY--SA%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-sa/4.0/)
[![Latest Release](https://img.shields.io/github/v/release/Algiras/Miserable)](https://github.com/Algiras/Miserable/releases/latest)

**The Official Archive of The Reverse Maven** — Counter-programming to Gladwell, Taleb, and Clear. Because success is just a lack of imagination.

---

## 📚 Get the Book

- **[Download PDF/EPUB](https://github.com/Algiras/Miserable/releases/tag/v1.0.0)** — Free, Creative Commons licensed
- **[Read Online](https://miserable.cloud/)** — 53 satirical blog posts
- **[Listen to Audiobook](https://www.youtube.com/watch?v=u-dnjEkpLLw)** — 3-hour AI-narrated version

---

## 🎯 What Is This?

*Miserable* is a satirical guide to failing at life with style. It's the anti-self-help book for the chronically unmotivated, professionally procrastinating, and existentially exhausted.

**Think of it as:**
- A reverse playbook for the "hustle culture" generation
- 53 "recipes for failure" disguised as life advice
- The literary equivalent of a slow-motion car crash (with academic citations)

**Topics include:**
- The Circadian Shuffle (how to ruin your sleep)
- Nutritional Nihilism (eating your way to misery)
- Corporate Gaslighting (the office as psychological warfare)
- The 4AM Inventory (auditing your failures at dawn)
- And 49 more ways to expertly sabotage yourself

---

## 🎧 Audiobook

The complete 3-hour audiobook is available for free on YouTube, narrated with AI voice synthesis (Chatterbox Turbo).

**[▶️ Listen Now](https://www.youtube.com/watch?v=u-dnjEkpLLw)**

Features:
- Professional narration with emotional inflection
- Chapter markers for easy navigation
- Synchronized with blog posts
- Creative Commons licensed (CC BY-SA 4.0)

---

## 📖 Formats Available

| Format | Link | License |
|--------|------|---------|
| **PDF** | [Download v1.0.0](https://github.com/Algiras/Miserable/releases/tag/v1.0.0) | CC BY-SA 4.0 |
| **EPUB** | [Download v1.0.0](https://github.com/Algiras/Miserable/releases/tag/v1.0.0) | CC BY-SA 4.0 |
| **Web** | [miserable.cloud](https://miserable.cloud/) | CC BY-SA 4.0 |
| **Audiobook** | [YouTube](https://www.youtube.com/watch?v=u-dnjEkpLLw) | CC BY-SA 4.0 |

---

## 🏗️ Project Structure

```
Miserable/
├── book/              # Quarto book source files (.qmd)
├── blog/              # Astro blog (53 satirical posts)
├── audiobook/         # TTS generation scripts
├── _book/             # Generated book output (PDF, EPUB, HTML)
└── README.md          # You are here
```

---

## 🛠️ Build It Yourself

### Prerequisites
- [Quarto](https://quarto.org/) for book generation
- [Node.js](https://nodejs.org/) for blog
- Python 3.11+ for audiobook generation

### Build the Book
```bash
quarto render
```

Outputs to `_book/`:
- `Miserable.pdf` — Print-ready PDF
- `Miserable.epub` — E-reader format
- `index.html` — Web version

### Run the Blog Locally
```bash
cd blog
npm install
npm run dev
```

Visit `http://localhost:4321`

### Generate Audiobook
```bash
cd audiobook
pip install -r requirements.txt
python generate_complete_audiobook.py
```

Requires:
- [Chatterbox Turbo](https://github.com/Hugging-Face-Supporter/chatterbox) (local TTS)
- [faster-whisper](https://github.com/SYSTRAN/faster-whisper) (transcription)
- FFmpeg (video generation)

---

## 📜 License

**Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)**

You are free to:
- ✅ **Share** — copy and redistribute in any medium or format
- ✅ **Adapt** — remix, transform, and build upon the material
- ✅ **Commercial use** — use for commercial purposes

Under the following terms:
- 📝 **Attribution** — You must give appropriate credit and link to [miserable.cloud](https://miserable.cloud/)
- 🔄 **ShareAlike** — Derivatives must use the same CC BY-SA 4.0 license

[Full License Text](https://creativecommons.org/licenses/by-sa/4.0/)

---

## 🤝 Contributing

This is a personal creative project, but if you find typos or have suggestions:

1. Open an issue
2. Submit a pull request
3. Or just [email me](mailto:hello@miserable.cloud)

---

## 🎭 About The Reverse Maven

The Reverse Maven is a satirical persona exploring the art of strategic failure. Think of it as the anti-Tim Ferriss, the un-Malcolm Gladwell, the counter-James Clear.

**Philosophy:** If self-help culture teaches you how to win, The Reverse Maven teaches you how to lose—with style, wit, and a surprising amount of academic rigor.

---

## 🔗 Links

- **Website:** [miserable.cloud](https://miserable.cloud/)
- **Audiobook:** [YouTube](https://www.youtube.com/watch?v=u-dnjEkpLLw)
- **Download:** [GitHub Releases](https://github.com/Algiras/Miserable/releases)
- **License:** [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)

---

## ⚠️ Disclaimer

This is satire. Dark, cynical, occasionally brutal satire. If you're looking for actual life advice, this is not the book for you. If you're looking for a mirror that reflects the absurdity of modern "productivity culture," welcome home.

---

*"The prisoner who loves his cell does not need a guard. The employee who loves the 'culture' does not need a raise."*  
— The Reverse Maven
