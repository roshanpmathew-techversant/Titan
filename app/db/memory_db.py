import psycopg2
from app.core.settings import get_settings

settings = get_settings()
DB_URL = settings.MEMORY_PG_CLOUD

# Gemini embeddings are 3072 dimensions
EMBEDDING_DIM = 3072


def initialize_memory_schema():
    conn = psycopg2.connect(DB_URL)
    print("DB Connected")
    cursor = conn.cursor()

    # Enable pgvector
    cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")

    # -------------------------
    # USERS TABLE
    # -------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            created_at TIMESTAMP DEFAULT NOW()
        );
    """)

    # -------------------------
    # USER CHATS TABLE
    # -------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_chats(
            chat_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL REFERENCES users(user_id),
            created_at TIMESTAMP DEFAULT NOW()
        );
    """)

    # -------------------------
    # USER MEMORY TABLE
    # -------------------------
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS user_memory (
            id SERIAL PRIMARY KEY,
            user_id TEXT NOT NULL REFERENCES users(user_id),
            chat_id TEXT NOT NULL REFERENCES user_chats(chat_id),
            memory_text TEXT NOT NULL,
            response_text TEXT NOT NULL,
            embedding vector({EMBEDDING_DIM}) NOT NULL,
            created_at TIMESTAMP DEFAULT NOW()
        );
    """)

    conn.commit()

    # -------------------------
    # Ensure Correct Vector Dimension
    # -------------------------
    cursor.execute("""
        SELECT atttypmod
        FROM pg_attribute
        WHERE attrelid = 'user_memory'::regclass
        AND attname = 'embedding';
    """)

    result = cursor.fetchone()

    if result:
        current_dim = result[0] - 4  # pgvector stores dimension as typmod-4

        if current_dim != EMBEDDING_DIM:
            print(f"Updating embedding dimension from {current_dim} → {EMBEDDING_DIM}")

            # Required: incompatible vector sizes cannot coexist
            cursor.execute("TRUNCATE TABLE user_memory;")

            # Drop any existing ANN index
            cursor.execute("DROP INDEX IF EXISTS user_memory_embedding_idx;")

            # Alter column type
            cursor.execute(f"""
                ALTER TABLE user_memory
                ALTER COLUMN embedding TYPE vector({EMBEDDING_DIM});
            """)

            conn.commit()

    # -------------------------
    # Ensure No ANN Index Exists
    # -------------------------
    cursor.execute("DROP INDEX IF EXISTS user_memory_embedding_idx;")

    cursor.execute("ANALYZE user_memory;")

    conn.commit()
    cursor.close()
    conn.close()

    print("Memory schema initialized successfully.")