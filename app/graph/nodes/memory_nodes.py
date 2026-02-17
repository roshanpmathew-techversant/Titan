import psycopg2
from app.graph.state import TitanState
from app.core.settings import get_settings

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from app.core.secrets import get_gemini_api_key


# ----------------------------
# Config
# ----------------------------

API_KEY = get_gemini_api_key()
settings = get_settings()
DB_URL = settings.MEMORY_PG_CLOUD

SIMILARITY_THRESHOLD = 0.85


# ----------------------------
# Embedding Model
# ----------------------------

embedder = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",
    google_api_key=API_KEY,
    
)


# ----------------------------
# Helpers
# ----------------------------

def get_memory_connection():
    return psycopg2.connect(DB_URL)


def embed_text_to_pgvector(text: str) -> str:
    """
    Converts embedding list into pgvector string format:
    [0.123,0.456,...]
    """
    embedding = embedder.embed_query(text)
    return "[" + ",".join(map(str, embedding)) + "]"


# ============================
# MEMORY RETRIEVE NODE
# ============================

def memory_retrieve_node(state: TitanState) -> TitanState:
    user_id = state.get("user_id")
    chat_id = state.get("chat_id")
    user_query = state.get("user_query")

    if not user_id or not chat_id or not user_query:
        state["memory_hit"] = False
        return state

    conn = get_memory_connection()
    cursor = conn.cursor()

    try:
        # Ensure user exists
        cursor.execute("""
            INSERT INTO users (user_id)
            VALUES (%s)
            ON CONFLICT (user_id) DO NOTHING;
        """, (user_id,))

        # Ensure chat exists
        cursor.execute("""
            INSERT INTO user_chats (chat_id, user_id)
            VALUES (%s, %s)
            ON CONFLICT (chat_id) DO NOTHING;
        """, (chat_id, user_id))

        conn.commit()

        query_embedding = embed_text_to_pgvector(user_query)

        cursor.execute("""
            SELECT response_text,
                   1 - (embedding <=> %s::vector) AS similarity
            FROM user_memory
            WHERE user_id = %s
              AND chat_id = %s
            ORDER BY embedding <=> %s::vector
            LIMIT 1;
        """, (query_embedding, user_id, chat_id, query_embedding))

        result = cursor.fetchone()

        if result:
            stored_response, similarity = result
            if similarity >= SIMILARITY_THRESHOLD:
                state["response"] = stored_response
                state["memory_hit"] = True
                return state

        state["memory_hit"] = False
        return state

    finally:
        cursor.close()
        conn.close()


# ============================
# MEMORY STORE NODE
# ============================

def memory_store_node(state: TitanState) -> TitanState:
    if state.get("memory_hit"):
        return state

    user_id = state.get("user_id")
    chat_id = state.get("chat_id")
    user_query = state.get("user_query")
    response = state.get("response")
    print(response)



    if not user_id or not chat_id or not user_query or not response:
        return state
    
    upper_response = response.upper()

    if any(word in upper_response for word in ["INVALID", "ERROR"]):
        print("Invalid Ans not stored in memory")
        return state

    conn = get_memory_connection()
    cursor = conn.cursor()

    try:
        embedding = embed_text_to_pgvector(user_query)

        cursor.execute("""
            INSERT INTO user_memory
            (user_id, chat_id, memory_text, response_text, embedding)
            VALUES (%s, %s, %s, %s, %s::vector);
        """, (user_id, chat_id, user_query, response, embedding))

        conn.commit()
        print('Memory Stored')
        return state

    finally:
        cursor.close()
        conn.close()