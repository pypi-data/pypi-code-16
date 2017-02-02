from click import Option, Argument
from groundwork.patterns import GwCommandsPattern
from groundwork_utilities.resources import get_resources


class GwResourceMonitor(GwCommandsPattern):
    def __init__(self, app, **kwargs):
        self.name = kwargs.get("name", self.__class__.__name__)
        super(GwResourceMonitor, self).__init__(app, **kwargs)

    def activate(self):
        self.commands.register("resources", "Prints used resources", self._print_resources,
                               params=[Argument(("resource",),
                                                required=False),
                                       Option(("--description", "-d"),
                                              required=False,
                                              help="Will print also a short description of each value",
                                              default=False,
                                              is_flag=True)])
        self.commands.register("resources_list", "Prints a list of all available resources", self._print_resources_list)

    def _print_resources_list(self):
        resources = get_resources()
        print("Application: %s" % ", ".join(resources["application"].keys()))
        print("\nSystem: %s" % ", ".join(resources["system"].keys()))

    def _print_resources(self, resource=None, description=False):
        resources = get_resources()

        if resource is not None:
            if resource in resources["application"].keys():
                self._print_nice(resource, resources["application"][resource], description)
            if resource in resources["system"].keys():
                self._print_nice(resource, resources["system"][resource], description)
        else:
            print("\nApplication")
            print("-----------")
            for key, item in resources["application"].items():
                self._print_nice(key, item, description)
            print("\nSystem")
            print("------")
            for key, item in resources["system"].items():
                self._print_nice(key, item, description)

    def _print_nice(self, key, item, description=False):
        if isinstance(item["value"], list):
            print(key)
            for element in item["value"]:
                print("%s: %s" % (key, element))
        elif isinstance(item["value"], dict):
            print(key)
            for name, element in item["value"].items():
                print("%s: %s" % (name, element))
        else:
            print("%s: %s" % (key, item["value"]))
        if description:
            print(item["description"], "\n")
