def format_line_items(line_items: list[list]) -> list[list]:
    new_line_items = []
    for line_item in line_items:
        new_line_item = []
        for i, cell in enumerate(line_item):
            cell_temp = cell
            if i > 0:
                cell_temp = {".": cell, "style": {"text_align": "r"}}
            new_line_item.append(cell_temp)
        new_line_items.append(new_line_item)
    return new_line_items


def format_column_headers(column_headers: list[str]) -> list:
    new_headers = []
    for i, header in enumerate(column_headers):
        header_temp = header
        if i > 0:
            header_temp = {".": header, "style": {"text_align": "r"}}
        new_headers.append(header_temp)
    return new_headers


def format_totals(totals: list[list], colour: str) -> list[list]:
    new_totals = []
    for total in totals:
        new_total = []
        for i, cell in enumerate(total):
            cell_temp = cell
            if i == 0:
                cell_temp = {".b": cell}
            elif "Balance" in total[0]:
                cell_temp = {f".s:14;c:{colour}": cell}
            new_total.append(cell_temp)

        new_totals.append(new_total)
    return new_totals
