import io
import os
from functools import partial

import pytest

from iospec import IoSpec
from markio import parse_markio, parse_marked
from markio.utils import strip_trailing_whitespace

DIRNAME = os.path.dirname(__file__)


def src(idx):
    path = os.path.join(DIRNAME, 'examples', 'valid-%s.md' % idx)
    return open(path).read()


def markio(idx):
    return parse_markio(src(idx))


@pytest.fixture
def hello():
    path = os.path.join(DIRNAME, 'examples', 'hello-person.md')
    data = open(path).read()
    return parse_markio(data)


def mk_fixture(func, idx):
    def fixture():
        return func(idx)
    fixture.__name__ = '%s_%s' % (func.__name__, idx)
    return pytest.fixture(fixture)

src_0 = mk_fixture(src, 0)
src_1 = mk_fixture(src, 1)
src_2 = mk_fixture(src, 2)
src_3 = mk_fixture(src, 3)
src_4 = mk_fixture(src, 4)
src_5 = mk_fixture(src, 5)
src_6 = mk_fixture(src, 6)
markio_0 = mk_fixture(markio, 0)
markio_1 = mk_fixture(markio, 1)
markio_2 = mk_fixture(markio, 2)
markio_3 = mk_fixture(markio, 3)
markio_4 = mk_fixture(markio, 4)
markio_5 = mk_fixture(markio, 5)
markio_6 = mk_fixture(markio, 6)


@pytest.fixture(params=[0, 1, 2])
def round_trip_source(request):
    return src(request.param)


#
# Generic tests
#
def test_markio_is_valid_marked_source(round_trip_source):
    marked = parse_marked(round_trip_source)
    assert marked.title


#
# Test meta information
#
def test_author_syncs_with_meta(hello):
    author = 'Chips Chipperfield <chips@chipperfield.com>'
    assert hello.author == hello.meta['author'] == author

    hello.author = 'foo'
    assert hello.meta['author'] == hello.meta['Author'] == 'foo'


def test_slug_syncs_with_meta(hello):
    assert hello.slug == hello.meta['slug'] == 'hello-person'

    hello.slug = 'foo'
    assert hello.meta['slug'] == 'foo'


def test_timeout_syncs_with_meta(hello):
    assert hello.timeout == hello.meta['timeout'] == 1.5

    hello.timeout = 5
    assert hello.meta['timeout'] == 5


def test_tags_syncs_with_meta(hello):
    tags = ['beginner', 'basic']
    assert hello.meta['tags'] == tags
    assert hello.tags == tags


#
# Sections
#
def test_sections_basic(markio_0):
    obj = markio_0
    assert list(obj.sections.keys()) == [
        'Description',
    ]


def test_sections_extra(markio_6):
    obj = markio_6
    assert list(obj.sections.keys()) == [
        'Description',
        'Extra section',
        'Extra section 2'
    ]


def test_sections(hello):
    assert list(hello.sections.keys()) == [
        'Description',
        'Examples',
        'Tests',
        'Answer Key',
        'Answer Key',
        'Placeholder',
        'Placeholder',
    ]
    assert hello.sections[0].title == 'Description'


def test_description_section_maps_to_attribute(markio_0):
    assert markio_0.sections['description'].data == 'Description.'
    assert markio_0.description == 'Description.'

    markio_0.description = 'other'
    assert markio_0.description == 'other'
    assert markio_0.sections['description'].data == 'other'


def test_examples_is_iospec_source(markio_2):
    examples = markio_2.examples
    assert isinstance(examples, IoSpec)
    assert len(examples) == 1

    tests = markio_2.tests
    src1 = '    @input $name\n    @input john lennon'
    src2 = '@input $name\n@input john lennon'
    assert markio_2.tests_source == src2
    assert isinstance(tests, IoSpec)
    assert tests.source() == src2
    assert len(tests) == 2


#
# Answer keys
#
def test_answer_key_behaves_like_a_dict(markio_0, markio_3):
    assert dict(markio_0.answer_key) == {}
    assert dict(markio_3.answer_key) == {
        'python': "print('hello world')",
        'ruby': "puts 'hello world'",
    }
    assert len(markio_3.answer_key) == 2


def test_can_add_a_new_answer_key(markio_3):
    markio_3.answer_key.add('...', 'js')
    assert dict(markio_3.answer_key) == {
        'python': "print('hello world')",
        'ruby': "puts 'hello world'",
        'js': '...'
    }


#
# Placeholder
#
def test_placeholder_behaves_like_a_dict(markio_0, markio_4):
    assert dict(markio_0.placeholder) == {}
    assert dict(markio_4.placeholder) == {
        None: 'Generic comment',
        'ruby': 'Use the `puts text` command'
    }
    assert len(markio_4.placeholder) == 2


def test_placeholder_can_determine_comment_from_text(markio_4):
    assert markio_4.placeholder['python'] == '# Generic comment'
    assert markio_4.placeholder['c'] == '/**\n * Generic comment\n */'


#
# Non-standard values
#
def test_extra_sections_supported(markio_6):
    obj = markio_6
    assert sorted(obj.extra.keys()) == [('extra section',),
                                        ('extra section 2', 'meta')]
    assert obj.extra['extra section'] == 'Extra section.'
    assert obj.extra['extra section 2', 'meta'] == 'Extra section 2.'


#
# Other tests
#
def test_round_trip(hello):
    path = os.path.join(DIRNAME, 'examples', 'hello-person.md')
    src = strip_trailing_whitespace(hello.source())
    with open(path) as F:
        data = strip_trailing_whitespace(F.read())
        assert src == data
