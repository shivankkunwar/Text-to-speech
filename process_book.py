"""
Book to Audiobook Processor
Parses PDF text, cleans for TTS, and splits into 23 natural chapters.
"""

import re
from pathlib import Path

# Read the raw extracted text
raw_text = Path("raw_extracted/raw_full.txt").read_text(encoding="utf-8")

# Create output directory
tts_dir = Path("tts_ready")
tts_dir.mkdir(exist_ok=True)

def clean_for_tts(text: str) -> str:
    """Clean text for optimal TTS reading."""
    # Remove Table of Contents section entirely (everything between TOC header and Preface/Chapter 0)
    text = re.sub(r'(Table of Contents.*?)(?=Preface|CHAPTER 0|CHAPTER 1)', '', text, flags=re.DOTALL)
    
    # Remove any remaining TOC-style lines (title with dots then page number)
    text = re.sub(r'\n[^\n]+[\.·]{5,}\s*\d+\n', '\n', text)
    
    # Remove page numbers and headers/footers
    text = re.sub(r'\n\s*\d+\s+Chapter \d+: [^\n]+\n', '\n', text)
    text = re.sub(r'\n\d+\s+[^\n]+\n', '\n', text)  # "123 Title" patterns
    text = re.sub(r'\n[^\n]+\s+\d+\n', '\n', text)  # "Title 123" patterns

    # Remove standalone page numbers
    text = re.sub(r'^\d+$', '', text, flags=re.MULTILINE)

    # Remove excessive whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r' +', ' ', text)

    # Fix hyphenated line breaks (words split across lines)
    text = re.sub(r'(\w+)-\n(\w+)', r'\1\2', text)

    # Remove standalone page numbers
    text = re.sub(r'^\d+$', '', text, flags=re.MULTILINE)
    
    # Remove "Table of Contents" header lines
    text = re.sub(r'\n\s*Table of Contents\s*\d*\n', '\n', text, flags=re.IGNORECASE)
    
    # Remove lines that are just numbers with "Table of Contents" nearby
    text = re.sub(r'\n\d+\s+Table of Contents\s*\d*\n', '\n', text, flags=re.IGNORECASE)

    # Remove excessive whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r' +', ' ', text)

    # Fix hyphenated line breaks (words split across lines)
    text = re.sub(r'(\w+)-\n(\w+)', r'\1\2', text)
    
    # Fix common OCR issues
    text = text.replace('fi ', 'fi')
    text = text.replace('fl ', 'fl')
    text = text.replace('ffi', 'ffi')
    text = text.replace('ffl', 'ffl')
    
    # Remove figure captions and references
    text = re.sub(r'Figure \d+\.\d+:?[^\n]*', '[Diagram skipped]', text)
    text = re.sub(r'\[Diagram skipped\]\s*\n', '', text)
    
    # Clean up table-like content
    text = re.sub(r'^\s*[-|]+\s*$', '', text, flags=re.MULTILINE)
    
    # Convert bullet points to spoken form
    text = re.sub(r'^\s*•\s+', '• ', text, flags=re.MULTILINE)
    
    # Fix abbreviations for TTS
    # Note: With en-US-AvaMultilingualNeural, most acronyms are handled correctly
    # We keep them capitalized so the TTS engine recognizes them as initialisms
    # Only expand ambiguous ones that might be mispronounced
    
    # Keep these as uppercase initialisms (Ava handles them correctly)
    # GPU, API, LLM, SQL, IDE, CUDA, ONNX all stay capitalized
    
    # Expand these for clarity
    text = re.sub(r'\bB2B\b', 'business to business', text)
    text = re.sub(r'\bKV\b', 'key value', text)  # KV cache → key value cache
    text = re.sub(r'\bRecSys\b', 'recommendation systems', text)
    
    # ASR and TTS are okay as-is, but expand for listeners unfamiliar with terms
    text = re.sub(r'\bASR\b', 'automatic speech recognition', text)
    text = re.sub(r'\bTTS\b', 'text to speech', text)
    
    # RAG - keep as initialism, Ava pronounces it correctly
    # text = re.sub(r'\bRAG\b', 'retrieval augmented generation', text)  # Optional expansion
    
    # Fix numbers for TTS
    text = re.sub(r'(\d+)x', r'\1 times', text)
    
    # Clean up extra whitespace again
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = text.strip()
    
    return text

