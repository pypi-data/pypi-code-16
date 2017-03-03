from .utils import is_seq
from collections import OrderedDict

EXCLUDE_ME = 0xDEADC0DE

def default_context(ctx=None):
    return {} if not isinstance(ctx, dict) else ctx

def do(item, segment, ctx=None):
    if callable(segment):
        if hasattr(segment, 'requires_context'):
            return segment(default_context(ctx), item)
        return segment(item)
    return segment

def doall(item, pipeline, ctx=None):
    for seg in pipeline:
        if isinstance(seg, tuple):
            item = tuple([do(item, subseg, ctx) for subseg in seg])
        else:
            item = do(item, seg, ctx)
    return item

def render_item(description, item, ctx=None):
    result = OrderedDict() if isinstance(description, OrderedDict) else {}
    for key, pipeline in description.items():
        if isinstance(pipeline, dict):
            sub_description = pipeline
            rendered = render_item(sub_description, item, ctx)
        elif isinstance(pipeline, list):
            rendered = doall(item, pipeline, ctx)
        elif callable(pipeline):
            rendered = pipeline(doall, item) # no ctx? I might yank callable pipelines ...
        else:
            raise AssertionError("render pipeline for item is an unhandled type: %r" % type(pipeline))
        if rendered == EXCLUDE_ME:
            # pipeline has indicated this key should be discarded from the results
            continue
        result[key] = rendered
    return result

def render(description, data, ctx=None):
    assert is_seq(data), "data must be a sequence of values, not %r" % type(data)
    return map(lambda item: render_item(description, item, ctx), data)
