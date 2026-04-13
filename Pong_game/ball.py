from turtle import Turtle
class Ball(Turtle):
    def __init__(self):
        super().__init__()
        self.shape("circle")
        self.penup()
        self.color("blue")
        self.shapesize(1)
        self.x_move = 10
        self.y_move = 10

    def move(self):
        """Let the ball move"""
        x_cor = self.xcor() + self.x_move
        y_cor = self.ycor() + self.y_move
        self.goto(x_cor,y_cor)
    
    def bounce_y(self):
        """let the ball reverse its direction in y axis"""
        self.y_move *= -1
    
    def bounce_x(self):
        """let the ball reverse its direction in x axis"""

        self.x_move *= -1
    
    def reset(self):
        """Basically reset the ball position to (0,0) after scoring"""
        self.goto(0,0)