from tkinter import *
from tkinter import messagebox
import random
import pyperclip

# Create the window
window = Tk()
window.title("Password Manager")
window.minsize(600,600)
window.config(padx=50,pady=50)

# Add the photo
canvas = Canvas(width=200,height=200)
pic = PhotoImage(file=r"C:/Users/makka\Desktop/CS/logo.png")
canvas.create_image(100,100,image=pic)
canvas.place(x=140,y=10)

# Labels
website_label = Label(text="Website:")
website_label.place(x=80,y=205)

email_label = Label(text="Email/Username:")
email_label.place(x=50,y=240)

password_label = Label(text="Password:")
password_label.place(x=70,y=280)

# Entries
web_entry = Entry(width=35)
web_entry.place(x=150,y=205)
web_entry.focus()

email_entry = Entry(width=35)
email_entry.place(x=150,y=240)
email_entry.insert(0, "example@example.com")

password_entry = Entry(width=21) # use show method to show * other than than real password
password_entry.place(x=150,y=280)

# Generate Functionality
def generate():
    """Generate a random password for the user"""
    
    password_entry.delete(0,END)

    letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
    numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    symbols = ['!', '#', '$', '%', '&', '(', ')', '*', '+']

    nr_letters = random.randint(8, 10)
    nr_symbols = random.randint(2, 4)
    nr_numbers = random.randint(2, 4)

    password_list = []

    password_list += [random.choice(letters) for i in range(nr_letters)]
    password_list += [random.choice(numbers) for i in range(nr_numbers)]
    password_list += [random.choice(symbols) for i in range(nr_symbols)]

    random.shuffle(password_list)

    password = ""
    for char in password_list:
        password += char
        
    password_entry.insert(0,password)
    pyperclip.copy(password) # to copy password to the clipboard
    

# Add functionality
def add():
    """Add the website and its email and password in a file to save it"""

    if len(email_entry.get()) == 0 or len(web_entry.get()) == 0 or len(password_entry.get()) == 0:
        messagebox.showwarning(title="oops",message="Please don't leave any fields empty!")
    else:
            yes_no = messagebox.askokcancel(f"{web_entry.get()}",message=f"The email : {email_entry.get()}\nThe password : {password_entry.get()}\nIs it okay to add?")
            if yes_no:
                with open ("password.txt","a") as file:
                    file.write(f"{web_entry.get()} | {email_entry.get()} | {password_entry.get()}\n")
                    web_entry.delete(0,END)
                    password_entry.delete(0,END)


# Buttons
generate_button = Button(text="Generate Password",command=generate)
generate_button.place(x=280,y=280)

add_button = Button(text="Add",command=add)
add_button.place(x=150,y=310)
add_button.config(width=34)


window.mainloop()
