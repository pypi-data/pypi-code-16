
import copy

import logging_helper
from fdutil.dict_tools import sort_dict
from uiutil.frame.frame import BaseFrame
from configurationutil import Configuration

logging = logging_helper.setup_logging()

# General keys
EXPANDING_COLUMNS = u'expand_col'
EXPANDING_ROWS = u'expand_row'

# Frame Keys
ROWS_FIRST = u'rows_first'
WIDGET_GRID = u'widget_grid'
ITEM_KEY = u'item_key'
ITERABLE_LINE = u'iterable'
ITERABLE_SORTED = u'sort_iterable'

# Line keys
WIDGET_GRID_LINE = u'line'
LINE_DEFAULT = u'default'

# Widget Keys
WIDGET_NAME = u'name'
WIDGET_TYPE = u'type'
WIDGET_KWARGS = u'kwargs'
WIDGET_BINDING = u'binding'
WIDGET_VAR = u'var'
WIDGET_VAR_SETTINGS = u'var_settings'

BIND_FUNCTION = u'function'
BIND_EVENTS = u'events'

KWARG_VALUE = u'value'
KWARG_LOCATION = u'location'
KWARG_LAMBDA = u'lambda'

# kwarg locations
KWARG_LOCAL = u'local'
KWARG_SELF = u'self'
KWARG_PARENT = u'parent'
KWARG_WINDOW = u'window'
KWARG_DICT = u'dict'
KWARG_LIST = u'list'
KWARG_CFG = u'cfg'
KWARG_ITER_VALUE = u'iter_value'
KWARG_VAR = u'var'

# Internal line kwarg keys
_LINE_KWARG_LINE = u'line'
_LINE_KWARG_ROW = u'row'
_LINE_KWARG_COLUMN = u'column'
_LINE_KWARG_ITER_NAME = u'iterable_name'
_LINE_KWARG_ITER_VALUE = u'iterable_value'
_LINE_KWARG_DEFAULT = u'default'


