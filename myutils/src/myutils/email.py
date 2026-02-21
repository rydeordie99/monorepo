import base64
import logging
import mimetypes
import os
import pathlib
import quopri
import smtplib
import string
from email import message_from_string
from email.header import decode_header
from email.message import EmailMessage
from email.utils import formatdate, make_msgid, parseaddr
from io import BytesIO

import html2text


def send_email(
    fr: str,
    subject: str = "no subject",
    html: str = "empty body",
    to: str = os.environ.get("EMAIL_TO_DEFAULT", ""),
    cc: str = "",
    *,
    bcc: str = "",
    attachment: pathlib.Path | list[pathlib.Path] | None = None,
    image: pathlib.Path | bytes | None = None,
    fr_email: str = os.environ.get("EMAIL_FROM_DEFAULT", ""),
    smtp_server: str = os.environ.get("SMTP_SERVER", ""),
    login: str = os.environ.get("SMTP_USER", ""),
    password: str = os.environ.get("SMTP_PASS", ""),
) -> None:
    text = html2text.html2text(html)

    # cleanup subject to remove new lines (leads to errors)
    subject = subject.replace("\n", "")

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = f"{fr} <{fr_email}>"
    msg["To"] = to
    msg["Date"] = formatdate(localtime=True)
    msg["Message-ID"] = make_msgid()

    if cc:
        msg["Cc"] = cc
    if bcc:
        msg["Bcc"] = bcc

    msg.set_content(text)
    msg.add_alternative(html, subtype="html")

    if image:
        type_main, type_sub = "image", "png"
        if isinstance(image, pathlib.Path):
            guess_mime = mimetypes.guess_type(image)[0]
            if guess_mime is not None:
                type_main, type_sub = guess_mime.split("/")
            with image.open("rb") as f:
                image = f.read()

        msg.get_payload()[1].add_related(  # type: ignore
            image, maintype=type_main, subtype=type_sub, cid="<image_cid>"
        )

    if attachment:
        if isinstance(attachment, pathlib.Path):
            attachment = [attachment]
        for one_file in attachment:
            type_main, type_sub = "application", "octet-stream"
            guess_mime = mimetypes.guess_type(one_file)[0]
            if guess_mime is not None:
                type_main, type_sub = guess_mime.split("/")
            with one_file.open("rb") as f:
                msg.add_attachment(
                    f.read(), maintype=type_main, subtype=type_sub, filename=one_file.name
                )

    with smtplib.SMTP(smtp_server, 587) as server:
        server.starttls()
        server.login(login, password)
        server.send_message(msg)

    logging.info("Email sent!: %s", subject)


def parse_mail(raw_message: str) -> dict:
    message = message_from_string(raw_message)
    text_plain = text_html = attachment = None

    for part in message.walk():
        content_disposition = part.get("Content-Disposition")
        content_type = part.get_content_type()
        content_transfer_encoding = part.get("Content-Transfer-Encoding", "")
        if content_type == "text/plain" and text_plain is None:
            text_plain = part.get_payload()
        if content_type == "text/html" and text_html is None:
            text_html_raw = part.get_payload()
            printable = set(string.printable)
            text_html_ascii = "".join(filter(lambda x: x in printable, text_html_raw))
            text_html = str(quopri.decodestring(text_html_ascii)).replace("\n", "")[2:-1]
            if content_transfer_encoding == "base64":
                text_html = base64.b64decode(text_html_raw + b"===").decode("utf-8")  # type: ignore
        if content_disposition is not None and content_disposition.startswith("attachment"):
            content_content = part.get_payload(decode=True)
            attachment = BytesIO(content_content)  # type: ignore
            attachment.name = part.get_filename()

    decoded_subject = decode_header(message.get("Subject", ""))
    subject = decoded_subject[0][0]
    encoding = decoded_subject[0][1]
    if encoding is not None:
        subject = subject.decode(encoding)

    return {
        "to": parseaddr(message.get("To", ""))[1],
        "from": parseaddr(message.get("From", ""))[1],
        "subject": subject,
        "text_plain": text_plain,
        "text_html": text_html,
        "attachment": attachment,
    }
