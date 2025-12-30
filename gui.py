from tkinter import Label, Tk, Button, Entry, Radiobutton
from tkinter import messagebox, Toplevel, OptionMenu
from tkinter import IntVar, StringVar, Frame
from helper import Warehouse, trace, get_date, date_selection
from dataclasses import dataclass
import getpass
import asyncio
import threading
import tracemalloc
import logging

tracemalloc.start()
log = logging.getLogger('__name__')
logging.basicConfig(filename='info.log', level=logging.DEBUG)

@dataclass
class Flow:
    income: str
    debt: str

def elements(warehouse: Warehouse, flow: str) -> list:
    number: int = asyncio.run(warehouse.length(flow))
    if number is not None:
        index: int = number if number <= 10 else 10
    else:
        print('number variable is currently None')
        return
    try:
        out = asyncio.run(warehouse.get_entries(flow))
        return out[:index+1]
    except Exception as error:
        print(trace(error))

def end_process(root):
    try:
        answer: int = messagebox.askyesno('EXPENSE TRACKER', 'Close the program?')
        if answer == 1:
            root.destroy()
        else:
            return
    except Exception as error:
        print(trace(error))

def add_entry(user: Warehouse, flow:str, title:str, amount:str):
    def run_async():
        async def add_coroutine(flow:str, title:str, amount:str):
            await user.add_item(flow, title, amount)
        asyncio.run(add_coroutine(flow, title, amount))
    threading.Thread(target=run_async, daemon=True).start()

def project(dropdown: IntVar, user: Warehouse):
    labels: list[str] = ['Item', 'Type', 'Amount']
    try:
        user.open()
        income = elements(user, 'income')
        debt = elements(user, 'debt')
        fields: list = [income, debt]
        display: Tk = Toplevel()
        # Label(display, text='INCOME').grid(column=0, row=1)
        # Label(display, text='DEBT').grid(column=2, row=2)
        # [OptionMenu(display, variable=fields[i], values=fields[i]).grid(column=1, row=3)
        #     for i in fields[0]]
        Label(display, text=fields[0]).grid(column=0, row=len(fields[0])+2)
        Label(display, text=fields[1]).grid(column=2, row=len(fields[1])+2)
        match dropdown:
            case 0:
                Label(display, text = labels[0]).grid(column=0, row=0)
                Label(display, text=labels[1]).grid(column=0, row=1)
                Label(display, text=labels[2]).grid(column=0, row=2)
                title: Entry = Entry(display, width = 50)
                flow: Entry = Entry(display, width=50)
                amount: Entry = Entry(display, width=50)
                submit: Button = Button(display, text='submit', command=
                    lambda: add_entry(user, str(flow.get()), str(title.get()), str(amount.get())))
                end: Tk = Button(display, text='End program', command=display.destroy)

                title.grid(column=2, row=0)
                flow.grid(column=2, row=1)
                amount.grid(column=2, row=2)
                end.grid(column=3, row=1)
                submit.grid(column=3, row=2)
            case 1:
                title: Entry = Entry(display, width=50)
                flow: Entry = Entry(display, width=50)
                amount: Entry = Entry(display, width=50)
                submit: Button = Button(display, text='submit', command=
                    lambda: user.remove(flow, title, amount))
                end: Tk = Button(display, text='End program', command=display.destroy)

                title.grid(column=1, row=1)
                flow.grid(column=1, row=2)
                amount.grid(column=1, row=3)
                end.grid(column=2, row=5)
                submit.grid(column=2, row=4)
            case 2:
                end: Tk = Button(display, text='End program', command=display.destroy)
                end.grid(column=2, row=8)
                graphs: list[tuple[str]] = [
                    ('ALL', 0),
                    ('DAYS', 1),
                    ('WEEKS', 2),
                    ('MONTHS', 3)
                ]
                action: IntVar = IntVar()
                action.set(0)
                [Radiobutton(display,
                    text=text,
                    command=lambda: \
                        show_graph(display, user, action.get())).grid(column=0, row=act+4)\
                        for text, act in graphs]
                Label(display, text=action)
    except Exception as error:
        print(trace(error))

def show_graph(display, base, action):
    try:
        flow: Flow = Flow('income', 'debt')
        _x_axis = None # Duration of measurement
        income: list[Warehouse] = base.get_entries(flow.income)
        income_list: list = [item[2] for item in income]
        del income
        debt: list[Warehouse] = base.get_entries(flow.debt)
        debt_list: list = [item[2] for item in debt]
        del debt
        match action:
            case 0:
                total_income: float = base.get_total(flow.income)
                total_debt: float = base.get_total(flow.debt)
                return base.bar_graph(total_income, total_debt)
            case 1:
                return base.line_graph(income_list, debt_list)
            case 2:
                time: str = get_date()
                current_date: str = date_selection(time, 30)
                income_date: list[Warehouse] = base.from_date(flow.income, current_date)
                debt_date: list[Warehouse] = base.from_date(flow.debt, current_date)
                return base.line_graph(income_date, debt_date)
            case 3:
                pass
    except Exception as error:
        print(trace(error))

def start():
    user: str = getpass.getuser()
    greet: str = f'Welcome to the expense tracker {user}\t'
    base: Warehouse = Warehouse(user + '.db')
    del user
    options: list[str] = [
        ('ADD ENTRY', 0),
        ('REMOVE ENTRY', 1),
        ('VIEW CHARTS', 2)
    ]
    labels = ['Item', 'Type', 'Amount']
    try:
        root: Tk = Tk()
        Frame(root).grid(column=1, row=0)
        Label(root, text=greet).grid(column=1,row=0)
        choice = IntVar()
        choice.set(0)
        Label(root, text = labels[0]).grid(column=0, row=2)
        Label(root, text=labels[1]).grid(column=0, row=1)
        Label(root, text=labels[2]).grid(column=0, row=2)
        # [Label(root, text=labels[i]).grid(column=0, row=j+2) for i, j in labels]
        [Radiobutton(root, text=text, variable=choice,\
            value=option).grid(column=1,row=option+2)\
                for text, option in options]
        user = Button(root, text='Take action',
            command=lambda: project(choice.get(), base))
        end = Button(root, text="close program", command=lambda: end_process(root))

        user.grid(column=2, row=5)
        end.grid(column=3, row=5)
        
        root.mainloop()
    except Exception as error:
        print(trace(error))

def decision(dropdown: Tk, base: Warehouse):
    _action = dropdown.get()

def delete(base, item: str, amount: float):
    types: list[str] = ['income', 'debt']
    try:
        action: Tk = Toplevel()
        pay_type: StringVar = StringVar()
        OptionMenu(action, pay_type, types).grid(column=0, row=0)
        item: StringVar = Entry()
        base.remove(pay_type, item, amount)
    except Exception as error:
        print(trace(error))


if __name__ == '__main__':
    snapshot = tracemalloc.take_snapshot()
    try:
        start()
    except Exception as error:
        print(trace(error))
