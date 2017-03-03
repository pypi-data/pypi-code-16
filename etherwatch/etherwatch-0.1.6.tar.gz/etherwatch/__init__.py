# /usr/bin/env python

from etherwatch.ether_functions import EtherFunctions
from etherwatch.messaging_functions import MessagingFunctions
from etherwatch.db_functions import DatabaseFunctions

from etherwatch.positions import POSITIONS

def get_eth_price():
    return EtherFunctions.get_eth_exchange_usd()


def message_clients(eth_price):
    for person_str in POSITIONS:
        person = POSITIONS[person_str]
        position = EtherFunctions.get_positions(eth_price, person)
        sign = EtherFunctions.set_sign(position)
        message = MessagingFunctions.write_position_message(
                person_str,
                eth_price,
                sign,
                position
        )
        MessagingFunctions.notify(person_str, message)


def log_eth_price(eth_price):
    DatabaseFunctions.create_database()
    DatabaseFunctions.log_price_datetime(eth_price)


def main():
    eth_price = get_eth_price()
    log_eth_price(eth_price)
    message_clients(eth_price)


if __name__ == '__main__':
    main()
