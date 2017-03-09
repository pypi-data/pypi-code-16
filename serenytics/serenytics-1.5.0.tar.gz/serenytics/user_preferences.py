

class UserPreferences(object):
    HOME_FOLDER = 'Home'

    def __init__(self, preferences):
        self._preferences = preferences

    @property
    def webapp_folder_names(self):
        folder_names = [self.HOME_FOLDER]
        folder_names.extend([folder['name'] for folder in self._preferences.get('webappsFolders')])
        return folder_names

    def _get_folder_from_id(self, folder_id, entity_type):
        try:
            folder = [folder for folder in self._preferences.get(entity_type + 'sFolders')
                      if folder['id'] == folder_id][0]
            return folder
        except IndexError:
            raise Exception('Unknown folder_id: ' + folder_id)
