import Questions
from tkinter import *
from quiz_brain import QuizBrain
import time

THEME_COLOR = "#375362"

dict_of_questions = Questions.questions

# Quiz Brain
qs = QuizBrain(dict_of_questions)

def first_window():
    # First Window
    window_f = Tk()
    window_f.title("Sign Up")
    window_f.minsize(300,200)

    # Create Window Labels
    email_label = Label(text="Email")
    email_label.place(x=0,y=50)

    password_label = Label(text="Password")
    password_label.place(x=0,y=80)

    # Entries
    email_entry = Entry()
    email_entry.insert(0,"example@gmail.com")
    email_entry.place(x=70,y=50)

    password_entry = Entry(show="*") 
    password_entry.place(x=70,y=80)

    # Button Function
    def sign_up():
        if len(email_entry.get()) != 0 and len(password_entry.get()) != 0:
            with open("Passwords.txt","a") as file:
                file.write(f"Email : {email_entry.get()} || Password : {password_entry.get()}\n")
                email_entry.delete(0,END)
                password_entry.delete(0,END)


    # Buttons
    signup_button = Button(text="Sign Up",command=sign_up)
    signup_button.place(x=130,y=150)


    window_f.mainloop()
    
def sec_window():

    window = Tk()
    window.title("Quizzler")
    window.minsize(400,500)
    window.config(bg=THEME_COLOR)

    # Canvas Frame
    canvas = Canvas(width=300,height=300,background='white')
    q = qs.display_question() 
    ques_text = canvas.create_text(150,150,text=f"{q}",font=("Ariel",10,"bold"),width=250,fill='black',justify="center")
    canvas.place(x=45,y=60)


    # Button Functionality
    def true():
        if qs.end():
            time.sleep(3)
            window.destroy()
            return
        ans = 'True'
        if ans == qs.check_answer():
            qs.increase_score()        
            qs.next_ques()
            q = qs.display_question() 
            score = qs.score
            canvas.itemconfig(ques_text,text=f'{q}')
            Label.config(score_label,text=f"SCORE: {score}")
        else:
            qs.next_ques()
            q = qs.display_question() 
            canvas.itemconfig(ques_text,text=f'{q}')
        window.update()
        if qs.end():
            time.sleep(3)
            window.destroy()
            return


    def false():
        if qs.end():
            time.sleep(3)
            window.destroy()
            return
        ans = 'False'
        if ans == qs.check_answer():
            qs.increase_score()
            qs.next_ques()
            q = qs.display_question() 
            score = qs.score
            canvas.itemconfig(ques_text,text=f'{q}')
            Label.config(score_label,text=f"SCORE: {score}")
        else:
            qs.next_ques()
            q = qs.display_question() 
            canvas.itemconfig(ques_text,text=f'{q}')
        window.update()
        if qs.end():
            time.sleep(3)
            window.destroy()
            return


    # Label
    score_label = Label(text=f"SCORE: {qs.score}",background=THEME_COLOR,fg="White",font=('Ariel',10,'bold'))
    score_label.place(x=270,y=20)

    # Buttons
    true_pic = PhotoImage(file=r"C:/Users/makka\Desktop/CS/images/true.png")
    true_button = Button(image=true_pic,highlightthickness=0,command=true)
    true_button.place(x=60,y=380)

    false_pic = PhotoImage(file=r"C:/Users/makka\Desktop/CS/images/false.png")
    false_button = Button(image=false_pic,highlightthickness=0,command=false)
    false_button.place(x=230,y=380)


    window.mainloop()
    
first_window()
sec_window()