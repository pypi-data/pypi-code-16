import logging
import json
import random
from collections import OrderedDict


class GenMenu(object):

    week_days = [
        'Monday',
        'Tuesday',
        'Wednesday',
        'Thursday',
        'Friday',
        'Saturday',
        'Sunday',
    ]

    lunch_menu = dict.fromkeys(week_days)
    dinner_menu = dict.fromkeys(week_days)

    def __init__(self, logging_level=logging.INFO):
        """
        logging_level: The wanted logging level that exists in logging module
        """

        # Create the dictionary structure
        day_dict = {'lunch': '', 'dinner': ''}
        self.my_menu = OrderedDict()
        for day in self.week_days:
            self.my_menu[day] = day_dict.copy()

        logger = logging.getLogger(__name__)
        formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        std_handler = logging.StreamHandler()
        std_handler.setFormatter(formatter)
        logger.addHandler(std_handler)

        logger.setLevel(logging_level)
        self.logger = logger

    def insert_lunch_menu(self, inpt):
        """
        Inserts a list of lunches into the menu

        First item will be Monday and next Tuesday and so forth
        :param inpt: Iterator containing lunch items
        """

        self._populate_menu(self.lunch_menu, inpt)

    def insert_dinner_menu(self, inpt, file_format=None, randomize=False):
        """
        Inserts a list of dinners into the menu

        If file_format is not specified, an iterator is expected
        First item will be Monday and next Tuesday and so forth

        Supported file_format(s): json
        """

        if file_format == 'json':
            with open(inpt, 'r') as f:
                food_items = json.load(f)
        else:
            food_items = list(inpt)

        if randomize:
            self.logger.debug("Randomizing food_items")
            self._randomize(food_items)

        self.logger.debug('food items is:{0}'.format(food_items))
        self._populate_menu(self.dinner_menu, food_items)

    def _randomize(self, lst):
        """
        Returns the list in random order
        """
        return random.shuffle(lst)

    def _populate_menu(self, menu_dict, lst):
        """
        Populate a menu with the items from a list
        """
        if not isinstance(lst, list):
            raise TypeError('Wrong type. Should be a list')
        for day, food_item in zip(GenMenu.week_days, lst):
            menu_dict[day] = food_item

        return menu_dict

    def generate_menu(self):
        """
        Generates the menu from lunch and dinner dicts
        """
        for k in self.lunch_menu:
            if self.lunch_menu[k]:
                self.my_menu[k]['lunch'] = self.lunch_menu[k]

        for k in self.dinner_menu:
            if self.dinner_menu[k]:
                self.my_menu[k]['dinner'] = self.dinner_menu[k]
