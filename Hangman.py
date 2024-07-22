import random as rn
from arts import *
from words import word_list

print(logo)

used_letters = []

no_of_guesses = 6

display = []

chosen_word = rn.choice(word_list) # To pick a random element from list

# print(f"The chosen word is {chosen_word} ")

for i in range(len(chosen_word)): # Create a blank list "_" 
    display.append("_")

while "_" in display and no_of_guesses >= 0:
    guess = input("guess a letter : ").lower()

    if guess in chosen_word and guess not in display:
        for i in range(len(chosen_word)): # Swap blanks with letters
            if guess == chosen_word[i]:
                display[i] = guess
        for i in range (len(display)):
            print(display[i],end=" ")
        print("\n")
    elif guess in display or guess in used_letters:
        print(f"letter {guess} is already guessed")
    else:
        used_letters.append(guess)
        print(f"You guessed {guess}, that's not in the word, you lose a life.")
        print(stages[no_of_guesses])
        no_of_guesses -=1

if no_of_guesses >= 0:
    print("You won!!!")
else:
    print("You Lost")
    print(f"The word was {chosen_word}")