from tkinter import Label, Tk, Frame, Button, Entry
from tkinter import messagebox, Toplevel, OptionMenu, StringVar
from helper import Warehouse, trace
from datetime import datetime
import logging

log = logging.getLogger('__name__')
logging.basicConfig(filename='info.log', level=logging.DEBUG)

def item():
    return Label(frame, text= frame.get())

def end_process():
    answer = messagebox.askyesno('EXPENSE TRACKER', 'Close the program?')
    return answer    

def project(user: str):
    try:
        assert not user.isdigit()
        assert not user[0].isdigit()
    except Exception as error:
        print(f' {datetime.now()} {error}\n\t{trace()}')
    base = Warehouse(user)
    base.open()
    project = Toplevel()
    Label(project, text='Welcome to the expense tracker').grid(column=1, row=0)
    Label(project, text='INCOME').grid(column=0, row=1)
    Label(project, text='DEBT').grid(column=2, row=1)
    Label(project, text=base.present('income')).grid(column=0, row=2)
    Label(project, text=base.present('debt')).grid(column=2, row=2)
    Button(project, text='Delete entry')

def delete(base, item: str, amount: float):
    types = ['income', 'debt']
    try:
        action = Toplevel()
        pay_type = StringVar()
        OptionMenu(action, pay_type, types).grid(column=0, row=0)
        item = Entry()
        base.remove(pay_type, item, amount)
    except Exception as error:
        print(f' {datetime.now()} {error}\n\t{trace()}')
    



try:
    exp = 'expenses.db'
    # base = Warehouse('expenses.db')
    # base.open()
    root = Tk()
    frame = Frame(root)
    frame.grid()
    top = Toplevel()
    intro = Label(top, text='Welcome to the expense tracker').grid(column=0, row=0)
    submit_button = Button(intro, text='submit', command=lambda: project(exp)).grid(column=0, row=3)
    answer = Button(frame, text='Exit', command=end_process).grid(column=10, row=10)
    if 1 == answer:
        exit
    Label(frame, text="Welcome to the expense tracker!!").grid(column=1, row=1)
    Label(frame, text="Enter item").grid(column=3, row=3)
    Entry(frame, width=50).grid(column=3, row=4)
    Label(frame, text="Enter amount").grid(column=4, row=3)
    Entry(frame, width=25).grid(column=4, row=4)
    # clicked = None
    # amount = None
    # item, amount, clicked = (str(item), str(amount), str(clicked))
    # OptionMenu(frame, clicked, 'PAYMENT TYPE', 'debt', 'income').grid(column=3, row=8)
    Button(frame, text='Submit', command=item).grid(column=8, row=10)
    root.mainloop()
except Exception as error:
    print(f' {datetime.now()} {error}\n\t{trace()}')

# if __name__ == '__main__':
#     root.mainloop()
