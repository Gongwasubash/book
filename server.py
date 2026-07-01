import os
import sys
import json
import re
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory, Response
import requests

app = Flask(__name__, static_url_path='', static_folder='.')

BASE = Path(__file__).parent.resolve()

# --- AI Provider Configuration ---
# Supports: "groq" (free, recommended) or "deepseek" (paid)
# Set AI_PROVIDER env var to override (default: groq)
# Groq: get free API key at https://console.groq.com/keys
#   Set GROQ_API_KEY env var or paste below
# DeepSeek: requires paid credits
#   Set DEEPSEEK_API_KEY env var or paste below

AI_PROVIDER = os.environ.get("AI_PROVIDER", "groq")

# Groq config (free tier — set GROQ_API_KEY env var)
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")  # or llama-3.1-8b-instant, qwen/qwen3-32b

# DeepSeek config (paid, fallback)
# Set DEEPSEEK_API_KEY env var to use DeepSeek
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
DEEPSEEK_URL = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_MODEL = "deepseek-chat"

# Mistral AI config (free tier fallback)
MISTRAL_API_KEY = os.environ.get("MISTRAL_API_KEY", "u0YMFGONYPEqZHTEChuOUUr9Sw4QZUBI")
MISTRAL_URL = "https://api.mistral.ai/v1/chat/completions"
MISTRAL_MODEL = os.environ.get("MISTRAL_MODEL", "mistral-small-latest")

# Build file mapping from the directory structure
def build_file_map():
    fmap = {}
    for i in range(1, 11):
        cls_dir = BASE / f"Class {i}"
        if not cls_dir.is_dir():
            continue
        for fpath in sorted(cls_dir.iterdir()):
            if not fpath.name.endswith('.md') or 'DUPLICATE' in fpath.name:
                continue
            # Strip "Class N " prefix and ".md" suffix
            name = fpath.stem  # e.g. "Class 6 Mathematics (Nepali)"
            # Remove "Class N " prefix
            m = re.match(r'^Class\s+\d+\s+(.+)$', name)
            if m:
                display = m.group(1).strip()
                fmap[(f"Class {i}", display)] = str(fpath)
    return fmap

FILE_MAP = build_file_map()

@app.route('/')
def index():
    return send_from_directory(BASE, 'toc_webpage.html')

@app.route('/api/files', methods=['GET'])
def list_files():
    """Return the file mapping for debugging."""
    items = {}
    for (cls, subj), path in sorted(FILE_MAP.items()):
        items.setdefault(cls, {})[subj] = path
    return jsonify(items)

@app.route('/api/resolve', methods=['GET'])
def resolve_file():
    """Resolve a class+subject to its file path (without reading)."""
    cls = request.args.get('class', '')
    subj = request.args.get('subject', '')
    path = FILE_MAP.get((cls, subj))
    if path:
        rel = os.path.relpath(path, str(BASE))
        return jsonify({"path": rel, "exists": True})
    # Try fuzzy match
    for (c, s), p in FILE_MAP.items():
        if c == cls and (s.lower() == subj.lower() or subj.lower() in s.lower() or s.lower() in subj.lower()):
            rel = os.path.relpath(p, str(BASE))
            return jsonify({"path": rel, "exists": True, "matched_subject": s})
    return jsonify({"path": None, "exists": False}), 404

@app.route('/api/read-file', methods=['GET'])
def read_file():
    """Read and return the full content of a textbook markdown file."""
    cls = request.args.get('class', '')
    subj = request.args.get('subject', '')
    path = FILE_MAP.get((cls, subj))
    if not path:
        # fuzzy fallback
        for (c, s), p in FILE_MAP.items():
            if c == cls and (subj.lower() in s.lower() or s.lower() in subj.lower()):
                path = p
                break
    if not path:
        return jsonify({"error": f"File not found for {cls}/{subj}"}), 404
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        rel = os.path.relpath(path, str(BASE))
        return jsonify({"path": rel, "content": content, "size": len(content)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Send textbook content + user query to DeepSeek API.
    Body: { class, subject, chapterIndex, query, mode }
    """
    data = request.get_json() or {}
    cls = data.get('class', '')
    subj = data.get('subject', '')
    chapter_index = data.get('chapterIndex')
    query = data.get('query', '')
    mode = data.get('mode', 'ask')  # mcq, mindmap, exercise, ask

    # Accept fileContent from request, or read from filesystem
    content = data.get('fileContent', '')
    if not content:
        # Fallback: read from filesystem (for local dev with old frontend)
        path = FILE_MAP.get((cls, subj))
        if not path:
            for (c, s), p in FILE_MAP.items():
                if c == cls and (subj.lower() in s.lower() or s.lower() in subj.lower()):
                    path = p
                    break
        if path:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception as e:
                return jsonify({"error": f"Failed to read file: {e}"}), 500
        else:
            return jsonify({"error": f"No content provided and file not found for {cls}/{subj}"}), 400

    # Build system prompt based on mode
    subject_header = f"{cls} - {subj}"
    is_nepali = bool(re.search(r'[\u0900-\u097F]', (subj + content[:500])))
    lang = 'Nepali' if is_nepali else 'English'
    lang_instr = 'IMPORTANT: Respond in Nepali language only. Use textbook terminology and explanations.' if is_nepali else 'Respond in English.'
    source_instr = 'Base your answer strictly on the textbook content provided below. Do not use external knowledge or make up information not present in the text.'

    system_prompts = {
        "mcq": f"""You are an AI tutor for {subject_header}. {lang_instr} {source_instr} Generate 10 multiple-choice questions with 4 options each and an answer key. Focus on the most important concepts from the chapter covered in the textbook content. Format as:

## Multiple Choice Questions

1. **Question text?**
   - A) Option A
   - B) Option B  
   - C) Option C
   - D) Option D
   **Answer:** A) Option A

