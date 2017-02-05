from files_by_date.parsers.command_line_argument_parser import CommandLineArgumentParser
from files_by_date.service.file_copier_service import FileCopierService
from files_by_date.validators.argument_validator import ArgumentValidator


def run(*, args=None):
    command_line_argument_parser = CommandLineArgumentParser()

    try:
        arguments = ArgumentValidator.validate_arguments(command_line_argument_parser.parse(args=args))
    except AssertionError as assertion_error:
        command_line_argument_parser.print_help()
        raise assertion_error

    file_mover = FileCopierService(input_dir=arguments.input_dir, target_dir=arguments.target_dir,
                                   force_overwrite=arguments.force_overwrite)
    file_mover.copy_files()
    # print(f'Copying files within {arguments.input_dir} to {arguments.target_dir} in YYYYMM formatted subdirectories') # 3.6
    print('Copying files within {input_dir} to {target_dir} in YYYYMM formatted subdirectories'.format(
        input_dir=arguments.input_dir, target_dir=arguments.target_dir))
