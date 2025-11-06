from helper import Warehouse, trace
from datetime import datetime
from dataclasses import dataclass
import logging

fill = ['income', 'debt', 'first', 'second', 'third']
log = logging.getLogger(__name__)
logging.basicConfig(filename='info.log', level=logging.DEBUG)

@dataclass
class Item:
    title: str
    amount: float

@dataclass
class Flow:
    income: str
    debt: str

def db_test():
    start = datetime.now()
    flow = Flow('income', 'debt')
    in1 = Item('shoes', 2.0)
    in2 = Item('shirt', 1.0)
    in3 = Item('pants', 3.0)
    out1 = Item('agent', 1.0)
    out2 = Item('vacation', 2.0)
    out3 = Item('food', 3.0)
    out4 = Item('car', 4.0)
    incomes = [in1, in2, in3]
    debts = [out1, out2, out3, out4]
    warehouse = Warehouse(':memory:')
    warehouse.open()
    try:
        assert 0 == warehouse.length(flow.income)
        assert 0 == warehouse.length(flow.debt)
    except AssertionError as e:
        print(f' {datetime.now()} {e}\n\t{trace()}')
    [warehouse.add_item(flow.income, income.title, income.amount) for income in incomes]
    [warehouse.add_item(flow.debt, debt.title, debt.amount) for debt in debts]
    del incomes
    del debts
    try:
        assert 3 == warehouse.length(flow.income)
        assert 4 == warehouse.length(flow.debt)
        assert 6.0 == warehouse.get_total(flow.income)
        assert 10.0 == warehouse.get_total(flow.debt)
        assert -4.0 == warehouse.difference()
        assert 2.0 == warehouse.get_average(flow.income)
        assert 2.5 == warehouse.get_average(flow.debt)
        warehouse.remove_items(flow.income, in2.title)
        assert 2 == warehouse.length(flow.income)
        warehouse.remove(flow.debt, out2.title, out2.amount)
        print(warehouse.get_entries(flow.debt))
        assert 3 == warehouse.length(flow.debt)
        print(f'database tests completed in {datetime.now() - start}')
    except AssertionError as e:
        print(f' {datetime.now()} {e}\n\t{trace()}')
        print(f'database tests failed in {datetime.now() - start}')

    # out = len(warehouse.get_entries('debt'))
    # total = warehouse.return_dates(out)
    # warehouse.line_graph(total, warehouse.get_entries('debt'))

db_test()
