const https = require('https');

const GROQ_API_KEY = process.env.GROQ_API_KEY || '';
const GROQ_URL = 'https://api.groq.com/openai/v1/chat/completions';
const GROQ_MODEL = process.env.GROQ_MODEL || 'llama-3.3-70b-versatile';

const MISTRAL_API_KEY = process.env.MISTRAL_API_KEY || 'u0YMFGONYPEqZHTEChuOUUr9Sw4QZUBI';
const MISTRAL_URL = 'https://api.mistral.ai/v1/chat/completions';
const MISTRAL_MODEL = process.env.MISTRAL_MODEL || 'mistral-small-latest';

function callProvider(apiKey, apiUrl, model, payload) {
  return new Promise((resolve, reject) => {
    const body = JSON.stringify({
      model,
      messages: [
        { role: 'system', content: payload.systemPrompt },
        { role: 'user', content: payload.userPrompt }
      ],
      temperature: 0.7,
      max_tokens: 4096,
      stream: false
    });

    const url = new URL(apiUrl);
    const options = {
      hostname: url.hostname,
      path: url.pathname,
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(body)
      },
      timeout: 120000
    };

    const req = https.request(options, (res) => {
      let responseBody = '';
      res.on('data', (chunk) => { responseBody += chunk; });
      res.on('end', () => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          try {
            const data = JSON.parse(responseBody);
            resolve(data.choices?.[0]?.message?.content || '');
          } catch {
            reject(new Error(`Invalid JSON response: ${responseBody.substring(0, 200)}`));
          }
        } else {
          let errMsg = `${model} API error: ${res.statusCode}`;
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
    req.on('timeout', () => { req.destroy(); reject(new Error(`${model} timed out`)); });
    req.write(body);
    req.end();
  });
}

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
  const fileContent = data.fileContent || '';
  const isStream = data.stream === true;

  if (!fileContent) {
    const err = 'Could not read textbook file. Make sure the markdown file exists in the repo.';
    if (isStream) return { statusCode: 200, headers: { 'Content-Type': 'text/plain' }, body: err };
    return { statusCode: 502, headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ error: err }) };
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

  const userPrompt = `Here is the full textbook content for ${subjectHeader}:

=== BEGIN TEXTBOOK CONTENT ===
${fileContent.substring(0, 12000)}
=== END TEXTBOOK CONTENT ===

${chapterContext}
Student's request: ${query}`;

  const payload = { systemPrompt, userPrompt };
  let answer = '';
  let modelUsed = '';

  // Try Groq first
  if (GROQ_API_KEY) {
    try {
      answer = await callProvider(GROQ_API_KEY, GROQ_URL, GROQ_MODEL, payload);
      modelUsed = GROQ_MODEL;
    } catch (e) {
      console.log('Groq failed:', e.message);
    }
  }

  // Fallback to Mistral if Groq failed or returned empty
  if (!answer && MISTRAL_API_KEY) {
    try {
      answer = await callProvider(MISTRAL_API_KEY, MISTRAL_URL, MISTRAL_MODEL, payload);
      modelUsed = MISTRAL_MODEL;
    } catch (e) {
      console.log('Mistral also failed:', e.message);
      const err = `Both AI providers failed. Groq: ${!GROQ_API_KEY ? 'no key' : 'error'}, Mistral: error - ${e.message}`;
      if (isStream) return { statusCode: 200, headers: { 'Content-Type': 'text/plain' }, body: `Error: ${err}` };
      return { statusCode: 502, headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ error: err }) };
    }
  }

  if (!answer) {
    const err = 'No AI provider available. Set GROQ_API_KEY or MISTRAL_API_KEY in environment variables.';
    if (isStream) return { statusCode: 200, headers: { 'Content-Type': 'text/plain' }, body: `Error: ${err}` };
    return { statusCode: 502, headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ error: err }) };
  }

  if (isStream) {
    return { statusCode: 200, headers: { 'Content-Type': 'text/plain' }, body: answer };
  }

  return {
    statusCode: 200,
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ answer, model: modelUsed })
  };
};
