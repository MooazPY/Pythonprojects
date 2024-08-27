class QuizBrain:

    def __init__(self, q_list):
        self.question_number = 0
        self.score = 0
        self.question_list = q_list
        # self.current_question = None

    def display_question(self):
        question = self.question_list[self.question_number]['question']
        return question
    
    def check_answer(self):
        answer = self.question_list[self.question_number]['correct_answer']
        return answer
    
    def next_ques(self):
        self.question_number += 1
    
    def increase_score(self):
        self.score += 1
        
    def end(self):
        return self.question_number == 10