(Continue for all 10 questions)""",

        "mindmap": f"""You are an AI tutor for {subject_header}. {lang_instr} {source_instr} Create a detailed mind map / concept map of the chapter based on the textbook content. Use indentation to show hierarchy. Format as:

## Mind Map: [Chapter Title]

- Main Concept 1
  - Sub-concept 1.1
    - Detail 1.1.1
    - Detail 1.1.2
  - Sub-concept 1.2
- Main Concept 2
  - Sub-concept 2.1
...""",

        "exercise": f"""You are an AI tutor for {subject_header}. {lang_instr} {source_instr} Create a practice exercise set based on the textbook content with:
1. 5 short-answer questions
2. 3 numerical/long-answer problems
3. A brief answer key

Format clearly with sections.""",

        "chapter_exercise": f"""You are an AI tutor for {subject_header}. {lang_instr} {source_instr} This is the most important instruction: Carefully read the provided textbook content for this specific chapter and generate a complete chapter exercise that includes:
1. 5 MCQs (multiple choice questions with 4 options each and answer key)
2. 5 short-answer conceptual questions
3. 3 numerical/long-answer problems with step-by-step solutions
4. A summary of key formulas/concepts from this chapter

Every question must be directly based on the content present in the textbook excerpt below. Do not include any topic not covered in the provided text. Use the exact terminology and examples from the textbook. Format clearly with sections.""",

        "ask": f"""You are an AI tutor for {subject_header}. {lang_instr} {source_instr} Answer the student's question based on the textbook content below. Be thorough, educational, and use examples from the text. If the question is off-topic, politely redirect to the subject matter."""
    }

    system_prompt = system_prompts.get(mode, system_prompts["ask"])

    # If chapter specified, try to extract that section
    chapter_context = ""
    if chapter_index is not None:
        chapter_context = f"\n(The student is asking about Chapter {chapter_index + 1})"

    user_prompt = f"""Here is the full textbook content for {subject_header}:

=== BEGIN TEXTBOOK CONTENT ===
{content[:20000]}
=== END TEXTBOOK CONTENT ===

{chapter_context}
Student's request: {query}"""

    # Call AI API — try Groq first, fallback to Mistral
    def call_api(api_key, api_url, model):
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 4096,
            "stream": False
        }
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        resp = requests.post(api_url, json=payload, headers=headers, timeout=120)
        resp.raise_for_status()
        return resp.json()

    answer = None
    model_used = None
    last_error = None

    # Try Groq first
    if GROQ_API_KEY:
        try:
            result = call_api(GROQ_API_KEY, GROQ_URL, GROQ_MODEL)
            answer = result['choices'][0]['message']['content']
            model_used = GROQ_MODEL
        except Exception as e:
            last_error = f"Groq failed: {str(e)}"

    # Fallback to Mistral
    if not answer and MISTRAL_API_KEY:
        try:
            result = call_api(MISTRAL_API_KEY, MISTRAL_URL, MISTRAL_MODEL)
            answer = result['choices'][0]['message']['content']
            model_used = MISTRAL_MODEL
        except Exception as e:
            last_error = f"Groq and Mistral both failed. Mistral error: {str(e)}"

    if not answer:
        err_msg = last_error or "No AI provider available. Set GROQ_API_KEY or MISTRAL_API_KEY."
        return jsonify({"error": err_msg}), 502

    return jsonify({
        "answer": answer,
        "model": model_used
    })

