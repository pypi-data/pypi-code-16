
from ._dynamic_base import (DynamicBaseFrame)


class DynamicWidgetFrame(DynamicBaseFrame):

    def __init__(self,
                 *args,
                 **kwargs):

        super(DynamicWidgetFrame, self).__init__(*args, **kwargs)
