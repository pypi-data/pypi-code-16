from invisibleroads_macros.disk import (
    make_enumerated_folder, make_unique_folder, resolve_relative_path)
from invisibleroads_posts.models import DummyBase, FolderMixin


class Upload(FolderMixin, DummyBase):

    @classmethod
    def spawn_folder(Class, data_folder, random_length=None, owner_id=None):
        user_folder = Class.get_user_folder(data_folder, owner_id)
        return make_unique_folder(
            user_folder, length=random_length,
        ) if random_length else make_enumerated_folder(user_folder)

    @classmethod
    def get_user_folder(Class, data_folder, owner_id):
        parent_folder = Class.get_parent_folder(data_folder)
        folder_name = str(owner_id or 'anonymous')
        return resolve_relative_path(folder_name, parent_folder)

    def get_folder(self, data_folder):
        user_folder = self.get_user_folder(data_folder, self.owner_id)
        folder_name = str(self.id)
        return resolve_relative_path(folder_name, user_folder)
