import time
from turtle import Screen
from player import Player
from car_manager import CarManager
from scoreboard_calc import Score


screen = Screen()
screen.setup(600,600)
screen.tracer(0)

user_player = Player()
new_car = CarManager()
score = Score()
score.score()



screen.onkey(user_player.up,"Up")
screen.listen()

game_is_on = True
while game_is_on:
    time.sleep(0.1)
    screen.update()
    new_car.create_car()
    new_car.move()
    
    # Check if collision with car happend
    for car in new_car.list_cars:
        if user_player.distance(car) < 20 or (user_player.xcor() == car.xcor() and user_player.ycor() == car.ycor()) :
            game_is_on = False
            score.game_over()
    
    # Check if the player reach the other side 
    if user_player.check_win() == 1:
        user_player.reset()
        new_car.increase_speed()
        score.update()
    


screen.exitonclick()