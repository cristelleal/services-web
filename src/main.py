from response_checker import verify_and_score, generate_response
from database import get_connection

def fetch_questions():
    """Fetches all question IDs and their texts from the database."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, question_text FROM questions WHERE id BETWEEN 1 AND 4386;")
    questions = cur.fetchall()
    cur.close()
    conn.close()
    return questions

def run_trivia():
    """Loops through questions, generates AI responses, and scores them."""
    questions = fetch_questions()
    
    for question_id, question_text in questions:
        print(f"\nQuestion ID {question_id}: {question_text}")
        
        # Generate AI response using Llama 3
        ai_answer = generate_response(question_text)
        print("AI Answer:", ai_answer)
        
        # Verify and score the AI's response
        result = verify_and_score(question_id, ai_answer)
        print("Result:", result)
    
    print("\nTrivia game completed!")

if __name__ == "__main__":
    run_trivia()
