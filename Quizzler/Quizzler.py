import Questions
from tkinter import *
from quiz_brain import QuizBrain
import time

THEME_COLOR = "#375362"

dict_of_questions = Questions.questions

# Quiz Brain
qs = QuizBrain(dict_of_questions)

# UI 
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
score_label = Label(text=f"Score: {qs.score}",background=THEME_COLOR,fg="White",font=('Ariel',10,'bold'))
score_label.place(x=270,y=20)

# Buttons
true_pic = PhotoImage(file=r"C:/Users/makka\Desktop/CS/images/true.png")
true_button = Button(image=true_pic,highlightthickness=0,command=true)
true_button.place(x=60,y=380)

false_pic = PhotoImage(file=r"C:/Users/makka\Desktop/CS/images/false.png")
false_button = Button(image=false_pic,highlightthickness=0,command=false)
false_button.place(x=230,y=380)


window.mainloop()
