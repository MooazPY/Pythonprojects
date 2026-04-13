import turtle as t
import random

screen = t.Screen()
t.colormode(255)

color_list = [(80, 177, 230), (252, 241, 246), (229, 225, 97), (238, 48, 84), (121, 226, 187), (54, 80, 159), (228, 120, 79), (165, 47, 86), (226, 128, 174), (128, 195, 131), (244, 65, 49), (188, 21, 35), (190, 52, 37), (56, 46, 126), (31, 168, 196), (248, 163, 159), (71, 38, 48), (63, 45, 35), (38, 210, 210), (233, 167, 181), (140, 212, 227), (100, 114, 170), (250, 6, 20), (183, 182, 215), (135, 36, 33), (171, 128, 80), (70, 68, 45)]

def random_color():
    color = random.choice(color_list)
    r = color[0]
    g = color[1]
    b = color[2]
    color_tuple = (r,g,b)
    return color_tuple

new_turtle = t.Turtle()
new_turtle.penup()
new_turtle.setx(-220)
new_turtle.sety(-220)
y_axis = new_turtle.ycor()
new_turtle.shape("classic")
new_turtle.speed("normal")
new_turtle.pensize(2)

for i in range(10):
    for j in range(10):
        rgb = random_color()
        new_turtle.dot(20,(rgb)) 
        new_turtle.forward(50)
        
    y_axis += 50
    new_turtle.sety(y_axis)
    new_turtle.setx(-220)
    
new_turtle.hideturtle()

screen.exitonclick()