class DynamicBaseFrame(BaseFrame):

    def __init__(self,
                 key,
                 *args,
                 **kwargs):

        BaseFrame.__init__(self, *args, **kwargs)

        self.key = key
        self.cfg = Configuration()

        self.item_key = self.cfg[self.key].get(ITEM_KEY)
        self.iterable_line = self.cfg[self.key].get(ITERABLE_LINE)
        self.sort_iterable = self.cfg[self.key].get(ITERABLE_SORTED, False)
        self.rows_first = self.cfg[u'{k}.{c}'.format(k=self.key, c=ROWS_FIRST)]
        self.widget_grid = self.cfg[u'{k}.{c}'.format(k=self.key, c=WIDGET_GRID)]

        self.is_list = False

        # If an item_key is set then load it from self.cfg
        if self.item_key is not None:
            config = self.cfg[self.item_key]

            if isinstance(config, dict):
                self.parent.item_dict = config

            if isinstance(config, list):
                self.parent.item_list = config
                self.is_list = True

        if self.sort_iterable:
            # sort_iterable is true convert item_dict to an Ordered dict and sort it
            self.parent.item_dict = sort_dict(self.parent.item_dict)
            self.parent.item_list.sort()

        self.draw_layout()

    def __iter_layout(self,
                      line_idx,
                      line_cfg,
                      offset,
                      item_name,
                      item_value=None,
                      **line_kwargs):

        line_kwargs[_LINE_KWARG_ITER_NAME] = item_name

        if item_value is not None:
            line_kwargs[_LINE_KWARG_DEFAULT] = line_cfg.get(LINE_DEFAULT, False)
            line_kwargs[_LINE_KWARG_ITER_VALUE] = item_value

        line_kwargs[
            _LINE_KWARG_ROW
            if self.rows_first
            else _LINE_KWARG_COLUMN
        ] = line_idx + offset

        self.draw_line(**line_kwargs)

        # Update iterable offset so that further lines are drawn in their correct position
        offset += 1

        return offset, line_kwargs

    def draw_layout(self):

        iterable_offset = 0

        for line_idx, line in enumerate(self.widget_grid):

            line_kwargs = {
                _LINE_KWARG_LINE: line[WIDGET_GRID_LINE],
                _LINE_KWARG_ROW if self.rows_first else _LINE_KWARG_COLUMN: line_idx + iterable_offset
            }

            logging.debug(u'draw_layout line kwargs: {k}'.format(k=line_kwargs))

            if line_idx == self.iterable_line:

                if self.is_list:
                    for item_name in self.parent.item_list:
                        iterable_offset, line_kwargs = self.__iter_layout(line_idx=line_idx,
                                                                          line_cfg=line,
                                                                          offset=iterable_offset,
                                                                          item_name=item_name,
                                                                          **line_kwargs)

                else:
                    for item_name, item_value in self.parent.item_dict.iteritems():
                        iterable_offset, line_kwargs = self.__iter_layout(line_idx=line_idx,
                                                                          line_cfg=line,
                                                                          offset=iterable_offset,
                                                                          item_name=item_name,
                                                                          item_value=item_value,
                                                                          **line_kwargs)

                # Once iteration complete remove the extra kwargs
                del line_kwargs[_LINE_KWARG_ITER_NAME]

                if not self.is_list:
                    del line_kwargs[_LINE_KWARG_DEFAULT]
                    del line_kwargs[_LINE_KWARG_ITER_VALUE]

            else:
                self.draw_line(**line_kwargs)

        # Configure columns that are allowed to expand
        for column in self.cfg[self.key].get(EXPANDING_COLUMNS, []):
            self.columnconfigure(column, weight=1)

        # Configure rows that are allowed to expand
        for row in self.cfg[self.key].get(EXPANDING_ROWS, []):
            self.rowconfigure(row, weight=1)

    def draw_line(self,
                  line,
                  row=0,
                  column=0,
                  default=False,
                  **iter_kwargs):

        for idx, widget in enumerate(line):

            # Set row / column value
            if self.rows_first:
                column = idx

            else:
                row = idx

            # Draw the widget for this position
            self.draw_widget(widget_config=copy.deepcopy(widget),
                             row=row,
                             column=column,
                             **iter_kwargs)

        if default:
            item_name = iter_kwargs.get(_LINE_KWARG_ITER_NAME)

            if item_name is not None:
                item_dict = self.parent.item_dict.get(item_name)

                if item_dict is not None and LINE_DEFAULT in item_dict:
                    self.label(text=u'X' if item_dict[LINE_DEFAULT] else u'',
                               row=row if self.rows_first else row + 1,
                               column=column + 1 if self.rows_first else column)
                    if item_dict[LINE_DEFAULT]:
                        self.parent.default.set(item_name)

    def draw_widget(self,
                    widget_config,
                    row=None,
                    column=None,
                    **iter_kwargs):

        # Get the Tk objects (These must be defined in widget & var mix-ins!)
        widget_object = getattr(self, widget_config[WIDGET_TYPE])  # Tk widget object
        widget_var_object = getattr(self, widget_config[WIDGET_VAR])  # Tk var object

        # Get the kwarg configurations for both objects
        widget_kwargs = widget_config.get(WIDGET_KWARGS, {})
        widget_var_settings = widget_config.get(WIDGET_VAR_SETTINGS, {})

        # Setup object name parameters
        widget_name = u'_{id}_{type}'.format(id=widget_config[WIDGET_NAME],
                                             type=widget_config[WIDGET_TYPE])

        # if this is an iterable then we must set the name accordingly to stop each new line overwriting the previous
        if _LINE_KWARG_ITER_NAME in iter_kwargs:
            widget_name = u'{widget_name}_{iter_name}'.format(widget_name=widget_name,
                                                              iter_name=iter_kwargs[_LINE_KWARG_ITER_NAME])

        widget_var_name = u'{widget_name}_var'.format(widget_name=widget_name)

        # Setup dict of available local params for use in kwargs
        locals_dict = {
            u'widget_name': widget_name,
            u'widget_var_name': widget_var_name,
            u'row': row,
            u'column': column
        }

        # add the iterable kwargs for this widget line to the locals dict
        locals_dict.update(iter_kwargs)

        # Process the widget var initial value
        widget_var_kwargs = {}

        if u'value' in widget_var_settings:
            widget_var_kwargs[u'value'] = self.handle_kwarg(widget_var_settings[u'value'], locals_dict)

        # Create the widget var.
        widget_var = widget_var_object(name=widget_var_name,
                                       **widget_var_kwargs)

        # Process the widget var trace value (if required)
        if u'trace' in widget_var_settings:
            widget_var_trace_fn = self.handle_kwarg(widget_var_settings[u'trace'], locals_dict)

            # Ensure the function has not evaluated as a string value (this is possible!)
            if not isinstance(widget_var_trace_fn, str):
                widget_var.trace("w", (lambda name, index, mode, wdgt_name=widget_name, wdgt_var=widget_var:
                                       widget_var_trace_fn(wdgt_name, wdgt_var)))

        # Add widget_var to locals_dict
        locals_dict[u'widget_var'] = widget_var

        # Process the widget kwargs
        for kw_name, kw in widget_kwargs.iteritems():
            widget_kwargs[kw_name] = self.handle_kwarg(kw, locals_dict)

        # Handle grid row & column
        if u'row' not in widget_kwargs:
            widget_kwargs[u'row'] = row

        if u'column' not in widget_kwargs:
            widget_kwargs[u'column'] = column

        # If this is a radiobutton and selected has not been set then set selected
        if widget_config[WIDGET_TYPE] == u'radiobutton' \
                and self.parent.selected.get() == u'' \
                and _LINE_KWARG_ITER_NAME in locals_dict:
                self.parent.selected.set(locals_dict[_LINE_KWARG_ITER_NAME])

        # Draw the widget
        widget_object(name=widget_name,
                      **widget_kwargs)

        # Handle bind for widget (if required)
        bind = widget_config.get(WIDGET_BINDING, False)

        if bind:
            bind_fn = self.handle_kwarg(bind[BIND_FUNCTION], locals_dict)

            # Ensure the function has not evaluated as a string value (this is possible!)
            if not isinstance(bind_fn, str):
                self.bind_events(control=getattr(self, widget_name),
                                 events=bind[BIND_EVENTS],
                                 function=bind_fn)

    def handle_kwarg(self,
                     kwarg_cfg,
                     locals_dict=None):

        logging.debug(u'un-processed kwarg: {k}'.format(k=kwarg_cfg))

        if locals_dict is None:
            locals_dict = {}

        logging.debug(u'locals_dict: {l}'.format(l=locals_dict))

        # Handle specific kwargs that are expected to have config
        # Get kwarg config
        kw_value = kwarg_cfg[KWARG_VALUE]
        kw_location = kwarg_cfg.get(KWARG_LOCATION)
        kw_lambda = kwarg_cfg.get(KWARG_LAMBDA, False)

        # If the value is a number set the kwarg otherwise we have to do some processing!
        if isinstance(kw_value, (int, float)):
            kwarg = kw_value

        else:
            # Split the attribute path in case we have to reduce
            attribute_pth = kw_value.split(u'.')

            # Decode the kwarg value
            if kw_location == KWARG_LOCAL and kw_value in locals_dict:
                kwarg = locals_dict[kw_value]

            elif kw_location == KWARG_SELF:
                kwarg = reduce(getattr, attribute_pth, self)

            elif kw_location == KWARG_PARENT:
                kwarg = reduce(getattr, attribute_pth, self.parent)

            elif kw_location == KWARG_WINDOW:
                kwarg = reduce(getattr, attribute_pth, self.parent.parent.master)

                if kw_lambda:
                    cmd_fn = kwarg  # We need to use a temp var otherwise lambda will pass itself!
                    kwarg = (lambda name=locals_dict.get(u'widget_name'), var=locals_dict.get(u'widget_var'):
                             cmd_fn(widget_name=name,
                                    widget_var=var))

            elif kw_location == KWARG_VAR:
                # Get the self reference to our widget var
                kwarg = getattr(self, locals_dict[kw_value])

            elif kw_location == KWARG_DICT:
                kwarg = self.parent.item_dict.get(kw_value)

            elif kw_location == KWARG_LIST:
                kwarg = self.parent.item_list[kw_value]

            elif kw_location == KWARG_CFG and self.item_key is not None:
                key = u'{c}.{k}'.format(c=self.item_key,
                                        k=kw_value)

                kwarg = self.cfg[key]

            elif kw_location == KWARG_ITER_VALUE:
                # Get the iterable_value param
                iterable_values = locals_dict.get(_LINE_KWARG_ITER_VALUE)

                # If iterable_values or lookup value is not available then return empty string
                kwarg = u'' if iterable_values is None else iterable_values.get(kw_value, u'')

            else:
                kwarg = kw_value

        logging.debug(u'processed kwarg: {k}'.format(k=kwarg))

        return kwarg
