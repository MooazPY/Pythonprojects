from turtle import Turtle
import random

CAR_HEAD = 180
CAR_DIS = 5
DIS_INC = 10
CARS_COLOR  = ["orange","red","green","blue","purple","yellow"]


class CarManager(Turtle):
    def __init__(self):
        # super().__init__()
        self.list_cars = []
        self.car_speed = CAR_DIS
        self.move()
    
    
    def move(self):
        for car in self.list_cars:
            car.forward(self.car_speed)
    
    
    def create_car(self):
        random_chance = random.randint(1,4)
        if random_chance == 1:
            for i in range(1):
                random_pos = (random.randint(280,290),random.randint(-250,260))
                random_color = (random.choice(CARS_COLOR))
                new_car = Turtle("square")
                new_car.penup()
                new_car.color(random_color)
                new_car.goto(random_pos)
                new_car.shapesize(stretch_len=2)
                new_car.setheading(CAR_HEAD)
            self.list_cars.append(new_car)
            
    
    def increase_speed(self):
        self.car_speed += DIS_INC
        self.move()

        
