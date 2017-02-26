import uuid

import pytest

import elemental_core


class _ProcessUUIDValueParams(object):
    values = [
        None,
        uuid.uuid4(),
        str(uuid.uuid4()),
        'garbage'
    ]


@pytest.mark.parametrize('value', _ProcessUUIDValueParams.values)
def test_process_uuid_value(value):
    if not value:
        result = elemental_core.util.process_uuid_value(value)
        assert result is None
    elif isinstance(value, uuid.UUID):
        result = elemental_core.util.process_uuid_value(value)
        assert result is value
    else:
        try:
            value_uuid = uuid.UUID(value)
        except (TypeError, ValueError):
            with pytest.raises(ValueError):
                elemental_core.util.process_uuid_value(value)
        else:
            result = elemental_core.util.process_uuid_value(value)
            assert result == value_uuid
