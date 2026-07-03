const pdfLookup = require('./pdf_lookup.json');

exports.handler = async (event) => {
  const params = event.queryStringParameters || {};
  const cls = params.class || '';
  const subj = params.subject || '';

  if (!cls || !subj) {
    return {
      statusCode: 400,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ error: 'Missing class or subject parameter', available: false })
    };
  }

  const key = cls + '|' + subj;
  const pdfUrl = pdfLookup[key] || null;

  return {
    statusCode: 200,
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      pdf_url: pdfUrl,
      available: pdfUrl !== null
    })
  };
};
