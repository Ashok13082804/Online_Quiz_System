import json
import os
from models import db, Quiz, Question
import random

def generate_quiz_gemini(topic, num_questions):
    api_key = os.environ.get('GEMINI_API_KEY')
    
    # ── Fallback Mode (No API Key) ──
    if not api_key:
        print("GEMINI_API_KEY not found. Using offline fallback generation mode.")
        quiz = Quiz(
            title=f"{topic} Master Challenge",
            description=f"A dynamic offline-generated test about {topic}.",
            time_limit=num_questions * 60
        )
        db.session.add(quiz)
        db.session.flush()
        
        # Templates for dummy questions related to the topic
        templates = [
            ("Which of the following is most strongly associated with {topic}?", "The core methodology", "It is unrelated", "Only its early versions", "It avoids this entirely", "The core methodology"),
            ("What is the primary benefit of understanding {topic}?", "Improved problem-solving", "Reduced screen time", "Physical fitness", "Better sleep", "Improved problem-solving"),
            ("Who was the leading pioneer involved in {topic}?", "Leading researchers", "Marie Curie", "Albert Einstein", "Isaac Newton", "Leading researchers"),
            ("When did {topic} begin gaining widespread recognition?", "Late 20th century", "Ancient Rome", "During the 1800s", "It hasn't yet", "Late 20th century"),
            ("What is the biggest challenge when dealing with {topic}?", "Complexity of variables", "Gravity", "High temperature", "Lack of colors", "Complexity of variables"),
            ("In what context is {topic} most effectively utilized?", "Modern environments", "Space travel", "Ocean depths", "Never used", "Modern environments"),
            ("Which fundamental principle drives {topic}?", "Systemic logic", "Chaos theory", "Thermodynamics", "Quantum entanglement", "Systemic logic"),
            ("What future trend will heavily impact {topic}?", "Artificial Intelligence", "Fax machines", "Floppy disks", "Steam engines", "Artificial Intelligence")
        ]
        
        random.shuffle(templates)
        for i in range(num_questions):
            q_template = templates[i % len(templates)]
            
            question = Question(
                quiz_id=quiz.id,
                question_text=q_template[0].format(topic=topic),
                option1=q_template[1], option2=q_template[2],
                option3=q_template[3], option4=q_template[4],
                correct_answer=q_template[5]
            )
            # Shuffle options
            opts = [question.option1, question.option2, question.option3, question.option4]
            random.shuffle(opts)
            question.option1, question.option2, question.option3, question.option4 = opts
            
            db.session.add(question)
            
        db.session.commit()
        return quiz.id

    # ── Online Mode (API Key Present) ──
    try:
        import google.generativeai as genai
    except ImportError:
        raise Exception("google-generativeai package missing. Install it using pip.")
        
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
    You are an expert quiz generator. Generate a multiple-choice quiz about "{topic}" with exactly {num_questions} questions.
    Return ONLY a valid JSON object matching this schema, completely without markdown wrappers:
    {{
        "title": "A catchy title for the quiz",
        "description": "A short 1-sentence description",
        "questions": [
            {{
                "question": "The question text",
                "options": ["A", "B", "C", "D"],
                "correct": "The exact string of the correct option"
            }}
        ]
    }}
    Make sure the correct answer is exactly one of the options.
    """
    
    response = model.generate_content(prompt)
    response_text = response.text.strip()
    
    if response_text.startswith("```json"):
        response_text = response_text[7:]
    if response_text.startswith("```"):
        response_text = response_text[3:]
    if response_text.endswith("```"):
        response_text = response_text[:-3]
        
    data = json.loads(response_text.strip())
    
    quiz = Quiz(
        title=data['title'],
        description=data['description'],
        time_limit=num_questions * 60
    )
    db.session.add(quiz)
    db.session.flush()
    
    for q in data['questions']:
        opts = q['options']
        while len(opts) < 4:
            opts.append("Other")
            
        opts = opts[:4] # Ensure exactly 4
        
        question = Question(
            quiz_id=quiz.id,
            question_text=q['question'],
            option1=opts[0], option2=opts[1],
            option3=opts[2], option4=opts[3],
            correct_answer=q['correct']
        )
        db.session.add(question)
        
    db.session.commit()
    return quiz.id
