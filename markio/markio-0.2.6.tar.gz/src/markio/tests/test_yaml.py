from markio.pretty_yaml import dump


def test_yaml_dumps_pretty_docs():
    data = {'foo': 'spam eggs', 'bar': ['ham', 'spam', 'eggs']}
    print(dump(data))
    assert dump(data, safe=False) == \
"""
bar:
  - ham
  - spam
  - eggs
foo: spam eggs
""".lstrip()


def test_yaml_dumps_special_numbers():
    data = {'foo': 'spam\neggs\nparagraph', 'bar': [float('inf'), float('nan'), -float('inf')]}
    print(dump(data))
    assert dump(data, safe=False) == \
"""
bar:
  - .inf
  - .nan
  - -.inf
foo: |-
  spam
  eggs
  paragraph
""".lstrip()


def test_yaml_nested():
    data = {'foo': {'one': 1, 'two': 2}, 'bar': [{}, {'one': 1}, {'single': 1, 'many': [2, 3, 4]}]}
    data = dump(data, safe=False, vspacing=False)
    print(data)
    assert data == \
"""
bar:
  - {}
  - one: 1
  - many:
      - 2
      - 3
      - 4
    single: 1

foo:
  one: 1
  two: 2
""".lstrip()


def test_yaml_nested_vspacing():
    data = {'foo': {'one': 1, 'two': 2}, 'bar': [{}, {'one': 1}, {'single': 1, 'many': [2, 3, 4]}]}
    data = dump(data, safe=False, vspacing=True)
    print(data)
    assert data == \
"""
bar:
  - {}

  - one: 1

  - many:
      - 2
      - 3
      - 4
    single: 1

foo:

  one: 1

  two: 2
""".lstrip()


