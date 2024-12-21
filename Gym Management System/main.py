from tkinter import *

THEME_COLOR = "#0F0F0F"

window = Tk()
window.title("Gym Management System")
window.minsize(600,700)
window.config(bg=THEME_COLOR)


def main():

    canvas = Canvas(width=400,height=600,background='#2A2A2A')

    text = canvas.create_text(210,30,text=f"GYM SYSTEM",font=("wide",25,"bold"),width=250,fill='white',justify="center")
    canvas.place(x=95,y=60)

    button_trainer = Button(text="ADD TRAINER",width=17,height=2,font=("wide",10,"bold"),command=add_for_trainer,borderwidth=3)
    button_trainer.place(x=240,y=150)

    button_client = Button(text="ADD CLIENT",width=17,height=2,font=("wide",10,"bold"),command=add_for_client,borderwidth=3)
    button_client.place(x=240,y=220)

    edit_Tbutton = Button(text="EDIT TRAINER",width=17,height=2,font=("wide",10,"bold"),borderwidth=3)
    edit_Tbutton.place(x=240,y=290)

    edit_Cbutton = Button(text="EDIT CLIENT",width=17,height=2,font=("wide",10,"bold"),borderwidth=3)
    edit_Cbutton.place(x=240,y=360)

    del_Tbutton = Button(text="DELETE TRAINER",width=17,height=2,font=("wide",10,"bold"),command=delete,borderwidth=3)
    del_Tbutton.place(x=240,y=430)

    del_Cbutton = Button(text="DELETE CLIENT",width=17,height=2,font=("wide",10,"bold"),command=delete,borderwidth=3)
    del_Cbutton.place(x=240,y=500)
    
    
    window.mainloop()


def add_for_trainer():
    
    canvas = Canvas(width=400,height=600,background='#2A2A2A')
    text = canvas.create_text(210,30,text=f"ADD PAGE",font=("wide",25,"bold"),width=250,fill='white',justify="center")
    canvas.place(x=95,y=60)
    # ID
    id_label = Label(text="ID : ",background="#2A2A2A",foreground="white",font=("wide",15,"bold"),justify="left")
    id_label.place(x=120,y=150)
    
    id_entry = Entry(width=25,borderwidth=3,justify="center")
    id_entry.place(x=250,y=150)
    
    # NAME
    name_label = Label(text="NAME : ",background="#2A2A2A",foreground="white",font=("wide",15,"bold"),justify="left")
    name_label.place(x=120,y=210)
    
    name_entry = Entry(width=25,borderwidth=3,justify="center")
    name_entry.place(x=250,y=210)
    
    #ADDRESS
    address_label = Label(text="ADDRESS : ",background="#2A2A2A",foreground="white",font=("wide",15,"bold"),justify="left")
    address_label.place(x=120,y=270)
    
    name_entry = Entry(width=25,borderwidth=3,justify="center")
    name_entry.place(x=250,y=270)
    
    #PHONE
    phone_label = Label(text="PHONE : ",background="#2A2A2A",foreground="white",font=("wide",15,"bold"),justify="left")
    phone_label.place(x=120,y=330)
    
    phone_entry = Entry(width=25,borderwidth=3,justify="center")
    phone_entry.place(x=250,y=330)
    
    # Create a label frame
    radioGroup = LabelFrame(text = "Select Gender",width=90,height=100,borderwidth=3)
    radioGroup.place(x=280,y=400)

    # Radio variable
    gender = IntVar()

    # Create two radio buttons
    male = Radiobutton( text = "Male", variable = gender, value = 0)
    male.place(x=280,y=420)

    female = Radiobutton( text = "Female", variable = gender, value = 1)
    female.place(x=280,y=450)
    
    Add_Button = Button(text="ADD",font=("wide",15,"bold"),borderwidth=3,justify="center",width=20)
    Add_Button.place(x=180,y=550)
    
    back_button = Button(text="BACK",width=6,height=2,font=("wide",10,"bold"),command=main,borderwidth=3)
    back_button.place(x=20,y=20)
    
    
    window.mainloop()
    
    
