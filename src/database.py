import psycopg2
import psycopg2.extras


DB_NAME = "triviaDB"
DB_PORT = 5432

def get_connection():
    conn = psycopg2.connect(
        dbname=DB_NAME,
        port=DB_PORT
    )
    return conn

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    create_table_query = """
    CREATE TABLE IF NOT EXISTS articles (
        id SERIAL PRIMARY KEY,
        title TEXT,
        link TEXT,
        content TEXT,
        publication_date TIMESTAMP,
        source TEXT,
        created_at TIMESTAMP DEFAULT NOW()
    );
    """
    cur.execute(create_table_query)
    conn.commit()
    cur.close()
    conn.close()

def insert_article(title, link, content, publication_date=None, source=None):
    """Insère un article dans la table articles."""
    conn = get_connection()
    cur = conn.cursor()
    insert_query = """
        INSERT INTO articles (title, link, content, publication_date, source)
        VALUES (%s, %s, %s, %s, %s)
    """
    cur.execute(insert_query, (title, link, content, publication_date, source))
    conn.commit()
    cur.close()
    conn.close()

def article_exists_in_db(link):
    # Requête SQL pour vérifier si l'article existe déjà
    # SELECT COUNT(*) FROM articles WHERE link = %s
    pass

