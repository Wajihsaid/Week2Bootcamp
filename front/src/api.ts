export async function askQuestion(question: string) {
  const res = await fetch("http://localhost:8000/ask", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question })
  });

  return res.json();
}