@app.route('/api/chat/stream', methods=['POST'])
def chat_stream():
    """Streaming version of /api/chat."""
    data = request.get_json() or {}
    cls = data.get('class', '')
    subj = data.get('subject', '')
    chapter_index = data.get('chapterIndex')
    query = data.get('query', '')
    mode = data.get('mode', 'ask')

    # Accept fileContent from request, or read from filesystem
    content = data.get('fileContent', '')
    if not content:
        path = FILE_MAP.get((cls, subj))
        if not path:
            for (c, s), p in FILE_MAP.items():
                if c == cls and (subj.lower() in s.lower() or s.lower() in subj.lower()):
                    path = p
                    break
        if path:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception as e:
                return jsonify({"error": f"Failed to read file: {e}"}), 500
        else:
            return jsonify({"error": f"No content provided and file not found for {cls}/{subj}"}), 400

    subject_header = f"{cls} - {subj}"
    is_nepali = bool(re.search(r'[\u0900-\u097F]', subj + content[:500]))
    lang_instr = 'IMPORTANT: Respond in Nepali language only. Use textbook terminology and explanations.' if is_nepali else 'Respond in English.'
    source_instr = 'Base your answer strictly on the textbook content provided below. Do not use external knowledge.'
    system_prompts = {
        "mcq": f"You are an AI tutor for {subject_header}. {lang_instr} {source_instr} Generate 10 multiple-choice questions with 4 options each and an answer key. Focus on the most important concepts from the chapter covered in the textbook content.",
        "mindmap": f"You are an AI tutor for {subject_header}. {lang_instr} {source_instr} Create a detailed mind map / concept map of the chapter based on the textbook content. Use indentation to show hierarchy.",
        "exercise": f"You are an AI tutor for {subject_header}. {lang_instr} {source_instr} Create a practice exercise set based on the textbook content with 5 short-answer questions, 3 numerical/long-answer problems, and a brief answer key.",
        "chapter_exercise": f"You are an AI tutor for {subject_header}. {lang_instr} {source_instr} Carefully read the provided textbook content for this specific chapter and generate a complete chapter exercise that includes: 5 MCQs with answer key, 5 short-answer conceptual questions, 3 numerical/long-answer problems with step-by-step solutions, and a summary of key concepts. Every question must be directly based on the content present in the textbook excerpt below.",
        "ask": f"You are an AI tutor for {subject_header}. {lang_instr} {source_instr} Answer the student's question based on the textbook content below. Be thorough, educational, and use examples from the text."
    }

    system_prompt = system_prompts.get(mode, system_prompts["ask"])
    chapter_context = ""
    if chapter_index is not None:
        chapter_context = f"\n(The student is asking about Chapter {chapter_index + 1})"

    user_prompt = f"Here is the full textbook content for {subject_header}:\n\n=== BEGIN TEXTBOOK CONTENT ===\n{content[:20000]}\n=== END TEXTBOOK CONTENT ===\n{chapter_context}\nStudent's request: {query}"

    def generate():
        def stream_provider(api_key, api_url, model):
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 4096,
                "stream": True
            }
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            with requests.post(api_url, json=payload, headers=headers, stream=True, timeout=120) as resp:
                resp.raise_for_status()
                for line in resp.iter_lines(decode_unicode=True):
                    if line:
                        if line.startswith("data: "):
                            data_str = line[6:]
                            if data_str.strip() == "[DONE]":
                                break
                            try:
                                chunk = json.loads(data_str)
                                delta = chunk['choices'][0].get('delta', {})
                                if 'content' in delta:
                                    yield delta['content']
                            except json.JSONDecodeError:
                                continue

        yielded = False
        # Try Groq first
        if GROQ_API_KEY:
            try:
                for chunk in stream_provider(GROQ_API_KEY, GROQ_URL, GROQ_MODEL):
                    yielded = True
                    yield chunk
                if yielded:
                    return
            except Exception as e:
                yield f"\n[Groq failed, trying Mistral...]\n"

        # Fallback to Mistral
        if MISTRAL_API_KEY:
            try:
                for chunk in stream_provider(MISTRAL_API_KEY, MISTRAL_URL, MISTRAL_MODEL):
                    yielded = True
                    yield chunk
                if yielded:
                    return
            except Exception as e:
                yield f"\n\n[Error: Groq and Mistral both failed. Mistral error: {str(e)}]"
                return

        if not yielded:
            yield "\n\n[Error: No AI provider available. Set GROQ_API_KEY or MISTRAL_API_KEY.]"

    return Response(generate(), mimetype='text/plain')

if __name__ == '__main__':
    print(f"Server starting...")
    print(f"AI provider: {AI_PROVIDER}")
    key_status = "set" if (GROQ_API_KEY if AI_PROVIDER=='groq' else DEEPSEEK_API_KEY) else "MISSING"
    print(f"API key: {key_status}")
    if AI_PROVIDER == 'groq':
        print(f"Groq model: {GROQ_MODEL}")
    print(f"Files indexed: {len(FILE_MAP)}")
    # Print stats
    by_class = {}
    for (cls, subj) in FILE_MAP:
        by_class.setdefault(cls, 0)
        by_class[cls] += 1
    for cls in sorted(by_class):
        print(f"  {cls}: {by_class[cls]} files")
    app.run(host='127.0.0.1', port=5000, debug=True)
