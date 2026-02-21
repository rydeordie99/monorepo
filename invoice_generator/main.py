import datetime
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path

from myutils.date_util import date_fmt
from pdfme import build_pdf

from .utils import format_column_headers, format_line_items, format_totals


def to_currency(dec: Decimal) -> str:
    return f"${dec:,.2f}"


@dataclass
class Invoice:
    sender_name: str
    date: datetime.date
    number: str
    totals: list[list]
    column_headers: list[str]
    line_items: list[list]
    sender_address: str = ""
    sender_logo: str | None = None
    receiver_name: str = ""
    footer: str = ""
    colour: str = "#37A3C6"

    def generate_pdf(self) -> Path:
        new_line_items = format_line_items(self.line_items)

        column_layout = (3,) + (1,) * (len(self.column_headers) - 1)

        new_headers = format_column_headers(self.column_headers)

        new_totals = format_totals(self.totals, self.colour)

        output_pdf = Path(f"{self.number} {self.sender_name}.pdf")

        if self.sender_logo:
            table_widths = (2, 7)
            table = [{"image": self.sender_logo}]
        else:
            table_widths = (5,)
            table = []
        table += [
            {
                "style": {"cell_margin_top": 18},
                "cols": {"count": 2},
                "content": [{".b;s:14": self.sender_name}, self.sender_address],
            }
        ]
        table = [table]

        document = {
            "style": {
                "page_size": "letter",
                "border_width": 0,
                "margin_bottom": 0,
                "cell_margin": 5,
            },
            "formats": {
                "bold": {"b": 1},
                "right": {"text_align": "r"},
                "title": {"b": 1, "s": 18},
                "logo": {"b": 1, "text_align": "c"},
                "invoice": {"s": 28, "c": self.colour, "margin_left": 10},
                "table": {"cell_fill": "#FBFBFB"},
            },
            "sections": [
                {
                    "content": [
                        {"widths": table_widths, "table": table},
                        {".": " "},
                        {".": "INVOICE", "style": "invoice"},
                        {".": " \n \n "},
                        {
                            "widths": (1, 1),
                            "style": "bold",
                            "table": [["Invoice Date", "Due Date"]],
                        },
                        {
                            "widths": (1, 1),
                            "table": [
                                [
                                    f"{self.date:{date_fmt}}",
                                    f"{self.date + datetime.timedelta(7):{date_fmt}}",
                                ]
                            ],
                        },
                        {".": " "},
                        {
                            "widths": (1, 1),
                            "style": "bold",
                            "table": [["Invoice For", "Invoice Number"]],
                        },
                        {"widths": (1, 1), "table": [[self.receiver_name, self.number]]},
                        {".": " \n \n "},
                        {"widths": column_layout, "style": "bold", "table": [new_headers]},
                        {"widths": column_layout, "style": "table", "table": new_line_items},
                        {".": " "},
                        {"widths": (5, 1), "style": "right", "table": new_totals},
                        {".": " \n \n \n \n \n \n \n \n \n \n \n \n "},
                        {".": self.footer, "style": {"text_align": "c"}},
                    ]
                }
            ],
        }

        with output_pdf.open("wb") as f:
            build_pdf(document, f)

        return output_pdf
