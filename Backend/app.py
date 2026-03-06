from flask import Flask, request, jsonify
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from transformers import pipeline
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow frontend on another port

DB_PATH = "vector_db"

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

db = FAISS.load_local(DB_PATH, embeddings, allow_dangerous_deserialization=True)

llm = pipeline(
    "text2text-generation",
    model="google/flan-t5-large",
    max_new_tokens=128
)


@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    question = data.get("question", "").strip()

    # 🚫 Block casual / irrelevant questions
    casual_questions = ["hi", "hello", "how are you", "hey", "who are you"]
    if question.lower() in casual_questions:
        return jsonify({
            "answer": "Sorry, this chatbot only answers questions related to the provided Alzheimer research papers."
        })

    docs = db.similarity_search(question, k=3)

    if not docs:
        return jsonify({
            "answer": "Sorry, this is not covered in the provided research papers."
        })

    context = "\n\n".join(doc.page_content for doc in docs)

    prompt = f"""
Answer the question using ONLY the information from the context.
Do NOT repeat the context.
Answer in 2–4 complete sentences.
If the answer is not explicitly stated, reply:
"Sorry, this is not covered in the provided research papers."

Context:
{context}

Question:
{question}

Answer:
"""

    result = llm(prompt)
    answer = result[0]["generated_text"].strip()

    # 🛑 Final safety check
    if len(answer) < 10:
        answer = "Sorry, this is not covered in the provided research papers."

    return jsonify({"answer": answer})


if __name__ == "__main__":
    app.run(port=5000)
