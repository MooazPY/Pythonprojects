from turtle import Turtle
ALIGNMENT = "center"

class Score(Turtle):
    def __init__(self):
        super().__init__()
        self.score = 0
        self.color("white")
        self.penup()
        self.speed("fastest")
        self.goto(0,280)
        self.hideturtle()
        self.update()
        
    def update(self):
        self.write(f"Score: {self.score}",False,ALIGNMENT,(24))
    
    def game_over(self):
        self.goto(0,0)
        self.write(f"Game Over ",False,ALIGNMENT,(50))
        

    
    def increase(self):
        self.score += 1
        self.clear()
        self.update()