def split_into_chapters(text: str) -> dict:
    """Split the book into 23 logical chapters."""
    chapters = {}
    
    # Find chapter boundaries
    chapter_patterns = [
        (r'CHAPTER 0\s+Inference', 'Chapter 0: Inference'),
        (r'CHAPTER 1\s+Prerequisites', 'Chapter 1: Prerequisites'),
        (r'CHAPTER 2\s+Models', 'Chapter 2: Models'),
        (r'CHAPTER 3\s+Hardware', 'Chapter 3: Hardware'),
        (r'CHAPTER 4\s+Software', 'Chapter 4: Software'),
        (r'CHAPTER 5\s+Techniques', 'Chapter 5: Techniques'),
        (r'CHAPTER 6\s+Modalities', 'Chapter 6: Modalities'),
        (r'CHAPTER 7\s+Production', 'Chapter 7: Production'),
        (r'APPENDIX A\s+Inference Glossary', 'Appendix A: Inference Glossary'),
        (r'APPENDIX B\s+Recommended\s+Reading', 'Appendix B: Recommended Reading'),
    ]
    
    # Find positions of each chapter
    positions = []
    for pattern, title in chapter_patterns:
        match = re.search(pattern, text)
        if match:
            positions.append((match.start(), title, pattern))
    
    # Sort by position
    positions.sort(key=lambda x: x[0])
    
    # Extract each section
    sections = {}
    for i, (pos, title, pattern) in enumerate(positions):
        if i < len(positions) - 1:
            next_pos = positions[i + 1][0]
            sections[title] = text[pos:next_pos]
        else:
            sections[title] = text[pos:]
    
    # Now split into 23 logical chapters
    chapter_num = 1
    
    # Chapter 1: Preface
    preface_match = re.search(r'(Preface.*?)(?=CHAPTER 0)', text, re.DOTALL)
    if preface_match:
        chapters[f'chapter_{chapter_num:02d}'] = {
            'title': 'Preface',
            'content': clean_for_tts(preface_match.group(1))
        }
        chapter_num += 1
    
    # Chapter 0 becomes Chapter 2
    if 'Chapter 0: Inference' in sections:
        chapters[f'chapter_{chapter_num:02d}'] = {
            'title': 'Chapter 0: Inference',
            'content': clean_for_tts(sections['Chapter 0: Inference'])
        }
        chapter_num += 1
    
    # Split Chapter 1 (Prerequisites) into 2 chapters
    if 'Chapter 1: Prerequisites' in sections:
        ch1 = sections['Chapter 1: Prerequisites']
        # Split at section 1.3
        split_match = re.search(r'(1\.3 Model Selection)', ch1)
        if split_match:
            split_pos = split_match.start()
            chapters[f'chapter_{chapter_num:02d}'] = {
                'title': 'Chapter 1 Part 1: Prerequisites and Scale',
                'content': clean_for_tts(ch1[:split_pos])
            }
            chapter_num += 1
            chapters[f'chapter_{chapter_num:02d}'] = {
                'title': 'Chapter 1 Part 2: Model Selection and Metrics',
                'content': clean_for_tts(ch1[split_pos:])
            }
            chapter_num += 1
    
    # Split Chapter 2 (Models) into 3 chapters
    if 'Chapter 2: Models' in sections:
        ch2 = sections['Chapter 2: Models']
        # Split at 2.2 and 2.4
        splits = []
        for pattern in [r'(2\.2 LLM Inference Mechanics)', r'(2\.4 Calculating Inference Bottlenecks)']:
            match = re.search(pattern, ch2)
            if match:
                splits.append(match.start())
        splits.sort()
        
        if len(splits) >= 2:
            chapters[f'chapter_{chapter_num:02d}'] = {
                'title': 'Chapter 2 Part 1: Neural Networks and LLM Architecture',
                'content': clean_for_tts(ch2[:splits[0]])
            }
            chapter_num += 1
            chapters[f'chapter_{chapter_num:02d}'] = {
                'title': 'Chapter 2 Part 2: LLM Inference and Attention',
                'content': clean_for_tts(ch2[splits[0]:splits[1]])
            }
            chapter_num += 1
            chapters[f'chapter_{chapter_num:02d}'] = {
                'title': 'Chapter 2 Part 3: Image Generation and Optimization',
                'content': clean_for_tts(ch2[splits[1]:])
            }
            chapter_num += 1
    
    # Split Chapter 3 (Hardware) into 2 chapters
    if 'Chapter 3: Hardware' in sections:
        ch3 = sections['Chapter 3: Hardware']
        split_match = re.search(r'(3\.3 Instances)', ch3)
        if split_match:
            split_pos = split_match.start()
            chapters[f'chapter_{chapter_num:02d}'] = {
                'title': 'Chapter 3 Part 1: GPU Architecture',
                'content': clean_for_tts(ch3[:split_pos])
            }
            chapter_num += 1
            chapters[f'chapter_{chapter_num:02d}'] = {
                'title': 'Chapter 3 Part 2: GPU Instances and Local Inference',
                'content': clean_for_tts(ch3[split_pos:])
            }
            chapter_num += 1
    
    # Split Chapter 4 (Software) into 3 chapters
    if 'Chapter 4: Software' in sections:
        ch4 = sections['Chapter 4: Software']
        splits = []
        for pattern in [r'(4\.2 Deep Learning Frameworks)', r'(4\.4 NVIDIA Dynamo)']:
            match = re.search(pattern, ch4)
            if match:
                splits.append(match.start())
        splits.sort()
        
        if len(splits) >= 2:
            chapters[f'chapter_{chapter_num:02d}'] = {
                'title': 'Chapter 4 Part 1: CUDA and Kernels',
                'content': clean_for_tts(ch4[:splits[0]])
            }
            chapter_num += 1
            chapters[f'chapter_{chapter_num:02d}'] = {
                'title': 'Chapter 4 Part 2: Frameworks and Inference Engines',
                'content': clean_for_tts(ch4[splits[0]:splits[1]])
            }
            chapter_num += 1
            chapters[f'chapter_{chapter_num:02d}'] = {
                'title': 'Chapter 4 Part 3: Dynamo and Benchmarking',
                'content': clean_for_tts(ch4[splits[1]:])
            }
            chapter_num += 1
    
    # Split Chapter 5 (Techniques) into 3 chapters
    if 'Chapter 5: Techniques' in sections:
        ch5 = sections['Chapter 5: Techniques']
        splits = []
        for pattern in [r'(5\.2 Speculative Decoding)', r'(5\.4 Model Parallelism)']:
            match = re.search(pattern, ch5)
            if match:
                splits.append(match.start())
        splits.sort()
        
        if len(splits) >= 2:
            chapters[f'chapter_{chapter_num:02d}'] = {
                'title': 'Chapter 5 Part 1: Quantization',
                'content': clean_for_tts(ch5[:splits[0]])
            }
            chapter_num += 1
            chapters[f'chapter_{chapter_num:02d}'] = {
                'title': 'Chapter 5 Part 2: Speculative Decoding and Caching',
                'content': clean_for_tts(ch5[splits[0]:splits[1]])
            }
            chapter_num += 1
            chapters[f'chapter_{chapter_num:02d}'] = {
                'title': 'Chapter 5 Part 3: Parallelism and Disaggregation',
                'content': clean_for_tts(ch5[splits[1]:])
            }
            chapter_num += 1
    
    # Split Chapter 6 (Modalities) into 4 chapters
    if 'Chapter 6: Modalities' in sections:
        ch6 = sections['Chapter 6: Modalities']
        splits = []
        for pattern in [r'(6\.2 Embedding Models)', r'(6\.4 TTS Models)', r'(6\.6 Video Generation Models)']:
            match = re.search(pattern, ch6)
            if match:
                splits.append(match.start())
        splits.sort()

        if len(splits) >= 3:
            chapters[f'chapter_{chapter_num:02d}'] = {
                'title': 'Chapter 6 Part 1: Vision Language Models',
                'content': clean_for_tts(ch6[:splits[0]])
            }
            chapter_num += 1
            chapters[f'chapter_{chapter_num:02d}'] = {
                'title': 'Chapter 6 Part 2: Embedding Models',
                'content': clean_for_tts(ch6[splits[0]:splits[1]])
            }
            chapter_num += 1
            chapters[f'chapter_{chapter_num:02d}'] = {
                'title': 'Chapter 6 Part 3: Speech Recognition and Synthesis',
                'content': clean_for_tts(ch6[splits[1]:splits[2]])
            }
            chapter_num += 1
            chapters[f'chapter_{chapter_num:02d}'] = {
                'title': 'Chapter 6 Part 4: Image and Video Generation',
                'content': clean_for_tts(ch6[splits[2]:])
            }
            chapter_num += 1
    
    # Split Chapter 7 (Production) into 2 chapters
    if 'Chapter 7: Production' in sections:
        ch7 = sections['Chapter 7: Production']
        split_match = re.search(r'(7\.4 Testing and Deployment)', ch7)
        if split_match:
            split_pos = split_match.start()
            chapters[f'chapter_{chapter_num:02d}'] = {
                'title': 'Chapter 7 Part 1: Containerization to Multi-Cloud',
                'content': clean_for_tts(ch7[:split_pos])
            }
            chapter_num += 1
            chapters[f'chapter_{chapter_num:02d}'] = {
                'title': 'Chapter 7 Part 2: Deployment and Client Code',
                'content': clean_for_tts(ch7[split_pos:])
            }
            chapter_num += 1
        else:
            chapters[f'chapter_{chapter_num:02d}'] = {
                'title': 'Chapter 7: Production',
                'content': clean_for_tts(ch7)
            }
            chapter_num += 1
    
    # Appendices as final chapters
    if 'Appendix A: Inference Glossary' in sections:
        chapters[f'chapter_{chapter_num:02d}'] = {
            'title': 'Appendix A: Inference Glossary',
            'content': clean_for_tts(sections['Appendix A: Inference Glossary'])
        }
        chapter_num += 1
    
    if 'Appendix B: Recommended Reading' in sections:
        chapters[f'chapter_{chapter_num:02d}'] = {
            'title': 'Appendix B: Recommended Reading',
            'content': clean_for_tts(sections['Appendix B: Recommended Reading'])
        }
        chapter_num += 1
    
    return chapters

