import os


class ArgumentValidator:
    @staticmethod
    def validate_input_dir(path):
        if not os.path.exists(path) or not os.access(path, os.R_OK):
            # raise AssertionError(f'Invalid input directory: {path}') # 3.6
            raise AssertionError('Invalid input directory: {path}'.format(path=path))

    @staticmethod
    def validate_target_dir(path):
        if not os.access(os.path.dirname(path), os.W_OK):
            # raise AssertionError(f'Invalid target directory: {path}') # 3.6
            raise AssertionError('Invalid target directory: {path}'.format(path=path))

    @staticmethod
    def validate_arguments(arguments):
        ArgumentValidator.validate_input_dir(arguments.input_dir)
        ArgumentValidator.validate_target_dir(arguments.target_dir)
        return arguments
