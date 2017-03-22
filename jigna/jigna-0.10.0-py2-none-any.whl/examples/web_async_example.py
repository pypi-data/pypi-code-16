"""
This example shows how to serve a simple jigna view over the web.
"""

#### Imports ####
from __future__ import print_function

import argparse

from tornado.ioloop import IOLoop
from traits.api import HasTraits, Int, Str, Instance, List, Dict
from jigna.vue_template import VueTemplate
from jigna.template import Template
from jigna.web_app import WebApp

#### Domain model ####


class Person(HasTraits):
    name = Str
    age  = Int
    start = Int
    friends = List(Instance('Person'))
    spouse = Instance('Person')
    fruits = List(Str)
    tags = Dict

    def add_friend(self):
        self.friends.append(Person(name='Person', age=0))

    def remove_friend(self, index):
        del self.friends[index]

    def _anytrait_changed(self, trait, new, old):
        if trait != 'friends':
            print(trait, old, new)


#### UI layer ####

body_html_vue = """
<html>
    <head>
        <!-- Load the jigna-vue script. The location of jigna-vue script file
        will always be '/jigna/jigna-vue.js' -->
        <script type='text/javascript' src='/jigna/jigna-vue.js'></script>

        <!-- Once jigna is loaded, initialize it. -->
        <script type='text/javascript'>
            jigna.initialize({async:%s, debug:true});
        </script>
    </head>

  <body>
    <h2> Using Vue.js with async: %s, N={{person.friends.length}}</h2>
    <div>
      Name: <input v-model="person.name"><br/>
      Age: <input v-model="person.age" number><br/>
      Spouse: {{person.spouse.name}}<br/>
      Start: <input v-model="person.start" number>
      <div v-for="(tag, value) in person.tags">
       <label>{{tag}}</label><input v-model="value">
      </div>
    </div>
    <div style="height:150px; width: 1000px; overflow:scroll;" class="resizable">
      <div v-for="friend in person.friends | limitBy 20 person.start">
         Name: <input v-model="friend.name"> Age: <input v-model="friend.age" number>
         <div v-if="friend.spouse">Spouse: {{friend.spouse.name}}</div>
        <label v-on:click="person.remove_friend(person.start + $index)">-</label>
      </div>
    </div>
    <div v-on:click="person.start = Math.min(person.start + 10, person.friends.length)"> &gt;</div>
    <div v-on:click="person.add_friend()">+</div>


  <script>
      var vm = undefined;

      jigna.ready.done(function() {
          var vm = new Vue({
              el: "body", // Attach to the body tag.
              data: jigna.models,
          });
      });

    </script>

  </body>

"""

body_html_ng = """
<html ng-app='jigna'>
    <head>
        <script type='text/javascript' src='/jigna/jigna.js'></script>

        <!-- Once jigna is loaded, initialize it. -->
        <script type='text/javascript'>
            jigna.initialize({async:%s, debug:true});
        </script>
    </head>

  <body>
    <h2> Using angular.js with async: %s, N={{person.friends.length}}</h2>
    <div>
      Name: <input ng-model="person.name"><br/>
      Age: <input ng-model="person.age" type="number"><br/>
      Spouse: {{person.spouse.name}}<br/>
      Start: <input ng-model="person.start" type="number">
      <div ng-repeat="(tag, value) in person.tags">
       <label>{{tag}}</label><input ng-model="value">
      </div>
    </div>
    <div style="height:150px; width: 1000px; overflow:scroll;" class="resizable">
      <div ng-repeat="friend in person.friends.slice(person.start, person.start+20)">

         Name: <input ng-model="friend.name"> Age: <input ng-model="friend.age" number>
         <div ng-if="friend.spouse">Spouse: {{friend.spouse.name}}</div>
        <label ng-click="person.remove_friend(person.start + $index)">-</label>
      </div>
    </div>
    <div ng-click="person.start = Math.min(person.start + 10, person.friends.length)"> &gt;</div>
    <div ng-click="person.add_friend()">+</div>

  </body>

"""


#### Entry point ####

def main(async=True, N=10000, engine='vue'):
    s_async = 'true' if async else 'false'
    if engine == 'vue':
        template = VueTemplate(
            html=body_html_vue%(s_async, s_async)
        )
    elif engine == 'ng':
        template = Template(
            html=body_html_ng%(s_async, s_async)
        )

    # Start the tornado ioloop application
    ioloop = IOLoop.instance()

    # Instantiate the domain model
    fred = Person(name='Fred', age=42)
    fred.tags = dict(x=1, y=2, z=3)
    fred.spouse = Person(name='Wilma', age=40)
    fred.friends = [Person(name=str(i), age=i) for i in range(N)]

    # Create a web app serving the view with the domain model added to its
    # context.
    import socket
    from jigna.utils.web import get_free_port
    #port = get_free_port()
    port = 8000
    app = WebApp(template=template, context={'person': fred}, async=async)
    #addr = socket.gethostbyname(socket.gethostname())
    #print(addr)
    app.listen(port)

    # Start serving the web app on port 8000.
    #
    # Point your web browser to http://localhost:8000/ to connect to this jigna
    # web app. Any operation performed on the client directly update the
    # model attributes on the server.
    print('Serving on port %s...'%port)
    from threading import Thread
    def set_attrs():
        import time
        time.sleep(5)
        fred.name = 'Guido'
        fred.age = 25
        time.sleep(0.1)
        del fred.tags['z']
        time.sleep(0.1)
        fred.tags['a'] = 1
        time.sleep(0.1)
        fred.tags['a'] = 100

    t = Thread(target=set_attrs)
    t.setDaemon(True)
    t.start()
    ioloop.start()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Jigna test code',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        '--sync', help='Use sync mode', action='store_true', default=False
    )
    parser.add_argument(
        '-n', help='Use N instances.', default=50000, type=int
    )
    parser.add_argument(
        '--engine', help='Use specific engine', default='vue',
        choices=['ng', 'vue']
    )
    args = parser.parse_args()
    main(not args.sync, args.n, args.engine)

#### EOF ######################################################################
