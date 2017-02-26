import uuid

from ._elemental_base import ElementalBase


def process_uuid_value(value):
    """
    Processes a value into a UUID.

    Args:
        value (str or uuid): Data to process into a uuid.

    Returns:
        UUID if `value`, else None.

    Raises:
        ValueError: If `value` is not a UUID instance and cannot be converted
            into a UUID instance.
    """
    if not value:
        result = None
    elif isinstance(value, uuid.UUID):
        result = value
    else:
        try:
            result = uuid.UUID(value)
        except (TypeError, ValueError):
            msg = 'Invalid uuid value: "{0}"'
            msg = msg.format(value)
            raise ValueError(msg)

    return result


def process_uuids_value(value):
    """
    Processes a sequence of values into a sequence of UUIDs.

    Args:
        value (List[str or uuid]): Sequence of values to process.

    Returns:
        List[uuid]: Sequence of unique UUID instances.

    Raises:
        TypeError: If any item in `value` is not a UUID instance and cannot
            be converted into a UUID instance.
    """
    result = value or list()

    if isinstance(value, str):
        result = [result]
    else:
        try:
            result = list(result)
        except TypeError:
            result = [result]

    valid_values = []
    invalid_values = []
    for id in result:
        try:
            id = process_uuid_value(id)
        except ValueError:
            invalid_values.append(id)
        else:
            valid_values.append(id)

    if invalid_values:
        invalid_values = ['"{0}"'.format(id) for id in invalid_values]
        invalid_values = ', '.join(invalid_values)
        msg = 'Invalid uuid values: {0}'
        msg = msg.format(invalid_values)
        raise ValueError(msg)

    seen = set()
    result = [
        id for id in valid_values
        if id and not (id in seen or seen.add(id))
    ]

    return result


def process_elemental_class_value(value):
    """
    Processes a name into an Elemental class.

    Args:
        value (str or cls): Name of an `ElementalBase` subclass.

    Returns:
        A `ElementalBase` subclass if successful, None otherwise.
    """
    try:
        result = value if issubclass(value, ElementalBase) else None
    except TypeError:
        result = None

    if not result:
        value = str(value).lower().strip().replace(' ', '')
        for elemental_cls in ElementalBase.iter_elemental_types():
            if value == elemental_cls.__name__.lower():
                result = elemental_cls
                break

    return result


def process_data_format_value(value):
    """
    Computes a standardized label for a data format.

    Args:
        value (str): Name of a data format

    Returns:
        Formatted string if successful, None otherwise.
    """
    if value:
        return str(value).lower().strip().replace(' ', '_')
    return None