def format_list_items(text: str) -> str:
    """Convert bullet points and numbered lists to natural spoken sentences."""
    lines = text.split('\n')
    result = []
    in_list = False
    list_items = []
    
    for line in lines:
        stripped = line.strip()
        is_list_item = stripped.startswith('• ') or re.match(r'^\d+\.\s+', stripped)
        
        if is_list_item:
            if not in_list:
                in_list = True
                list_items = []
            # Clean the item
            item = re.sub(r'^•\s*', '', stripped)
            item = re.sub(r'^\d+\.\s*', '', item)
            list_items.append(item)
        else:
            if in_list and list_items:
                # Convert list to spoken form
                if len(list_items) == 1:
                    result.append(f"The key point is: {list_items[0]}")
                elif len(list_items) == 2:
                    result.append(f"There are two points: {list_items[0]}, and {list_items[1]}.")
                else:
                    items_str = ', '.join(list_items[:-1]) + f', and {list_items[-1]}.'
                    result.append(f"The key points are: {items_str}")
                in_list = False
                list_items = []
            result.append(line)
    
    # Handle any remaining list
    if list_items:
        if len(list_items) == 1:
            result.append(f"The key point is: {list_items[0]}")
        else:
            items_str = ', '.join(list_items[:-1]) + f', and {list_items[-1]}.'
            result.append(f"The key points are: {items_str}")
    
    return '\n'.join(result)

