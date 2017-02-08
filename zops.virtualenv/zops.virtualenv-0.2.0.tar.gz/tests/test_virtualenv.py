

def test_virtualenv(tmpdir, cli_runner):
    import os
    from zops.virtualenv.cli import main

    def assert_installed_packages(*packages):
        from virtualenvapi.manage import VirtualEnvironment
        venv = VirtualEnvironment(str(workon_home.join(venv_name)))
        for i_package in packages:
            assert venv.is_installed(i_package)

    def pre_checks():
        assert venv_dir.check(exists=False)

    def post_checks(result, packages, output):
        assert result.output == output
        assert result.exit_code == 0
        assert workon_home.join(venv_name).check(dir=True)
        assert workon_home.join(venv_name).join('bin/python').check(file=True)
        assert_installed_packages(*packages)

    venv_name = 'TEST'
    workon_home = tmpdir
    venv_dir = workon_home.join(venv_name)
    requirements_filename = tmpdir.join('requirements.txt')
    requirements_filename.write('requests\npytest\n')

    pre_checks()

    # Preparation
    os.environ['WORKON_HOME'] = str(workon_home)

    # Execution
    result = cli_runner.invoke(main, ['create', venv_name, '-r', str(requirements_filename)])

    post_checks(
        result,
        packages=['requests', 'pytest'],
        output="""! REQUIREMENT: {}\n* requests\n* pytest\n""".format(requirements_filename),
    )
