from turtle import Screen
from paddle import Paddle
from ball import Ball
from ScoreBoard import Scoreboard
import time

screen = Screen()
screen.setup(800,600)
screen.bgcolor("black")
screen.title("Pong Game")
screen.tracer(0)


l_paddle = Paddle((-350,0))
r_paddle = Paddle((350,0))
ball = Ball()
Score = Scoreboard()
Score.write_score()
Score.draw_net()


screen.onkey(l_paddle.up,"w")
screen.onkey(l_paddle.down,"s")
screen.onkey(r_paddle.up,"Up")
screen.onkey(r_paddle.down,"Down")
screen.listen()
timer = 0.1
game_is_on = True
while game_is_on:
    time.sleep(timer)
    screen.update()
    ball.move()
    if ball.ycor() > 280 or ball.ycor() < -280:
        ball.bounce_y()
        timer*= 0.9

    elif ball.distance(r_paddle) < 50 and ball.xcor() >= 330 or ball.distance(l_paddle) < 50 and ball.xcor() <= -330:
        ball.bounce_x()
        timer*= 0.9

    elif ball.xcor() > 380:
        Score.increase_lscore()
        ball.reset()
        timer = 0.1
    elif  ball.xcor() < -380:
        Score.increase_rscore()
        ball.reset()
        timer = 0.1    

screen.exitonclick()
