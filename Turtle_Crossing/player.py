from turtle import Turtle

WIN_LINE = 280
INIT_POS = (0,-280)
MOVE_DISTANCE = 15

class Player(Turtle):
    def __init__(self):
        super().__init__()
        self.penup()
        self.setheading(90)
        self.shape("turtle")
        self.color("black")
        self.goto(INIT_POS)
        
    def up(self):
        """Let you to control the turtle up only"""
        if self.ycor() < WIN_LINE:
            self.forward(MOVE_DISTANCE)
        
        
    def check_win(self):
        """return true if the turtle cross the road"""
        if self.ycor() >= WIN_LINE:
            return 1
    
    
    def reset(self):
        """Set the position of the turtle to the first position when he cross the road"""
        self.goto(INIT_POS)
