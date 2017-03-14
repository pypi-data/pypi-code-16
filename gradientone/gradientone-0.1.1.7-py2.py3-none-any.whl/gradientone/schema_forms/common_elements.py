

def gen_channel(num_chans=4):
    output = {}
    for i in range(1, num_chans+1):
        chan_label = "ch"+str(i)
        output[chan_label] = {}
        output[chan_label]["title"] = "Channel "+str(i)
        output[chan_label]["type"] = "object"
        output[chan_label]["properties"] = {}
        output[chan_label]["properties"]["channel_enabled"] = {}
        output[chan_label]["properties"]["channel_enabled"]["title"] = "Enabled"
        output[chan_label]["properties"]["channel_enabled"]["type"] = "boolean"
        output[chan_label]["properties"]["channel_enabled"]["default"] = True
        output[chan_label]["properties"]["channel_offset"] = {}
        output[chan_label]["properties"]["channel_offset"]["title"] = "Offset (V)"
        output[chan_label]["properties"]["channel_offset"]["type"] = "number"
        output[chan_label]["properties"]["channel_offset"]["default"] = 0
        output[chan_label]["properties"]["channel_range"] = {}
        output[chan_label]["properties"]["channel_range"]["title"] = "Range (V)"
        output[chan_label]["properties"]["channel_range"]["type"] = "number"
        output[chan_label]["properties"]["channel_range"]["default"] = 2
        output[chan_label]["properties"]["channel_coupling"] = {}
        output[chan_label]["properties"]["channel_coupling"]["title"] = "Coupling"
        output[chan_label]["properties"]["channel_coupling"]["type"] = "string"
        output[chan_label]["properties"]["channel_coupling"]["enum"] = ["dc", "ac"]
        output[chan_label]["properties"]["channel_coupling"]["default"] = "dc"
    return output

FORM_BOTTOM = [{
        "key": "comment",
        "type": "textarea",
        "placeholder": "Make a comment"
    },
    {
        "type": "section",
        "htmlClass": "row",
        "items": [
            {
                "type": "submit",
                "style": "btn-success",
                "htmlClass": "col-xs-2",
                "title": "Load"
            },
            {
                "type": "submit",
                "style": "btn-primary",
                "htmlClass": "col-xs-2",
                "title": "Save",
                "onClick": "saveTest()"
            },
            {
                "type": "button",
                "htmlClass": "col-xs-2",
                "style": "btn-default",
                "title": "Cancel",
                "onClick": "cancel()"
            }
        ]
    }]
