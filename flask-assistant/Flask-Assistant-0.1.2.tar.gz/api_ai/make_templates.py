import yaml

def build_user_says_skeleton(self):
    skeleton = {}
    for intent in self.assist._intent_action_funcs:
       skeleton.append({intent: {'UserSays': [], 'Annotations': []}})

    with open self.template_file as f:
        yaml.dump(skeleton, f)

def build_user_says_skeleton(self):
    skeleton = {}
    for intent in self.assist._intent_action_funcs:
       skeleton.append({intent: {'UserSays': [], 'Annotations': []}})

    with open self.template_file as f:
        yaml.dump(skeleton, f)

def build_enttity(assist):
    skeleton = {}
    for intent in self._intent_action_funcs:
        action_func = self.assist._intent_action_funcs[intent_name][0]
        for param in inspect.getargspec(action_func).args:
            skeleton[param] = ['entry1': ['synonym', 'synonym']]


        

