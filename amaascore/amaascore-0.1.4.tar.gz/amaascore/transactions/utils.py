from __future__ import absolute_import, division, print_function, unicode_literals

import csv

from amaascore.transactions.position import Position
from amaascore.transactions.transaction import Transaction


def json_to_position(json_position):
    position = Position(**json_position)
    return position


def json_to_transaction(json_transaction):
    for (collection_name, clazz) in Transaction.children().items():
        children = json_transaction.pop(collection_name, {})
        collection = {}
        for (child_type, child_json) in children.items():
            # Handle the case where there are multiple children for a given type - e.g. links
            if isinstance(child_json, list):
                child = set()
                for child_json_in_list in child_json:
                    child.add(clazz(**child_json_in_list))
            else:
                child = clazz(**child_json)
            collection[child_type] = child
        json_transaction[collection_name] = collection
    transaction = Transaction(**json_transaction)
    return transaction


def csv_filename_to_transactions(filename):
    with open(filename, 'rb') as f:
        transactions = csv_stream_to_transactions(f)
    return transactions


def csv_stream_to_transactions(stream):
    reader = csv.DictReader(stream)
    transactions = []
    for row in reader:
        transactions.append(json_to_transaction(row))
    return transactions


def transactions_to_csv(transactions, filename):
    with open(filename, 'w') as csvfile:
        transactions_to_csv_stream(transactions=transactions, stream=csvfile)


def transactions_to_csv_stream(transactions, stream):
    if not transactions:
        return
    transaction_dicts = []
    for transaction in transactions:
        transaction_dict = transaction.to_json()
        # FOR NOW - remove all children
        [transaction_dict.pop(child, None) for child in Transaction.children().keys()]
        transaction_dicts.append(transaction_dict)
    fieldnames = transaction_dicts[0].keys()
    writer = csv.DictWriter(stream, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(transaction_dicts)
