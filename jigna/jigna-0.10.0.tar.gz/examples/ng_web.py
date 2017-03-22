"""
This example shows how to serve a simple jigna view over the web.
"""

#### Imports ####
from __future__ import print_function

from tornado.ioloop import IOLoop
from traits.api import HasTraits, Int, Str, Instance, List
from jigna.api import Template, WebApp

#### Domain model ####

class Person(HasTraits):
    name = Str
    age  = Int

    friends = List(Instance('Person'))

    def add_friend(self):
        self.friends.append(Person(name='Person', age=0))

    #def _anytrait_changed(self, trait, new, old):
    #    print(trait, old, new)

#### UI layer ####

body_html = """
    <div>
      Name: <input ng-model="person.name"><br>
      Age: <input ng-model="person.age" number>
    </div>
    <div style="height:150px; width: 400px; overflow:scroll;" class="resizable">
      <div ng-repeat="friend in person.friends">
         Name: <input ng-model="friend.name"> Age: <input ng-model="friend.age" type="number">
      </div>
    </div>
    <div ng-click="person.add_friend()">+</div>
"""

template = Template(body_html=body_html)

#### Entry point ####

def main():
    # Start the tornado ioloop application
    ioloop = IOLoop.instance()

    # Instantiate the domain model
    fred = Person(name='Fred', age=42)
    N = 1000
    fred.friends = [Person(name=str(i), age=i) for i in range(N)]

    # Create a web app serving the view with the domain model added to its
    # context.
    app = WebApp(template=template, context={'person': fred})
    app.listen(8000)

    # Start serving the web app on port 8000.
    #
    # Point your web browser to http://localhost:8000/ to connect to this jigna
    # web app. Any operation performed on the client directly update the
    # model attributes on the server.
    print('Serving on port 8000...')
    ioloop.start()

if __name__ == "__main__":
    main()

#### EOF ######################################################################
