import requests
import json
from datetime import datetime

class QuizService:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.deepseek.com/v1"  # Example API endpoint
    
    def generate_quiz(self, transcript, question_type="multiple_choice", num_questions=5, video_id=None):
        """Generate quiz questions from transcript"""
        try:
            # Prepare the transcript text
            transcript_text = " ".join([t['text'] for t in transcript])
            
            # Call the DeepSeek API (example implementation)
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'model': 'quiz-generator',
                'prompt': f"""
                Generate {num_questions} {question_type} questions based on the following video transcript.
                For each question, provide:
                - The question text
                - 4 possible answers (for multiple choice)
                - The correct answer
                - A brief explanation of why this is the correct answer
                
                The questions should test understanding of key concepts in the transcript.
                The difficulty should vary from easy to moderate.
                
                Transcript:
                {transcript_text}
                """,
                'max_tokens': 2000,
                'temperature': 0.7
            }
            
            # In a real implementation, this would call the actual API
            # response = requests.post(f"{self.base_url}/completions", headers=headers, json=payload)
            # response.raise_for_status()
            # data = response.json()
            
            # For demo purposes, we'll use mock data
            data = self._mock_quiz_generation(transcript_text, num_questions, question_type)
            
            return {
                'success': True,
                'video_id': video_id,
                'timestamp': datetime.now().isoformat(),
                'questions': data['questions']
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _mock_quiz_generation(self, transcript, num_questions, question_type):
        """Mock quiz generation for demo purposes"""
        # This would be replaced with actual API calls in production
        sample_questions = [
            {
                'question': 'What was the main topic discussed in the video?',
                'options': [
                    'History of the internet',
                    'Machine learning algorithms',
                    'Quantum computing basics',
                    'How to bake a cake'
                ],
                'correct_answer': 'Quantum computing basics',
                'explanation': 'The transcript focused primarily on introducing quantum computing concepts.'
            },
            {
                'question': 'What is a qubit in quantum computing?',
                'options': [
                    'A type of quantum bike',
                    'The basic unit of quantum information',
                    'A quantum measurement tool',
                    'A quantum encryption method'
                ],
                'correct_answer': 'The basic unit of quantum information',
                'explanation': 'The transcript explained that qubits are the fundamental units of quantum information, analogous to bits in classical computing.'
            }
        ]
        
        # Repeat sample questions to reach the requested number
        questions = []
        for i in range(num_questions):
            q_idx = i % len(sample_questions)
            question = sample_questions[q_idx].copy()
            question['question'] = f"{i+1}. {question['question']}"
            questions.append(question)
        
        return {'questions': questions}
