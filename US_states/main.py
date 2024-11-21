from turtle import Screen , Turtle
import pandas as pd

screen = Screen()
screen.setup(725,491)
screen.bgpic(r'YOUR_PIC_FOR_BACKGROUND')
screen.title("US-STATES")

data = pd.read_csv(r'YOUR_CSV_FILE_PATH')
states = data['state'].to_list()
state_axis = list(zip(data['x'],data['y']))

answer = Turtle()
answer.penup()
answer.hideturtle()
answer.pencolor("black")
answer.pensize(2)
answer.speed("normal")

score = 0
game_is_on = True
while game_is_on:
        user_answers = screen.textinput(f"{score}/50 States Correct", "Name a state in US:").title()
        if score == len(states):
                print("You win!!!")
                game_is_on = False
        if user_answers in states:
                score += 1
                state_index = states.index(user_answers)
                answer.goto(state_axis[state_index])
                answer.write(states[state_index],False)
                states.remove(user_answers)
                state_axis.remove(state_axis[state_index])

        if user_answers.lower() == 'stop':
                game_is_on = False
                with open("missed_states","w") as miss:# If you lose will make a file with missed states
                        for missed in states:
                                miss.write(f'{missed}\n')
        answer.goto(0,0)



screen.exitonclick()
