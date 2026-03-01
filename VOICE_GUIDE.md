# 🎙️ Voice Quick Reference

## Top 5 Voices for Technical Audiobooks

| Rank | Voice | Gender | Accent | Best For |
|------|-------|--------|--------|----------|
| 1 | `en-US-AvaMultilingualNeural` | Female | US | **Overall best** - technical content |
| 2 | `en-US-ChristopherNeural` | Male | US | Deep, calm narration |
| 3 | `en-GB-SoniaNeural` | Female | British | Crisp acronym pronunciation |
| 4 | `en-US-AndrewMultilingualNeural` | Male | US | Professional broadcast quality |
| 5 | `en-US-EmmaMultilingualNeural` | Female | US | Conversational, approachable |

## Quick Commands

### Test All Voices (Recommended First Step)
```bash
python test_voices.py
```
Generates 6 preview MP3s in `audiobook/` folder for comparison.

### Preview Current Voice
```bash
python generate_audiobook.py --preview
```

### List Available Voices
```bash
python generate_audiobook.py --list-voices
```

### Generate Audiobook with Custom Voice
```bash
# Best overall (default)
python generate_audiobook.py

# Best male voice
python generate_audiobook.py --voice en-US-ChristopherNeural --rate +8%

# British accent
python generate_audiobook.py --voice en-GB-SoniaNeural --rate -2%
```

## Recommended Settings

### Ava (Default - Best Choice)
```bash
--voice en-US-AvaMultilingualNeural --rate -5% --pitch +0Hz
```
- Rate -5% = better cognitive retention for dense material
- Optimal for 7+ hour listening sessions

### Christopher
```bash
--voice en-US-ChristopherNeural --rate +8% --pitch +0Hz
```
- Default is slow/narrative, +8% adds momentum for technical content

### Sonia (British)
```bash
--voice en-GB-SoniaNeural --rate -2% --pitch +0Hz
```
- Excellent for acronym-heavy content (GPU, API, LLM, CUDA)

## Technical Terms Handling

With **MultilingualNeural** voices (Ava, Andrew, Emma):

| Term | Pronunciation | Notes |
|------|---------------|-------|
| GPU | /dʒi-pi-ju/ | Correct initialism |
| LLM | /ɛl-ɛl-ɛm/ | Correct initialism |
| CUDA | /ku-də/ | Recognized as word, not acronym |
| Kubernetes | /ku-bər-nɛ-tiz/ | Correct stress pattern |
| PyTorch | /paɪ-tɔrtʃ/ | Compound word handling |
| inference | /ɪn-fə-rəns/ | Clear schwa articulation |

## Why Ava is #1

From voice-research.md:

1. **Multilingual Backend** - Superior phonetic flexibility
2. **Natural Pauses** - ~350ms between clauses (matches human narration)
3. **Balanced Intensity** - 52% median, no shouting/whispering
4. **Low Vocal Fry** - Minimal fatigue over 7-hour sessions
5. **Technical Lexicon** - Handles Kubernetes, PyTorch, CUDA flawlessly

## Full Voice List

Run `edge-tts --list-voices` for all 400+ voices.

English highlights:
- `en-US-*` - 17 voices (American)
- `en-GB-*` - 5 voices (British)
- `en-AU-*` - 2 voices (Australian)
- `en-IN-*` - 3 voices (Indian)
- `en-CA-*` - 2 voices (Canadian)
- Plus: Ireland, New Zealand, South Africa, Singapore, Philippines, Nigeria, Kenya, Tanzania

## Troubleshooting

**Voice sounds robotic:**
- Try MultilingualNeural voices (Ava, Andrew, Emma)
- Adjust rate: `-5%` often sounds more natural

**Acronyms mispronounced:**
- Ensure proper capitalization (GPU not gpu)
- Switch to Sonia (British) for crispest articulation

**Too fast for technical content:**
- Use `--rate -5%` to `-10%`
- Optimal: 130-160 words per minute

**Listener fatigue:**
- Choose Christopher (deep, calm) or Ava (balanced)
- Avoid overly expressive voices for long sessions

---

**Next Steps:**
1. Run `python test_voices.py`
2. Listen to all 6 previews
3. Pick your favorite
4. Generate full audiobook: `python generate_audiobook.py`
