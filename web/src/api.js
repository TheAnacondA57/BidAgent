const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

async function post(path, body) {
  const response = await fetch(`${API_URL}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!response.ok) throw new Error(`L'API a répondu ${response.status}`);
  return response.json();
}

export const askQuestion = (question) => post('/query', { question });
export const askQuestionWithTrace = (question) => post('/query/trace', { question });
