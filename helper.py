from datetime import datetime
from dataclasses import dataclass
import pandas as pd
from PIL import Image
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import logging
import sqlite3
import os
import io
import asyncio
import sys
import tracemalloc
import traceback
import calendar


tracemalloc.start()
class Warehouse:
    def __init__(self, location = None):
        if location is None:
            self.location = 'tracker.db'
        elif ':memory:' == location:
            self.location = location
        else:
            ext = '.db'
            if location.endswith(ext):
                self.location = location
            elif -1 == location.find(ext[:1]) and location.find('.'):
                log.error(f' {datetime.now()}\n\tentry contains invalid extension')
                print('INVALID ENTRY\n\tPlease use .db or omit extension')
                import sys
                sys.exit()
            else:
                self.location = location + ext
        self.data = None
        self.database = None

    def __del__(self):
        try:
            if self.data:
                self.data.close()
        except Exception as error:
            print(trace(error))

    def open(self):
        statements = ['''CREATE TABLE IF NOT EXISTS debt (
                item TEXT NOT NULL,
                date TEXT NOT NULL,
                amount REAL);''',

                '''CREATE TABLE IF NOT EXISTS income (
                item TEXT NOT NULL,
                date TEXT NOT NULL,
                amount REAL);'''
            ]
        if ':memory:' == self.location or not os.path.exists(self.location):
            conn = sqlite3.connect(self.location)
            curr = conn.cursor()
        else:
            conn = sqlite3.connect(self.location)
            curr = conn.cursor()
        [curr.execute(statement) for statement in statements]
        conn.commit()
        try:
            assert conn is not None
            assert curr is not None
        except Exception as error:
            print(trace(error))
        finally:
            curr.close()
            conn.close()

    async def length(self, pay_type: str) -> int:
        try:
            if not is_valid_pay(pay_type):
                return 0
            text = f'SELECT * FROM {pay_type}'
            loop = asyncio.get_running_loop()
            def fetch_length():
                conn = sqlite3.connect(self.location)
                curr = conn.cursor()
                try:
                    curr.execute(text)
                    return len(curr.fetchall())
                except Exception as error:
                    trace(error)
                finally:
                    curr.close()
                    conn.close()
            return await loop.run_in_executor(None, fetch_length)
        except Exception as error:
            print(trace(error))

    async def present(self, pay_type: str):
        if not is_valid_pay(pay_type):
            return
        text = f'SELECT * FROM {pay_type}'
        loop = asyncio.get_running_loop()
        def read_df():
            conn = sqlite3.connect(self.location)
            curr = conn.cursor()
            try:
                return pd.read_sql_query(text, curr)
            except Exception as error:
                print(trace(error))
            finally:
                curr.close()
                conn.close()
        try:
            return await loop.run_in_executor(None, read_df)
        except Exception as error:
            print(trace(error))

    async def line_graph(self, x_axis: list, y_axis: list) -> Image:
        loop = asyncio.get_running_loop()
        def create_graph():
            plt.plot(x_axis, y_axis)
            buf = io.BytesIO()
            plt.savefig('line.png')
            buf.seek(0)
            image = Image.open(buf)
            return image
        try:
            return await loop.run_in_executor(None, create_graph)
        except Exception as error:
            print(trace(error))

    async def bar_graph(self, x_axis: list, y_axis: list) -> Image:
        loop = asyncio.get_running_loop()
        def create_graph():
            plt.bar(x_axis, y_axis)
            buf = io.BytesIO()
            plt.savefig('bar.png')
            buf.seek(0)
            image = Image.open(buf)
            return image
        try:
            return await loop.run_in_executor(None, create_graph)
        except Exception as error:
            print(trace(error))

    async def difference(self) -> float:
        try:
            income = await self.get_total('income')
            debt = await self.get_total('debt')
            return income - debt
        except Exception as error:
            print(trace(error))

    async def get_entry(self, pay_type: str, item: str, amount: str = None, date = None):
        if not is_valid_pay(pay_type, amount):
            return
        output = None
        amount = float(amount)
        try:
            df = await self.present(pay_type)
            if amount is not None and date is not None:
                return df[date == df['date'] & amount == df['amount']]
            if date is not None:
                output = df['date'] == date
            if amount is not None:
                output = df['amount'] == amount
            if output is not None:
                return output.loc[output]
        except Exception as error:
            print(trace(error))
    
    async def get_entries(self, pay_type: str) -> list:
        if not is_valid_pay(pay_type):
            return
        text = f'SELECT * FROM {pay_type}'
        loop = asyncio.get_running_loop()
        def fetch_entries():
            conn = sqlite3.connect(self.location)
            curr = conn.execute(text)
            try:
                return curr.fetchall()
            except Exception as error:
                trace(error)
            finally:
                curr.close()
                conn.close()
        return await loop.run_in_executor(None, fetch_entries)

    async def get_total(self, pay_type: str = None) -> sqlite3.Cursor:
        if not is_valid_pay(pay_type):
            return
        text = f'SELECT amount FROM {pay_type}'
        loop = asyncio.get_running_loop()
        def compute_total():
            conn = sqlite3.connect(self.location)
            curr = conn.cursor()
            try:
                curr.execute(text)
                totals = curr.fetchall()
                return sum(total[0] for total in totals)
            except Exception as error:
                trace(error)
            finally:
                curr.close()
                conn.close()
        return await loop.run_in_executor(None, compute_total)

    async def get_average(self, pay_type: str) -> float:
        if not is_valid_pay(pay_type):
            return
        text = f'SELECT amount FROM {pay_type}'
        loop = asyncio.get_running_loop()
        def compute_average():
            conn = sqlite3.connect(self.location)
            curr = conn.cursor()
            try:
                curr.execute(text)
                totals = curr.fetchall()
                if not totals:
                    return 0.0
                output = sum(total[0] for total in totals)
                return output / len(totals)
            except Exception as error:
                trace(error)
            finally:
                curr.close()
                conn.close()
        return await loop.run_in_executor(None, compute_average)

    async def add_item(self, pay_type: str, new_item: str, amount: float):
        if not is_valid_pay(pay_type):
            return
        date = get_date()
        amount = float(amount)
        text = f'INSERT INTO {pay_type} VALUES (?,?,?)'
        loop = asyncio.get_running_loop()
        def add():
            conn = sqlite3.connect(self.location)
            curr = conn.cursor()
            try:
                curr.execute(text, (new_item, date, amount))
                conn.commit()
            except Exception as error:
                trace(error)
            finally:
                curr.close()
                conn.close()
        try:
            await loop.run_in_executor(None, add)
        except Exception as error:
            print(trace(error))

    async def from_date(self, pay_type: str, date: str = None):
        if not is_valid_pay(pay_type):
            return
        text = f'SELECT * FROM {pay_type} WHERE date >= ?'
        conn = sqlite3.connect(self.location)
        curr = conn.cursor()
        try:
            date = get_date() if date is None else date
            curr.execute(text, (date,))
            return curr.fetchall()
        except Exception as error:
            print(trace(error))
        finally:
            curr.close()
            conn.close()

    async def get_items(self, pay_type: str):
        if not is_valid_pay(pay_type):
            return
        text = f'SELECT * FROM {pay_type}'
        loop = asyncio.get_running_loop()
        def fetch_items():
            conn = sqlite3.connect(self.location)
            curr = conn.cursor()
            try:
                curr.execute(text)
                rows = curr.fetchall()
                return [row for row in rows]
            except Exception as error:
                trace(error)
            finally:
                curr.close()
                conn.close()
        return await loop.run_in_executor(None, fetch_items)

    def return_dates(self, days: int):
        try:
            output: list[str] = []
            date: str = get_date()
            for i in range(days):
                output.append(date_selection(date, days))
            return output
        except Exception as error:
            print(trace(error))

    async def remove(self, pay_type: str, item: str, amount: float):
        if not is_valid_pay(pay_type) or isinstance(amount, float):
            return
        amount = float(amount)
        text = f'DELETE FROM {pay_type} WHERE item = ? AND amount = ?'
        loop = asyncio.get_running_loop()
        def remove_entry():
            print(f'number of {pay_type} records before cleaning is {self.length(pay_type)}')
            conn = sqlite3.connect(self.location)
            curr = conn.cursor()
            try:
                curr.execute(text, (item, amount))
                conn.commit()
            except Exception as error:
                trace(error)
            finally:
                curr.close()
                conn.close()
            print(f'number of {pay_type} records after cleaning is {self.length(pay_type)}')
        await loop.run_in_executor(None, remove_entry)

    async def remove_items(self, pay_type: str, item: str):
        if not is_valid_pay(pay_type):
            return
        text = f'DELETE FROM {pay_type} WHERE item = ?'
        print(f'REMOVING {item} FROM {pay_type}')
        loop = asyncio.get_running_loop()
        def remove_entry():
            conn = sqlite3.connect(self.location)
            curr = conn.cursor()
            try:
                curr.execute(text, (item,))
                conn.commit()
            except Exception as error:
                trace(error)
            finally:
                curr.close()
                conn.close()
        await loop.run_in_executor(None, remove_entry)

    async def remove_all(self, pay_type: str):
        if not is_valid_pay(pay_type):
            return
        text = f'DELETE FROM {pay_type}'
        loop = asyncio.get_running_loop()
        def remove_entries():
            conn = sqlite3.connect(self.location)
            curr = conn.cursor()
            try:
                curr.execute(text)
                conn.commit()
            except Exception as error:
                trace(error)
            finally:
                curr.close()
                conn.close()
        await loop.run_in_executor(None, remove_entries)


