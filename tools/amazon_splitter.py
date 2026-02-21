import datetime
import logging
import re
from decimal import Decimal
from pathlib import Path

import pdfplumber
from myutils.config import Setup
from myutils.date_util import today
from PyPDF2 import PdfReader, PdfWriter

s = Setup("amazon_splitter")

pdf_files = list(Path("./").resolve().glob("./*.pdf"))

date_re = re.compile(r"Invoice date.+?:(.+)")
total_re = re.compile(r"Total \$(.+?)\s\$")
invoice_date = today

for pdf_file in pdf_files:
    logging.info("Processing pdf: %s", pdf_file.stem)
    with pdfplumber.open(pdf_file) as pdf:
        page_cuts = []
        totals = []
        total_flag = False
        for page in pdf.pages:
            lines = page.extract_text().splitlines()

            for line in lines:
                if line.startswith("Invoice date"):
                    date_search = date_re.search(line)
                    if not date_search:
                        raise ReferenceError
                    invoice_date = datetime.datetime.strptime(
                        date_search.group(1).strip(), "%d %B %Y"
                    ).astimezone()

                if total_flag:
                    totals.append(Decimal(line.removeprefix("$")))
                    total_flag = False

                if line.startswith("Invoice subtotal"):
                    if "$" in line:
                        totals.append(Decimal(line.split("$")[-1].strip()))
                    else:
                        total_flag = True

                if line.startswith("Total $"):
                    page_cuts.append(page.page_number)

    total = sum(totals)

    reader = PdfReader(pdf_file)
    writer = PdfWriter()

    for page_num, page in enumerate(reader.pages, start=1):
        writer.add_page(page)
        if page_num == page_cuts[0]:
            page_cuts.pop(0)

            with Path(f"{invoice_date:%Y%m%d}_{total}_{pdf_file.stem}_{page_num}.pdf").open(
                "wb"
            ) as f:
                writer.write(f)
            if len(page_cuts) > 0:
                writer = PdfWriter()

    pdf_file.unlink()
