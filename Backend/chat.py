from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from transformers import pipeline

DB_PATH = "vector_db"

# Load embeddings
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Load FAISS DB
db = FAISS.load_local(
    DB_PATH,
    embeddings,
    allow_dangerous_deserialization=True
)

# Load LLM
llm = pipeline(
    "text-generation",
    model="google/flan-t5-base",
    max_new_tokens=256
)

def ask(question: str) -> str:
    question = question.strip()

    # 🚫 block casual / meaningless questions
    if len(question.split()) < 3:
        return "This chatbot only answers questions related to the provided Alzheimer research papers."

    # Retrieve top documents with similarity scores
    docs_with_scores = db.similarity_search_with_score(question, k=3)

    # lower score = better match (STRICT filtering)
    docs = [doc for doc, score in docs_with_scores if score < 0.4]

    if not docs:
        return "Sorry, this is not covered in the provided research papers."

    # Build context
    context = "\n\n".join(doc.page_content for doc in docs)

    prompt = f"""
You are a medical research assistant.

Answer the QUESTION using ONLY the information from the CONTEXT.
Write a clear, natural, human-like answer in 2–4 complete sentences.
Do NOT list keywords.
Do NOT copy the context.
Do NOT add external knowledge.

If the answer is not explicitly stated in the context, reply exactly:
"Sorry, this is not covered in the provided research papers."

CONTEXT:
{context}

QUESTION:
{question}

ANSWER:
"""

    result = llm(prompt)
    answer = result[0]["generated_text"].strip()

    # 🛑 safety fallback
    if len(answer.split()) < 8:
        return "Sorry, this is not covered in the provided research papers."

    return answer


if __name__ == "__main__":
    print("🧠 Alzheimer Research Chatbot")
    while True:
        q = input("\nAsk a question (type exit to quit): ")
        if q.lower() == "exit":
            break
        print(ask(q))
