from unittest import TestCase
import xml.etree.ElementTree as ET
from autosetup.app import Generator


class TestGenerator(TestCase):

    def test_generate_setup_file(self):
        tree = ET.fromstring('''<DocumentData>
    <BuildConfigurations>
        <BuildConfig>
            <Filename>setup.exe</Filename>
        </BuildConfig>
    </BuildConfigurations>
</DocumentData>''')
        Generator._generate_setup_file(tree, 'hello')
        self.assertEqual('''<DocumentData>
    <BuildConfigurations>
        <BuildConfig>
            <Filename>hello</Filename>
        </BuildConfig>
    </BuildConfigurations>
</DocumentData>''', ET.tostring(tree).decode())

    def test__generate_session_data(self):
        o = '''<DocumentData>
    <SUF7SessionVars>
        <SessionVar>
            <Name>%IMDNS%</Name>
            <Value>lingyi365</Value>
            <Type>10</Type>
        </SessionVar>
        <SessionVar>
            <Name>%IMIP%</Name>
            <Value>172.18.113.224</Value>
            <Type>10</Type>
        </SessionVar>
    </SUF7SessionVars>
</DocumentData>'''
        tree = ET.fromstring(o)
        Generator._generate_session_data(tree, {
            'IM': {
                'DNS': 'imly365',
                'IP': '211.151.85.100',
            }})
        aa = ET.tostring(tree).decode()
        self.assertEqual('''<DocumentData>
    <SUF7SessionVars>
        <SessionVar>
            <Name>%IMDNS%</Name>
            <Value>imly365</Value>
            <Type>10</Type>
        </SessionVar>
        <SessionVar>
            <Name>%IMIP%</Name>
            <Value>211.151.85.100</Value>
            <Type>10</Type>
        </SessionVar>
    </SUF7SessionVars>
</DocumentData>''', ET.tostring(tree).decode())
