from langchain.llms import Ollama
from database import get_connection

# Load the local Llama model via Ollama
llm = Ollama(model="llama3:3b")

def get_correct_answer(question_id):
    """Retrieve the correct answer from the database."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT answer_text FROM answers WHERE question_id = %s AND is_correct = TRUE", (question_id,))
    result = cur.fetchone()
    cur.close()
    conn.close()
    return result[0] if result else None

def generate_response(question):
    """Use the Llama 3 model to generate an answer."""
    prompt = f"Answer this trivia question in a short and concise way: {question}"
    return llm.invoke(prompt)

def score_answer(user_answer, correct_answer):
    """Use the Llama 3 model to compare the user answer and give a score."""
    prompt = f"""
    You are an AI trivia judge. Compare the given user answer to the correct answer and score it from 0 to 10.
    
    - User Answer: "{user_answer}"
    - Correct Answer: "{correct_answer}"
    
    Score the answer and explain why you gave that score.
    """
    return llm.invoke(prompt)

def save_score(question_id, user_answer, correct_answer, score):
    """Stores the score in the database."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO scores (question_id, user_answer, correct_answer, score) VALUES (%s, %s, %s, %s)",
        (question_id, user_answer, correct_answer, score)
    )
    conn.commit()
    cur.close()
    conn.close()

def calculate_global_score():
    """Calculates the total average score from all answers."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT AVG(score) FROM scores")
    result = cur.fetchone()
    cur.close()
    conn.close()
    return result[0] if result[0] is not None else 0

def verify_and_score(question_id, user_answer):
    """Retrieve correct answer, compare with user answer, store score, and calculate global score."""
    correct_answer = get_correct_answer(question_id)
    
    if not correct_answer:
        return {"error": "Correct answer not found in the database."}
    
    # Get score from Ollama
    evaluation = score_answer(user_answer, correct_answer)
    
    # Extract score from evaluation
    score = int([int(s) for s in evaluation.split() if s.isdigit()][0])  # Extracts first number in response
    
    # Store the score
    save_score(question_id, user_answer, correct_answer, score)
    
    # Calculate global score
    global_score = calculate_global_score()
    
    # Print results in console
    print("\n--- Question ID:", question_id)
    print("User Answer:", user_answer)
    print("Correct Answer:", correct_answer)
    print("Score:", score)
    print("Global Average Score:", global_score)
    print("AI Evaluation:\n", evaluation)
    
    return {
        "question_id": question_id,
        "user_answer": user_answer,
        "correct_answer": correct_answer,
        "score": score,
        "global_score": global_score,
        "evaluation": evaluation
    }
