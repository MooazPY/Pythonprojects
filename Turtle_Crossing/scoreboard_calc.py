from turtle import Turtle

FONT = ("Courier",24,"normal")

class Score(Turtle):
    def __init__(self):
        super().__init__()
        self.penup()
        self.color("black")
        self.goto(-210,260)
        self.hideturtle()
        self.level = 1
        self.score()
        

    def score(self):
        self.write(f"Level : {self.level}",False,"center",FONT)
        
    
    def update(self):
        self.level +=1
        self.clear()
        self.score()
        
        
    def game_over(self):
        over = Turtle()
        over.color("black")
        over.penup()
        over.hideturtle()
        over.write("GAME OVER",False,"center",FONT)