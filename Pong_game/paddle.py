from turtle import Turtle
INI_SCORE = [0,0]
class Paddle(Turtle):
    def __init__(self,position):
        super().__init__()
        self.shape("square")
        self.penup()
        self.color("white")
        self.shapesize(stretch_wid=1,stretch_len=5)
        self.setheading(90)
        self.goto(position)
    
    def up(self):
        """Let the paddle move up"""
        if self.ycor() < 235:
            self.forward(30)
    
    
    def down(self):
        """Let the paddle move down"""
        if self.ycor() > -235:
            self.backward(30)


