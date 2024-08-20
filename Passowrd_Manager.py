from tkinter import *
from tkinter import messagebox
import random
import json

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

password_entry = Entry(width=21) # To show * except the password use show method
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


# Add functionality
def add():
    """Add the website and its email and password in a file to save it"""
    new_data = {
        web_entry.get():{
            "email":email_entry.get(),
            "password":password_entry.get(),
        }
    }
    
    
    if len(email_entry.get()) == 0 or len(web_entry.get()) == 0 or len(password_entry.get()) == 0:
        messagebox.showwarning(title="oops",message="Please don't leave any fields empty!")
    else:
        try:
            with open ("pass.json","r") as file:
                data = json.load(file)
        except FileNotFoundError:
            with open("pass.json","w") as file:
                json.dump(new_data,file,indent=4)
        else:
            data.update(new_data)
            with open("pass.json","w") as file:
                json.dump(data,file,indent=4)
            web_entry.delete(0,END)
            password_entry.delete(0,END)

# Search Functionality
def search():
    """Search if the specific website is in JSON file or not"""
    with open("pass.json") as file:
        data = json.load(file)
        mails = [mail for mail in data]

    if web_entry.get() in mails:
        with open("pass.json","r") as file:
            data = json.load(file)
            password_get = data[web_entry.get()]["password"]
            mail_get = data[web_entry.get()]["email"]
        messagebox.showinfo(f"{web_entry.get()}",message=f"Email: {mail_get}\nPassword: {password_get}")
    else:
        messagebox.showerror(f"{web_entry.get()} Not Found",message=f"There is no website called {web_entry.get()} in file")


# Buttons
generate_button = Button(text="Generate Password",command=generate)
generate_button.place(x=280,y=280)

add_button = Button(text="Add",command=add)
add_button.place(x=150,y=310)
add_button.config(width=34)

search_button = Button(text="Search",width=10,command=search)
search_button.place(x=370,y=205)


window.mainloop()
