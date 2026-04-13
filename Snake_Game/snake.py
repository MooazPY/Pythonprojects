from turtle import Turtle

LIST_POSITIONS = [(0,0),(-20,0),(-40,0)]
UP = 90
DOWN = 270
LEFT = 180
RIGHT = 0

class Snake:
    def __init__(self):
        self.list_snakes = []
        self.create_snake()
        self.head = self.list_snakes[0]

    def create_snake(self):
        for pos in LIST_POSITIONS:
            self.add_snake(pos)

    def move(self):
            for snake in range(len(self.list_snakes) -1, 0, -1):
                new_x = self.list_snakes[snake - 1].xcor()
                new_y = self.list_snakes[snake - 1].ycor()
                self.list_snakes[snake].goto(new_x,new_y)
            self.head.forward(20)


    def right(self):
        if self.head.heading() != LEFT: 
            self.head.setheading(0)


    def up(self):
        if self.head.heading() != DOWN: 
            self.head.setheading(90)

    def down(self): 
        if self.head.heading() != UP: 
            self.head.setheading(270)

    def left(self):
        if self.head.heading() != RIGHT: 
            self.head.setheading(180)
        
        
    def check_cor(self):
        return self.list_snakes[0].xcor() , self.list_snakes[0].ycor()
    
    def tail_cor(self):
        x_cor = self.list_snakes[len(self.list_snakes) - 1].xcor()
        y_cor = self.list_snakes[len(self.list_snakes) - 1].ycor()
        return x_cor , y_cor
    
    
    def add_snake(self,pos):
        snake = Turtle("square")
        snake.color("white")
        snake.penup()
        snake.goto(pos)
        self.list_snakes.append(snake)
        
    def extend(self):
        self.add_snake(self.list_snakes[-1].position())

