# 📚 PDF to Audiobook Converter

Transform any technical PDF book into a professional, listenable audiobook using **100% free tools**.

## 🎯 What This Does

- **Parses PDF/EPUB** books and extracts clean text
- **Removes** page numbers, headers, footers, OCR junk
- **Splits** books into natural chapters
- **Optimizes text for TTS** (fixes abbreviations, converts lists to spoken form)
- **Generates high-quality MP3** using Microsoft Edge TTS (free, unlimited)
- **Combines chapters** into a single audiobook file

## 🚀 Quick Start

### Prerequisites
```bash
pip install pdfplumber edge-tts pydub tqdm
```

### Usage

**Step 1: Extract text from PDF**
```bash
python extract_pdf.py
```

**Step 2: Process and clean text for TTS**
```bash
python process_book.py
```
This creates:
- `tts_ready/chapter_XX.txt` - Individual cleaned chapters
- `tts_ready/full_book.txt` - Complete book

**Step 3: Generate audiobook**
```bash
python generate_audiobook.py
```
This creates:
- `audiobook/chapter_XX.mp3` - Individual chapter MP3s
- `audiobook/full_audiobook.mp3` - Complete audiobook (if pydub available)

## 🎙️ TTS Voice Options

Default voice: `en-IN-NeerjaNeural` (Indian English, female)

**Popular alternatives:**
- `en-US-JennyNeural` - US English, natural female
- `en-US-GuyNeural` - US English, natural male
- `en-GB-SoniaNeural` - British English, female
- `en-AU-NatashaNeural` - Australian English, female

**Edit voice in `generate_audiobook.py`:**
```python
VOICE = "en-US-JennyNeural"  # Change here
```

**List all available voices:**
```bash
edge-tts --list-voices
```

## 📁 Project Structure

```
.
├── extract_pdf.py          # PDF text extraction
├── process_book.py         # Clean & split into chapters
├── generate_audiobook.py   # TTS generation
├── tts_ready/              # Processed text chapters (generated)
├── audiobook/              # Output MP3 files (generated)
└── raw_extracted/          # Raw PDF extraction (generated)
```

## 🛠️ Building a Personal App

### Hetzner CX33 Specs (4 vCPU, 8GB RAM, 160GB NVMe)

| Task | Capability | Notes |
|------|------------|-------|
| edge-tts (API) | ✅ Perfect | TTS runs on Microsoft servers |
| PDF Processing | ✅ Great | Handles large PDFs easily |
| Web App 24/7 | ✅ Good | 8GB RAM sufficient for moderate traffic |
| Local TTS | ⚠️ Limited | Possible but slow without GPU |

**Storage per audiobook:** ~1-2GB (can store 50-80 books)

### Creative Use Cases

1. **Daily Content Digest** - RSS → Morning briefing MP3
2. **Code Documentation Audio** - README/docs → Audio tutorials
3. **Telegram Bot** - Send PDF, get audiobook chapters
4. **Notion/Obsidian Integration** - Notes → Audio summaries
5. **YouTube Auto-Narration** - Blog posts → narrated videos
6. **Language Learning** - Generate multi-speed audio materials
7. **Accessibility Tool** - Browser extension for article narration
8. **Multi-Voice Audiobooks** - Different characters → different voices

### Future Enhancements

- [ ] Streamlit web interface
- [ ] FastAPI + React production app
- [ ] Telegram/Discord bot
- [ ] Docker deployment image
- [ ] Local TTS support (Coqui/Piper)
- [ ] Multi-voice character narration
- [ ] Background music integration

## ⚖️ Legal & Ethics

- **Personal use only** - Respect copyright laws
- **Public domain/Creative Commons** books recommended
- **Do not distribute** copyrighted audiobooks

## 📄 License

MIT License - Use freely for personal projects.

## 🙏 Credits

- **edge-tts** - Free Microsoft TTS API
- **pdfplumber** - PDF text extraction
- **pydub** - Audio manipulation

---

**Built for learning. Made with ❤️ for the AI community.**
