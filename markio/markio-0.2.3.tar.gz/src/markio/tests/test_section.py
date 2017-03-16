import pytest
from markio.marked import Section, SectionList


@pytest.fixture
def section():
    return Section('title', 'data', ['tag1', 'tag2'])


@pytest.fixture
def section_list(section):
    section2 = Section('Title-2', 'data-2')
    return SectionList(None, [section, section2])


def test_can_obtain_section_by_name(section_list, section):
    assert section_list[0] is section
    assert section_list['title'] is section
    assert section_list['Title'] is section
