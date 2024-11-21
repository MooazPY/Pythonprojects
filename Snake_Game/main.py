from turtle import Screen
import time
from snake import Snake 
from food import Food
from score import Score

screen = Screen()
screen.bgcolor("black")
screen.setup(600,600)
screen.title("Snake Game")
screen.tracer(0)


new_snake = Snake()
new_food =  Food()
new_food.refresh()
new_score = Score()

screen.onkey(new_snake.right,"Right")
screen.onkey(new_snake.up,"Up")
screen.onkey(new_snake.down,"Down")
screen.onkey(new_snake.left,"Left")

screen.listen()

game_is_on = True
while game_is_on:
    screen.update()
    time.sleep(0.1)
    new_snake.move()
    
    if new_snake.head.distance(new_food) < 15:
        new_food.refresh()
        new_snake.extend()
        new_score.increase()
    
    if new_snake.head.xcor() > 280 or new_snake.head.xcor() < -280 or new_snake.head.ycor() > 280 or new_snake.head.ycor() < -280:
        game_is_on = False
        new_score.game_over()

    for i in new_snake.list_snakes[1:]:
        if new_snake.head.distance(i) < 10:
            game_is_on = False
            new_score.game_over() 

screen.exitonclick()

