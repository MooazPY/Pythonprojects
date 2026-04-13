from art import logo

print(logo)

alphabet = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
# Take inputs from user
direction = input("Type 'encode' to enctypt, type 'decode' to decrypt:\n")
text = input("Type your message:\n").lower()
shift = int(input("Type the shift number:\n"))

def caesar(start_text,shift_amount,cipher_direction):
    # Encrypt side
    end_text = ""
    for letter in start_text:
        if letter not in alphabet:
            end_text += letter
            continue
        current_position =  alphabet.index(letter)
        if direction.lower() == "decode":
            if shift_amount > 0:
                shift_amount *= -1
        new_position = (current_position + shift_amount) % len(alphabet)
        end_text += alphabet[new_position]
    print(f"Here's the {cipher_direction}d result: {end_text}.\n")

while True:
    caesar(start_text=text,shift_amount=shift,cipher_direction=direction)
    user_answer = input("Want to restart the cipher program?\nType 'yes' if you want to go again. Otherwise type 'no'. ")
    if user_answer.lower() != "yes":
        print("Good bye")
        break
    direction = input("Type 'encode' to enctypt, type 'decode' to decrypt:\n")
    text = input("Type your message:\n").lower()
    shift = int(input("Type the shift number:\n"))
