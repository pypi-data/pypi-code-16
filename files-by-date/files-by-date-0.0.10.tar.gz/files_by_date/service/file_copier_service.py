from files_by_date.service.files_service import FilesService


class FileCopierService:
    def __init__(self, *, input_dir, target_dir, force_overwrite=False):
        self.input_dir = input_dir
        self.target_dir = target_dir
        self.force_overwrite = force_overwrite

    def copy_files(self):
        FilesService.copy_files(
            FilesService.group_files_by_modified_date(
                FilesService.gather_files(self.input_dir, list())),
            self.target_dir,
            self.force_overwrite)
