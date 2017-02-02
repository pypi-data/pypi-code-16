from terminaltables import AsciiTable, SingleTable


def render_basic(data, title=None):
    table = AsciiTable(data, title=title)
    table.inner_row_border = True
    table.inner_footing_row_border = True
    table.padding_left = 5
    table.padding_right = 5
    print(table.table)
    print("\n")
