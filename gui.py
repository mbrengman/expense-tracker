from tkinter import Label, Tk, Button, Entry, Radiobutton
from tkinter import messagebox, Toplevel, OptionMenu
from tkinter import IntVar, StringVar, Frame
from helper import Warehouse, trace, get_date, date_selection
from datetime import datetime
from dataclasses import dataclass
import getpass
import logging

log = logging.getLogger('__name__')
logging.basicConfig(filename='info.log', level=logging.DEBUG)

@dataclass
class Flow:
    income: str
    debt: str

def elements(base: Warehouse, flow: str):
    number = base.length(flow)
    index = number if number <= 10 else 10
    return base.get_entries(flow)[:index+1]

def end_process():
    answer = messagebox.askyesno('EXPENSE TRACKER', 'Close the program?')
    return answer    

def project(user: str):
    user = getpass.getuser()
    base = Warehouse(user + '.db')
    base.open()
    display = Toplevel()
    Label(display, text='Welcome to the expense tracker').grid(column=1, row=0)
    Label(display, text='INCOME').grid(column=0, row=1)
    Label(display, text='DEBT').grid(column=2, row=1)
    fields = [elements(base, 'income'), elements(base, 'debt')]
    [OptionMenu(display, variable=fields[i], values=fields[i]) for i in fields[0]]
    Label(display, text=fields[0]).grid(column=0, row=len(fields[0])+2)
    Label(display, text=fields[1]).grid(column=2, row=len(fields[1])+2)
    Button(display, text='Delete entry').grid(column=2, row=8)
    graphs: list[tuple[str]] = [
        ('ALL', 0),
        ('DAYS', 1),
        ('WEEKS', 2),
        ('MONTHS', 3)]
    action = IntVar()
    action.set(0)
    [Radiobutton(display,
        text=text,
        command=lambda: \
            show_graph(display, base, action.get())).grid(column=0, row=act+4)\
            for text, act in graphs]
    Label(display, text=action)

def show_graph(display, base, action):
    try:
        flow = Flow('income', 'debt')
        _x_axis = None # Duration of measurement
        income = base.get_entries(flow.income)
        income_list = [item[2] for item in income]
        del income
        debt = base.get_entries(flow.debt)
        debt_list = [item[2] for item in debt]
        del debt
        match action:
            case 0:
                total_income = base.get_total(flow.income)
                total_debt = base.get_total(flow.debt)
                return base.bar_graph(total_income, total_debt)
            case 1:
                return base.line_graph(income_list, debt_list)
            case 2:
                time = get_date()
                current_date = date_selection(time, 30)
                income_date = base.from_date(flow.income, current_date)
                debt_date = base.from_date(flow.debt, current_date)
                return base.line_graph(income_date, debt_date)
            case 3:
                pass
    except Exception as error:
         print(f' {datetime.now()} {error}\n\t{trace()}')

def start():
    try:
        root = Tk()
        Frame(root).grid(column=1, row=0)
        Label(root, text="Welcome to the expense tracker").grid(column=1,row=1)
        username = Entry(root, width=0)
        user = Button(root, text='submit',
            command=lambda: project(username.get()))
        user.grid(column=0, row=2)
        root.mainloop()
    except Exception as error:
        print(f' {datetime.now()} {error}\n\t{trace()}')

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
    


if __name__ == '__main__':
    try:
        start()
    except Exception as error:
        print(f' {datetime.now()} {error}\n\t{trace()}')
