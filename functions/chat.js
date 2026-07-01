const fs = require('fs');
const path = require('path');
const https = require('https');

const SITE_ROOT = process.cwd();
const GROQ_API_KEY = process.env.GROQ_API_KEY || '';
const GROQ_URL = 'https://api.groq.com/openai/v1/chat/completions';
const GROQ_MODEL = process.env.GROQ_MODEL || 'llama-3.3-70b-versatile';

function buildFileMap() {
  const fmap = {};
  for (let i = 1; i <= 10; i++) {
    const clsDir = path.join(SITE_ROOT, `Class ${i}`);
    try {
      const entries = fs.readdirSync(clsDir, { withFileTypes: true });
      for (const ent of entries) {
        if (!ent.name.endsWith('.md') || ent.name.includes('DUPLICATE')) continue;
        const stem = ent.name.replace(/\.md$/, '');
        const m = stem.match(/^Class\s+\d+\s+(.+)$/);
        if (m) {
          fmap[`Class ${i}|${m[1].trim()}`] = path.join(clsDir, ent.name);
        }
      }
    } catch (_) {
      // Directory doesn't exist
    }
  }
  return fmap;
}

const FILE_MAP = buildFileMap();

exports.handler = async (event, context) => {
  if (event.httpMethod !== 'POST') {
    return { statusCode: 405, body: 'Method Not Allowed' };
  }

  let data;
  try {
    data = JSON.parse(event.body);
  } catch {
    return { statusCode: 400, headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ error: 'Invalid JSON' }) };
  }

  const cls = data.class || '';
  const subj = data.subject || '';
  const chapterIndex = data.chapterIndex;
  const query = data.query || '';
  const mode = data.mode || 'ask';

  const isStream = data.stream === true;

  // Resolve file path
  let filePath = FILE_MAP[`${cls}|${subj}`];
  if (!filePath) {
    for (const [key, p] of Object.entries(FILE_MAP)) {
      const [c, s] = key.split('|');
      if (c === cls && (s.toLowerCase() === subj.toLowerCase() || s.toLowerCase().includes(subj.toLowerCase()) || subj.toLowerCase().includes(s.toLowerCase()))) {
        filePath = p;
        break;
      }
    }
  }
  if (!filePath) {
    return {
      statusCode: 404,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ error: `File not found for ${cls}/${subj}` })
    };
  }

  // Read file content
  let content;
  try {
    content = fs.readFileSync(filePath, 'utf-8');
  } catch (e) {
    return {
      statusCode: 500,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ error: `Failed to read file: ${e.message}` })
    };
  }

  const subjectHeader = `${cls} - ${subj}`;
  const systemPrompts = {
    mcq: `You are an AI tutor for ${subjectHeader}. Based on the textbook content below, generate 10 multiple-choice questions with 4 options each and an answer key. Focus on the most important concepts from the chapter. Format as:

## Multiple Choice Questions

1. **Question text?**
   - A) Option A
   - B) Option B
   - C) Option C
   - D) Option D
   **Answer:** A) Option A

(Continue for all 10 questions)`,

    mindmap: `You are an AI tutor for ${subjectHeader}. Based on the textbook content below, create a detailed mind map / concept map of the chapter. Use indentation to show hierarchy. Format as:

## Mind Map: [Chapter Title]

- Main Concept 1
  - Sub-concept 1.1
    - Detail 1.1.1
    - Detail 1.1.2
  - Sub-concept 1.2
- Main Concept 2
  - Sub-concept 2.1
...`,

    exercise: `You are an AI tutor for ${subjectHeader}. Based on the textbook content below, create a practice exercise set with:
1. 5 short-answer questions
2. 3 numerical/long-answer problems
3. A brief answer key

Format clearly with sections.`,

    ask: `You are an AI tutor for ${subjectHeader}. Answer the student's question based on the textbook content below. Be thorough, educational, and use examples from the text. If the question is off-topic, politely redirect to the subject matter.`
  };

  const systemPrompt = systemPrompts[mode] || systemPrompts.ask;
  let chapterContext = '';
  if (chapterIndex !== null && chapterIndex !== undefined) {
    chapterContext = `\n(The student is asking about Chapter ${chapterIndex + 1})`;
  }

  const truncatedContent = content.substring(0, 12000);
  const userPrompt = `Here is the full textbook content for ${subjectHeader}:

=== BEGIN TEXTBOOK CONTENT ===
${truncatedContent}
=== END TEXTBOOK CONTENT ===

${chapterContext}
Student's request: ${query}`;

  const groqPayload = JSON.stringify({
    model: GROQ_MODEL,
    messages: [
      { role: 'system', content: systemPrompt },
      { role: 'user', content: userPrompt }
    ],
    temperature: 0.7,
    max_tokens: 4096,
    stream: false
  });

  try {
    const result = await new Promise((resolve, reject) => {
      const url = new URL(GROQ_URL);
      const options = {
        hostname: url.hostname,
        path: url.pathname,
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${GROQ_API_KEY}`,
          'Content-Type': 'application/json',
          'Content-Length': Buffer.byteLength(groqPayload)
        },
        timeout: 120000
      };

      const req = https.request(options, (res) => {
        let responseBody = '';
        res.on('data', (chunk) => { responseBody += chunk; });
        res.on('end', () => {
          if (res.statusCode >= 200 && res.statusCode < 300) {
            try {
              resolve(JSON.parse(responseBody));
            } catch {
              reject(new Error(`Invalid JSON response: ${responseBody.substring(0, 200)}`));
            }
          } else {
            let errMsg = `Groq API error: ${res.statusCode}`;
            try {
              const errData = JSON.parse(responseBody);
              errMsg += ` - ${errData.error?.message || responseBody.substring(0, 200)}`;
            } catch {
              errMsg += ` - ${responseBody.substring(0, 200)}`;
            }
            reject(new Error(errMsg));
          }
        });
      });

      req.on('error', (e) => reject(new Error(`Request failed: ${e.message}`)));
      req.on('timeout', () => { req.destroy(); reject(new Error('Groq API timed out')); });
      req.write(groqPayload);
      req.end();
    });

    const answer = result.choices?.[0]?.message?.content || '';
    const usage = result.usage || {};

    if (isStream) {
      return {
        statusCode: 200,
        headers: { 'Content-Type': 'text/plain' },
        body: answer
      };
    }

    return {
      statusCode: 200,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ answer, usage, model: GROQ_MODEL })
    };

  } catch (e) {
    return {
      statusCode: 502,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ error: e.message })
    };
  }
};
