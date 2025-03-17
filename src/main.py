import psycopg2
import psycopg2.extras
import requests
import json
import time

DB_NAME = "triviaDB"
DB_PORT = 5432

def get_connection():
    """Establishes a connection to the PostgreSQL database."""
    conn = psycopg2.connect(
        dbname=DB_NAME,
        port=DB_PORT
    )
    return conn

def init_db():
    """Initializes the database with necessary tables for the trivia game."""
    conn = get_connection()
    cur = conn.cursor()
    
    create_tables_query = """
    CREATE TABLE IF NOT EXISTS categories (
        id SERIAL PRIMARY KEY,
        name TEXT UNIQUE NOT NULL
    );

    CREATE TABLE IF NOT EXISTS questions (
        id SERIAL PRIMARY KEY,
        question_text TEXT UNIQUE NOT NULL,
        category_id INTEGER REFERENCES categories(id),
        created_at TIMESTAMP DEFAULT NOW()
    );

    CREATE TABLE IF NOT EXISTS answers (
        id SERIAL PRIMARY KEY,
        question_id INTEGER REFERENCES questions(id) ON DELETE CASCADE,
        answer_text TEXT NOT NULL,
        is_correct BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT NOW()
    );
    """
    cur.execute(create_tables_query)
    conn.commit()
    cur.close()
    conn.close()

def insert_category(name):
    """Inserts a new category into the database if it does not exist."""
    conn = get_connection()
    cur = conn.cursor()
    insert_query = """
        INSERT INTO categories (name) VALUES (%s)
        ON CONFLICT (name) DO NOTHING
        RETURNING id;
    """
    cur.execute(insert_query, (name,))
    category_id = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return category_id[0] if category_id else None

def question_exists(question_text):
    """Checks if a question already exists in the database."""
    conn = get_connection()
    cur = conn.cursor()
    query = """
        SELECT COUNT(*) FROM questions WHERE question_text = %s;
    """
    cur.execute(query, (question_text,))
    exists = cur.fetchone()[0] > 0
    cur.close()
    conn.close()
    return exists

def insert_question(question_text, category_name):
    """Inserts a new trivia question into the database if it does not already exist."""
    if question_exists(question_text):
        return None
    
    category_id = insert_category(category_name)
    conn = get_connection()
    cur = conn.cursor()
    
    insert_query = """
        INSERT INTO questions (question_text, category_id) 
        VALUES (%s, %s) RETURNING id;
    """
    cur.execute(insert_query, (question_text, category_id))
    question_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return question_id

def insert_answer(question_id, answer_text, is_correct=False):
    """Inserts an answer linked to a trivia question."""
    conn = get_connection()
    cur = conn.cursor()
    insert_query = """
        INSERT INTO answers (question_id, answer_text, is_correct) 
        VALUES (%s, %s, %s);
    """
    cur.execute(insert_query, (question_id, answer_text, is_correct))
    conn.commit()
    cur.close()
    conn.close()

def scrape_trivia():
    """Fetches trivia questions from OpenTDB and stores them in the database."""
    token = requests.get('https://opentdb.com/api_token.php?command=request').json()['token']
    db = {}
    amount = 50
    
    while True:
        response = requests.get(f'https://opentdb.com/api.php?amount={amount}&token={token}')
        data = response.json()

        if 'results' not in data or not data['results']:
            print('Finished or rate limited', response.status_code)
            break

        for result in data['results']:
            question_text = result['question']
            category = result['category']
            correct_answer = result['correct_answer']
            incorrect_answers = result['incorrect_answers']

            if question_text in db:  # Avoid duplicates in memory
                continue
            
            # if question_exists(question_text):  # Avoid duplicates in database
            #     continue

            db[question_text] = result
            question_id = insert_question(question_text, category)
            if question_id:
                insert_answer(question_id, correct_answer, True)
                for answer in incorrect_answers:
                    insert_answer(question_id, answer, False)

        print(f'Total Questions Fetched: {len(db)}')
       
        if len(db) >= 4300:
            amount = 1
            
        # API rate limiting
        time.sleep(5)

    with open('trivia_db.json', 'w') as file:
        json.dump(list(db.values()), file)

if __name__ == '__main__':
    init_db()  # Ensure the database is initialized before scraping
    scrape_trivia()