def delete():
     
    canvas = Canvas(width=400,height=600,background='#2A2A2A')
    text = canvas.create_text(210,30,text=f"DELETE PAGE",font=("wide",25,"bold"),width=250,fill='white',justify="center")
    canvas.place(x=95,y=60)
    
    # ID
    id_label = Label(text="ID : ",background="#2A2A2A",foreground="white",font=("wide",15,"bold"),justify="left")
    id_label.place(x=120,y=150)
    
    id_entry = Entry(width=25,borderwidth=3,justify="center")
    id_entry.place(x=250,y=155)
    
    Add_Button = Button(text="DELETE",font=("wide",15,"bold"),borderwidth=3,justify="center",width=20)
    Add_Button.place(x=180,y=220)
    
    back_button = Button(text="BACK",width=6,height=2,font=("wide",10,"bold"),command=main,borderwidth=3)
    back_button.place(x=20,y=20)
    
    bye = Label(text="WISH U LUCK!",font=("wide",25,"bold"),background="#2A2A2A",foreground="white")
    bye.place(x=180,y=400)
    
    window.mainloop()
    
def add_for_client():
    
    canvas = Canvas(width=400,height=600,background='#2A2A2A')
    text = canvas.create_text(210,30,text=f"ADD PAGE",font=("wide",25,"bold"),width=250,fill='white',justify="center")
    canvas.place(x=95,y=60)
    # ID
    id_label = Label(text="ID : ",background="#2A2A2A",foreground="white",font=("wide",15,"bold"),justify="left")
    id_label.place(x=120,y=150)
    
    id_entry = Entry(width=25,borderwidth=3,justify="center")
    id_entry.place(x=250,y=150)
    
    # NAME
    name_label = Label(text="NAME : ",background="#2A2A2A",foreground="white",font=("wide",15,"bold"),justify="left")
    name_label.place(x=120,y=210)
    
    name_entry = Entry(width=25,borderwidth=3,justify="center")
    name_entry.place(x=250,y=210)
    
    #ADDRESS
    address_label = Label(text="ADDRESS : ",background="#2A2A2A",foreground="white",font=("wide",15,"bold"),justify="left")
    address_label.place(x=120,y=270)
    
    name_entry = Entry(width=25,borderwidth=3,justify="center")
    name_entry.place(x=250,y=270)
    
    #PHONE
    phone_label = Label(text="PHONE : ",background="#2A2A2A",foreground="white",font=("wide",15,"bold"),justify="left")
    phone_label.place(x=120,y=330)
    
    phone_entry = Entry(width=25,borderwidth=3,justify="center")
    phone_entry.place(x=250,y=330)
    
    # Create Gender RadioGroup
    radioGroup = LabelFrame(text = "Select Gender",width=90,height=100,borderwidth=3)
    radioGroup.place(x=350,y=400)

    # Radio variable
    gender = IntVar()

    # Create two radio buttons
    male = Radiobutton( text = "Male", variable = gender, value = 0)
    male.place(x=350,y=420)

    female = Radiobutton( text = "Female", variable = gender, value = 1)
    female.place(x=350,y=450)
    
    # Create MemberShip RadioGroup
    radioGroup = LabelFrame(text = "Select MemberShip",width=130,height=130,borderwidth=3)
    radioGroup.place(x=150,y=400)

    # Radio variable
    member_id = IntVar()

    # Create two radio buttons
    standard = Radiobutton( text = "Standard", variable = member_id, value = 0)
    standard.place(x=150,y=420)

    gold = Radiobutton( text = "Gold", variable = member_id, value = 1)
    gold.place(x=150,y=440)
    

    elite = Radiobutton( text = "Elite", variable = member_id, value = 2)
    elite.place(x=150,y=460)


    vip = Radiobutton( text = "Vip", variable = member_id, value = 3)
    vip.place(x=150,y=480)


    ultimate = Radiobutton( text = "Ultimate", variable = member_id, value = 4)
    ultimate.place(x=150,y=500)
    
    
    
    Add_Button = Button(text="ADD",font=("wide",15,"bold"),borderwidth=3,justify="center",width=20)
    Add_Button.place(x=180,y=550)
    
    back_button = Button(text="BACK",width=6,height=2,font=("wide",10,"bold"),command=main,borderwidth=3)
    back_button.place(x=20,y=20)
    
    
    window.mainloop()
    
main() 

    
    

    
    
