import pytest

from markio.marked import parse_marked


@pytest.fixture
def src():
    return """Title
=====

    meta1: value1
    meta2: value2

Short description paragraph.

Or maybe two paragraphs ;-)


Subsection 1
------------

Subsection 1.


Subsection 2
------------

Subsection 2.
"""


@pytest.fixture()
def src_hash_titles():
    return """# title

    meta: value

short description

## sub1

sub text.

## sub2

sub text.
"""


@pytest.fixture
def marked(src):
    return parse_marked(src)


@pytest.fixture
def marked_with_hashes(src_with_hashes):
    return parse_marked(src_hash_titles)


def test_parse_valid_document(src):
    marked = parse_marked(src)
    assert marked.title == 'Title'
    assert 'meta1' in marked.meta
    assert 'meta2' in marked.meta
    assert marked.short_description.startswith('Short description paragraph.')
    assert marked.short_description.endswith(';-)')
    assert len(marked.sections) == 2
    assert marked.sections[0][0] == ('Subsection 1')
    assert marked.sections[1][0] == ('Subsection 2')


def test_valid_document_round_trip(src):
    marked = parse_marked(src)
    assert marked.source() == src


def test_source_with_hash_titles(src_hash_titles):
    marked = parse_marked(src_hash_titles)
    assert marked.title == 'title'
    assert 'meta' in marked.meta
    assert marked.short_description == 'short description'
    assert marked.sections[0] == ('sub1', 'sub text.', ())
    assert marked.sections[1] == ('sub2', 'sub text.', ())
    assert len(marked.sections) == 2


def test_marked_behaves_as_a_seq(marked):
    title, meta, descr, sections = marked
    assert len(marked) == 4
    assert marked[0] == marked[-4] == title
    assert marked[1] == marked[-3] == meta
    assert marked[2] == marked[-2] == descr
    assert marked[3] == marked[-1] == sections


def test_marked_to_json_conversion(marked):
    assert marked.to_json() == {
        'title': 'Title',
        'meta': {'meta1': 'value1', 'meta2': 'value2'},
        'short_description': marked.short_description,
        'sections': [
            ['Subsection 1', 'Subsection 1.', []],
            ['Subsection 2', 'Subsection 2.', []],
        ]
    }


def test_marked_pprint(marked):
    assert marked.pformat() == """
title: Title
short_description: |-
  Short description paragraph.

  Or maybe two paragraphs ;-)
meta:
  meta1: value1
  meta2: value2
sections:
  - - Subsection 1
    - Subsection 1.
    - []
  - - Subsection 2
    - Subsection 2.
    - []
""".lstrip()


def test_produces_identical_copies(marked):
    cp = marked.copy()
    assert cp is not marked
    assert cp.to_json() == marked.to_json()
    assert cp == marked


def test_marked_repr(marked):
    assert repr(marked) == "Marked('Title')"