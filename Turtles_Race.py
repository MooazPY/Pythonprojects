from turtle import Screen , Turtle
import random

screen = Screen()
screen.setup(width=500,height=400)
user_guess =  screen.textinput("لعبه سباق السلاحف", "Which turtle gonna win: ")

start_y = -100
start_x = -230

list_of_turtles = []
list_of_colors = ["red","orange","yellow","green","purple","blue"]
for i in list_of_colors:
    new_turtle = Turtle()
    new_turtle.penup()
    new_turtle.shape("turtle")
    new_turtle.color(i)
    new_turtle.goto(start_x,start_y)
    list_of_turtles.append(new_turtle)
    start_y += 40

flag = True

while flag:
    for i in range(len(list_of_turtles)):
        current_turtle = list_of_turtles[i]
        current_turtle.forward(random.randint(1,10))
        current_turtle_x_axis = current_turtle.xcor()
        if current_turtle_x_axis >= 220:
            winner = current_turtle.pencolor()
            print(f"The winner is the {current_turtle.pencolor()} turtle")
            flag = False
            break
            
    
if user_guess == winner:
    print("Your prediction is right.")
else:
    print("You predict a wrong turtle.")

screen.exitonclick()