@dataclass
class Date:
    year: int
    month: int
    day: int
            
def is_valid_pay(pay_type: str, amount: str=None):
    if '' == pay_type:
        print('income or debt specificity is required')
        return False
    if amount is not None:
        if amount.rfind('.') == -1:
            return False
        if amount.isalpha():
            return False
    return True

def get_date():
    now = str(datetime.now())
    now = now.split()
    return str(now[0])    

def date_selection(current: str, num_days: int):
    current = current.split('-')
    hold = [int(d) for d in current]
    date = Date(hold[0], hold[1], hold[2])
    while True:
        if 0 == num_days:
            return f'{str(date.year)}-{str(date.month)}-{str(date.day)}'
        if date.day == 1:
            if 1 == date.month:
                date.month = 12
                date.year -= 1
            date.day = calendar._monthlen(date.year, date.month)
            date.month -= 1
        num_days -= 1

def trace(e: str):
    error, value, line = sys.exc_info()
    lines = traceback.format_exception(error, value, line)
    problem = '\n'.join(lines)
    now: datetime = datetime.now()
    output: str = f'{now} {e}\n\t{problem}\n\nMEMORY ALLOCATIONS'
    snapshot = tracemalloc.take_snapshot()
    stats = snapshot.statistics('lineno')
    return output + '\n\n' + '\n'.join([str(stat) for stat in stats])

log = logging.getLogger(__name__)
logging.basicConfig(filename='info.log', level=logging.DEBUG)
