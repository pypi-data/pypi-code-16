from simpleflow.activity import with_attribute as activity

@activity
def raise_money(minimum_amount):
    # ...
    return True

@activity
def build_boat():
    # ...
    return False

@activity
def find_crew(members):
    # ...
    return 5

@activity
def find_parrot():
    # ...
    return True

@activity
def leave_seaport():
    # ...
    return True




from simpleflow.workflow import Workflow
from simpleflow.canvas import Chain, Group

from .tasks import *

class PirateBusinessWorkflow(Workflow):
    def run(self, **context):
        members = ["Quartermaster", "Cabin Boy", "Gunner", "Carpenter"]

        chain = Chain(
            (find_money, [1000]),
            Group(
                build_boat,
                (find_crew, [members]),
                find_parrot,
            ),
            leave_seaport,
        )

        self.submit(chain)


