from turtle import Turtle

class Scoreboard(Turtle):
    
    def __init__(self):
        super().__init__()
        self.penup()
        self.color("white")
        self.hideturtle()
        self.l_score = 0
        self.r_score = 0
        self.write_score()
        
    def write_score(self):
        """Show to score on the screen"""
        self.goto(-100,200)
        self.write(self.l_score,False,"center",("Courier",80,"normal"))
        self.goto(100,200)
        self.write(self.r_score,False,"center",("Courier",80,"normal"))
        
    def increase_lscore(self):
        """Increase the left score"""
        self.l_score+=1
        self.clear()
        self.write_score()
        
        
    def increase_rscore(self):
        """Increase the right score"""
        self.r_score+=1
        self.clear()
        self.write_score()
    
    
    def draw_net(self):
        """Basically create a new turtle object to draw the net"""
        net = Turtle()
        net.color("white")
        net.penup()
        net.goto(0,-280)
        net.pensize(5)
        net.setheading(90)
        while(net.ycor()) < 280:
            net.forward(20)
            net.pendown()
            net.forward(20)
            net.penup()
        net.hideturtle()


