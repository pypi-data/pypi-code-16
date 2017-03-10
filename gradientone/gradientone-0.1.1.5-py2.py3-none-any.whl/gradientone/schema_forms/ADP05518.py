from common_elements import FORM_BOTTOM
from gradientone.device_drivers.can.motor import PROPERTIES
from gradientone.device_drivers.can.can_helpers import get_trace_variables

# pull out only the values that can be Mapped to a PDO
PDO_MAPPABLE = [key for key in PROPERTIES.keys() if PROPERTIES[key]['pdo']]
TRACE_VARIABLES = sorted(get_trace_variables())

PROPERTIES_LIST = [{"value": key, "name": key.replace("_", " ").capitalize(),
                    "category": "poll"} for key in sorted(PDO_MAPPABLE)] + \
                  [{"value": key,
                    "name": key.replace("_", " ").replace(":", ": ").capitalize(),
                    "category": "trace"} for key in TRACE_VARIABLES]

SCHEMA_DICT = {
    "type": "object",
    "title": "Config",
    "properties": {
        "name": {
            "title": "Config Name",
            "type": "string"
        },
        "motor_end_position": {
            "title": "Destination",
            "type": "number",
            "minimum": 0,
            "maximum": 65536
        },
        "time_window": {
            "title": "Time Window",
            "type": "number",
            "minimum": 0,
            "maximum": 10
        },
        "comment": {
            "title": "Comment",
            "type": "string",
            "maxLength": 200,
            "validationMessage": "Exceeds character limit!"
        },
        "trace": {
            "title": "DAq Method",
            "type": "string",
            "enum": ["poll", "trace"]
        },
        "properties": {
            "title": "Properties",
            "type": "array",
            "items": {"type": "string"},
            "maxItems": 7,
            "description": "Please select no more than 7 properties."
        },
    },
    "required": [
        "name",
        "trace",
        "destination",
        "multiselect"
    ]
}

FORM_DICT = [
    {
        "key": "name",
        "placeholder": "Copley"
    },
    {
        "key": "motor_end_position",
        "placeholder": 123
    },
    {
        "key": "time_window",
        "placeholder": 1
    },
    {
        "key": "trace",
        "placeholder": "Choose DAq Method"
    },
    {
        "key": "properties",
        "type": "strapselect",
        "placeholder": "Please select a property.",
        "options": {
            "multiple": "true",
            "filterTriggers": ["model.trace"],
            "filter": "item.category.indexOf(model.trace) > -1"
        },
        "validationMessage": "Please select a min of 1 and max of 7 properties!",
        "titleMap": PROPERTIES_LIST
    },
] + FORM_BOTTOM

