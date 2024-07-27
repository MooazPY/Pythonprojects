from game_data import data
import random
from Game_Arts import *

def generate_random_famous():
    """Gets two random famous persons from our data list"""
    for i in range(1):
        famous = data[random.randint(0,len(data) - 1)]
        data.remove(famous)
    return famous

def get_famous_score(famous):
    return famous["follower_count"]

def show_famous_data(famous1,famous2):
    print(f"Compare A: {famous1['name']}, {famous1['description']}, from {famous1['country']}")
    print(vs)
    print(f"Against B: {famous2['name']}, {famous2['description']}, from {famous2['country']}")

def check_winner(famous1,famous2,user_guess):
    if user_guess.upper() == 'A':
        user_guess = famous1
        if get_famous_score(user_guess) > get_famous_score(famous2):
            return 1
        else:
            return 0
    else:
        user_guess = famous2
        if get_famous_score(user_guess) > get_famous_score(famous1):
            return 1
        else:
            return 0

def play_game():
    print(logo)
    Flag = True
    score = 0
    fam1 = generate_random_famous() 
    while Flag:
        #Get the 2 generated famous persons from the data list
        # fam1,fam2 = generate_random_famous() 
        fam2 = generate_random_famous()
        
        #Get thier score
        # fam1_score = get_famous_score(fam1)
        # fam2_score = get_famous_score(fam2)
        
        show_famous_data(fam1,fam2)
        
        user_guess = input("Who has more followers? Type 'A' or 'B':" )
        if check_winner(famous1=fam1,famous2=fam2,user_guess=user_guess) != 0:
            score += 1
            print(f"You're right! Current score: {score}")
        else:
            print(f"Sorry, that's wrong. Final score: {score}")
            Flag = False
        
        



play_game()