# Process the book
print("Processing book...")
chapters = split_into_chapters(raw_text)

print(f"Found {len(chapters)} chapters")

# Remove chapter_01 (Preface with TOC contamination)
if 'chapter_01' in chapters:
    del chapters['chapter_01']
    print("Removed chapter_01 (Preface - TOC contamination)")

# Renumber chapters starting from 01 with clean title in filename
renumbered = {}
for i, (chapter_id, chapter_data) in enumerate(chapters.items(), 1):
    new_id = f"chapter_{i:02d}"
    # Create clean title from chapter title (remove "Chapter X" prefix)
    title_part = chapter_data['title'].lower()
    title_part = re.sub(r'^chapter\s*\d*\s*[:\-]?\s*', '', title_part)  # Remove "Chapter X:" prefix
    title_part = title_part.replace('/', '-')
    title_part = re.sub(r'[^a-z0-9 -]', '', title_part)
    title_part = '_'.join(title_part.split())[:40]  # Max 40 chars
    
    renumbered[new_id] = {
        'title': chapter_data['title'],
        'content': chapter_data['content'],
        'filename': f"{new_id}_{title_part}"
    }

# Save individual chapters
for chapter_id, chapter_data in renumbered.items():
    content = format_list_items(chapter_data['content'])

    # Add chapter announcement
    full_content = f"{chapter_data['title']}\n\n{content}"

    output_path = tts_dir / f"{chapter_data['filename']}.txt"
    output_path.write_text(full_content, encoding='utf-8')
    print(f"Saved {output_path.name} ({len(content)} chars)")

# Create full book
full_book = []
for chapter_id, chapter_data in renumbered.items():
    full_book.append(f"\n\n{'='*50}\n")
    full_book.append(f"{chapter_data['title']}\n")
    full_book.append(f"{'='*50}\n\n")
    full_book.append(format_list_items(chapter_data['content']))

full_book_text = '\n'.join(full_book)
(tts_dir / 'full_book.txt').write_text(full_book_text, encoding='utf-8')
print(f"\nSaved tts_ready/full_book.txt ({len(full_book_text)} chars)")

print("\n[OK] Book processing complete!")
