from response_checker import verify_and_score, generate_response, create_tables_score
from database import get_connection
import random

def fetch_questions():
    """Fetches all question IDs, their texts, and possible answers from the database."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT q.id, q.question_text, a.answer_text, a.is_correct 
        FROM questions q 
        JOIN answers a ON q.id = a.question_id
        WHERE q.id BETWEEN 1 AND 4386;
    """)
    results = cur.fetchall()
    cur.close()
    conn.close()
    
    questions = {}
    for question_id, question_text, answer_text, is_correct in results:
        if question_id not in questions:
            questions[question_id] = {"question": question_text, "answers": []}
        questions[question_id]["answers"].append((answer_text, is_correct))
    
    return questions


def run_trivia():
    """Loops through questions, shuffles answers, generates AI responses, and scores them."""
    create_tables_score()  # Ensure the scores table exists
    questions = fetch_questions()
    
    for question_id, data in questions.items():
        question_text = data["question"]
        answers = data["answers"]
        
        # Shuffle answer options
        random.shuffle(answers)
        answer_texts = [a[0] for a in answers]  # Extract just the answer text
        
        print(f"\nQuestion ID {question_id}: {question_text}")
        # print("Answer Options:")
        # for i, answer in enumerate(answer_texts, 1):
        #     print(f"{i}. {answer}")
        
        # Generate AI response using Llama 3
        ai_answer = generate_response(question_text, answer_texts)
        print("AI Answer:", ai_answer)
        
        # Verify and score the AI's response
        result = verify_and_score(question_id, ai_answer)
        print("Result:", result)
    
    print("\nTrivia game completed!")

if __name__ == "__main__":
#    create_tables_score()
    run_trivia()
