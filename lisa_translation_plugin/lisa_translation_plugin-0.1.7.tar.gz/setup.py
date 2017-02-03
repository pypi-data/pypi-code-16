from setuptools import setup

setup(
    name='lisa_translation_plugin',
    packages=['lisa_translation_plugin'],
    version='0.1.7',
    description='A translation plugin to use with Lisa (Lightweight Improvable Software Assistant).',
    author='Xavier Saliniere',
    author_email='xavier.saliniere@openmailbox.org',
    url='https://bitbucket.org/lisadevteam/lisa-translation-plugin',
    download_url='https://bitbucket.org/lisadevteam/lisa-translation-plugin/get/master.zip',
    keywords=['plugin', 'translate', 'translation', 'lisa'],
    classifiers=[],
    requires=['lisa_sdk', 'goslate'],
    entry_points={
        'lisaplugins': [
            'lisa_translation_plugin = lisa_translation_plugin:LisaTranslationPlugin',
        ],
    },
)
