from game_data import data
import random
from Game_Arts import *

def generate_random_famous():
    """Gets random famous persons from our data list"""
    famous = random.choice(data)
    return famous

def get_famous_score(famous):
    """Return number of followers of the random famous person"""
    return famous["follower_count"]

def show_famous_data(famous1,famous2):
    """Show the famous data from our data list"""
    famous1_name = famous1['name']
    famous1_desc = famous1['description']
    famous1_country = famous1['country']
    print(f"Compare A: {famous1_name}, {famous1_desc}, from {famous1_country}")
    print(vs)
    famous2_name = famous2['name']
    famous2_desc = famous2['description']
    famous2_country = famous2['country']
    print(f"Against B: {famous2_name}, {famous2_desc}, from {famous2_country}")

def check_winner(famous1,famous2,user_guess):
    """Check is user's answer is correct or not"""
    if user_guess.upper() == 'A':
        user_guess = famous1
        if get_famous_score(user_guess) > get_famous_score(famous2):
            return 1
        else:
            return 0
    elif user_guess.upper() == 'B':
        user_guess = famous2
        if get_famous_score(user_guess) > get_famous_score(famous1):
            return 1
        else:
            return 0
    else:
        return 0

def play_game():
    print(logo)
    Flag = True
    score = 0
    fam1 = generate_random_famous() 
    while Flag:

        fam2 = generate_random_famous()

        while fam1 == fam2:
            fam2 = generate_random_famous()
        
        show_famous_data(fam1,fam2)
        
        user_guess = input("Who has more followers? Type 'A' or 'B':" )
        if check_winner(famous1=fam1,famous2=fam2,user_guess=user_guess) != 0:
            score += 1
            print(f"You're right! Current score: {score}")
        else:
            print(f"Sorry, that's wrong. Final score: {score}")
            Flag = False
        fam1 = fam2
        



play_game()
