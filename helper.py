from datetime import datetime
import pandas as pd
import logging
import sqlite3
import os
import sys
import traceback
    
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
                raise('INVALID ENTRY\n\tPlease use .db or omit extension')
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
            log.critical(f' {datetime.now()} {error}\n\t{trace()}')

    def open(self):
        statements = ['''CREATE TABLE IF NOT EXISTS debt (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item TEXT NOT NULL,
                date TEXT NOT NULL,
                amount REAL);''',

                '''CREATE TABLE IF NOT EXISTS income (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item TEXT NOT NULL,
                date TEXT NOT NULL,
                amount REAL);'''
            ]
        if ':memory:' == self.location or not os.path.exists(self.location):
            self.data = sqlite3.connect(self.location)
            self.database = self.data.cursor()
        else:
            self.data = sqlite3.connect(self.location)
            self.database = self.data.cursor()
        [self.database.execute(statement) for statement in statements]
        self.data.commit()
        try:
            assert self.data is not None
            assert self.database is not None
        except Exception as error:
            print(f' {datetime.now()} {error}\n\t{trace()}')

    def length(self, pay_type: str) -> int:
        try:
            if 'income' == pay_type:
                self.database.execute('SELECT * FROM income')
            if 'debt' == pay_type:
                self.database.execute('SELECT * FROM debt')
            return len(self.database.fetchall())
        except Exception as error:
            log.error(f' {datetime.now()} {error}\n\t{trace()}')

    def present(self, pay_type: str):
        if '' == pay_type:
            print('income or debt specificity is required')
            return
        if 'income' == pay_type:
            return pd.read_sql_query('SELECT * FROM income', self.data)
        if 'debt' == pay_type:
            return pd.read_sql_query('SELECT * FROM debt', self.data)

    def difference(self) -> float:
        try:
            return self.get_total('income') - self.get_total('debt')
        except Exception as error:
            log.error(f' {datetime.now()} {error}\n\t{trace()}')

    def get_entry(self,
            pay_type: str,
            item: str,
            amount: float = None,
            date = None):
        try:
            df = self.present()
            if date is None:
                return df[amount == df['amount']]
            if amount is None:
                return df[date == df['date']]
            if amount is not None and date is not None:
                return df[date == df['date'] & amount == df['amount']]
        except Exception as error:
            print(f' {datetime.now()} {error}\n\t{trace()}')
    
    def get_entries(self, pay_type: str) -> list:
        try:
            if 'income' == pay_type:
                self.database.execute("SELECT * FROM income")
            if 'debt' == pay_type:
                self.database.execute("SELECT * FROM debt")
            return self.database.fetchall()
        except Exception as error:
            log.error(f' {datetime.now()} {error}\n\t{trace()}')

    def get_total(self, pay_type: str = None) -> sqlite3.Cursor:
        output: float = 0.0
        try:
            if 'income' == pay_type:
                self.database.execute('SELECT amount FROM income')
            elif 'debt' == pay_type:
                self.database.execute('SELECT amount FROM debt')
            totals = self.database.fetchall()
            for total in totals:
                output += total[0]
            return output
        except Exception as error:
            log.error(f' {datetime.now()} {error}\n\t{trace()}')

    def get_average(self, pay_type: str) -> float:
        output: float = 0.0
        try:
            if 'debt' == pay_type:
                self.database.execute('SELECT amount FROM debt')
            elif 'income' == pay_type:
                self.database.execute('SELECT amount FROM income')
            elements: int = self.database.fetchall()
            for total in elements:
                output += total[0]
            return output / len(elements)
        except Exception as error:
            print(f' {datetime.now()} {error}\n\t{trace()}')

    def add_item(self, new_item: str, pay_type: str, amount: float):
        date = get_date()
        try:
            with self.data:
                if 'income' == pay_type:
                    self.database.execute('''
                        INSERT INTO income (item, date, amount) VALUES (?,?,?)''',
                            (new_item, date, amount)
                        )
                if 'debt' == pay_type:
                    self.database.execute('''
                        INSERT INTO debt (item, date, amount) VALUES (?,?,?)''',
                            (new_item, date, amount)
                        )
                self.data.commit()
        except Exception as error:
            log.error(f' {datetime.now()} {error}\n\t{trace()}')

    def get_items(self, pay_type: str):
        if '' == pay_type:
            print('income or debt specificity is required')
            return
        output = []
        try:
            if pay_type == 'income':
                self.database.execute("SELECT * FROM income")
                rows = self.database.fetchall()
                for row in rows:
                    output.append(row)
            if pay_type == 'debt':
                self.database.execute("SELECT * FROM debt")
                rows = self.database.fetchall()
                for row in rows:
                    output.append(row)
        except Exception as error:
            print(f' {datetime.now()} {error}\n\t{trace()}')
        finally:
            return output

    def remove_item(self, pay_type: str, pointer: int):
        try:
            with self.data:
                if 'income' == pay_type:
                    self.database.execute('DELETE FROM income WHERE id = ?', (pointer,))
                if 'debt' == pay_type:
                    self.database.execute('DELETE FROM debt WHERE id = ?', (pointer,))
                self.data.commit()
        except Exception as error:
            print(f' {datetime.now()} {error}\n\t{trace()}')

    def remove(self, pay_type: str, item: int, amount: float):
        try:
            with self.data:
                print(f'number of {pay_type} records before cleaning is {self.length(pay_type)}')
                if 'income' == pay_type:
                    self.database.execute('''
                        DELETE FROM income WHERE item = ? AND amount = ?''',
                    (item, amount))
                if 'debt' == pay_type:
                    self.database.execute('''
                        DELETE FROM debt WHERE item = ? AND amount = ?''',
                    (item, amount))
                print(f'number of {pay_type} records after cleaning is {self.length(pay_type)}')
        except Exception as error:
            print(f' {datetime.now()} {error}\n\t{trace()}')

    def remove_items(self, pay_type: str, item: str):
        try:
            with self.data:
                if 'income' == pay_type:
                    self.database.execute('DELETE FROM income WHERE item = ?',
                        (item,))
                if 'debt' == pay_type:
                    self.database.execute('DELETE FROM debt WHERE item = ?',
                        (item,))
                self.data.commit()
        except Exception as error:
            print(f' {datetime.now()} {error}\n\t{trace()}')

    def remove_all(self, pay_type: str):
        try:
            with self.data:
                if 'income' == pay_type:
                    self.database.execute('DELETE FROM income')
                if 'debt' == pay_type:
                    self.database.execute('DELETE FROM debt')
                self.data.commit()
        except Exception as error:
            print(f' {datetime.now()} {error}\n\t{trace()}')
            
def get_date():
    now = str(datetime.now())
    now = now.split()
    return str(now[0])    

def trace():
    error, value, line = sys.exc_info()
    lines = traceback.format_exception(error, value, line)
    return '\n'.join(lines)

log = logging.getLogger(__name__)
logging.basicConfig(filename='info.log', level=logging.DEBUG)

# house = Warehouse()
# house.open()
# house.add_item('income', 'something', 12.0)
# house.add_item('income', 'something else', 2.0)
# print(house.get_total('income'))
