# type: ignore[attr-defined]

import datetime
import logging
import os
import re
from xml.etree import ElementTree as ET

import httpx
from bs4 import BeautifulSoup

from .extra_data import CP_DELIVERED, NA, PUROLATOR_END, PUROLATOR_START


def cp(package_id: str) -> tuple[datetime.datetime, str, str, bool, str]:
    headers = {
        "Accept": "application/vnd.cpc.track-v2+xml",
        "Authorization": f"Basic {os.environ.get('CP_API_KEY')}",
        "Accept-language": "en-CA",
    }

    r = httpx.get(
        f"https://soa-gw.canadapost.ca/vis/track/pin/{package_id}/detail", headers=headers
    ).text

    r = r.replace('xmlns="http://www.canadapost.ca/ws/track-v2"', "")

    tree = ET.fromstring(r)
    root = tree.find("significant-events")[0]
    event_date = root.find("event-date").text
    event_time = root.find("event-time").text
    status = root.find("event-description").text
    event_id = int(root.find("event-identifier").text)
    city = root.find("event-site").text
    province = root.find("event-province").text
    date_object = datetime.datetime.strptime(
        event_date + event_time, "%Y-%m-%d%H:%M:%S"
    ).astimezone()

    is_delivered = event_id in CP_DELIVERED

    return (
        date_object,
        status,
        f"{city} {province}",
        is_delivered,
        "https://www.canadapost-postescanada.ca/track-reperage/en#/search?searchFor=",
    )


def ups(package_id: str) -> tuple[datetime.datetime, str, str, bool, str]:
    data = {"grant_type": "client_credentials"}

    r_auth = httpx.post(
        "https://onlinetools.ups.com/security/v1/oauth/token",
        data=data,
        auth=(os.environ.get("UPS_CLIENT_ID"), os.environ.get("UPS_CLIENT_SECRET")),
    ).json()

    headers = {
        "Authorization": "Bearer " + r_auth["access_token"],
        "transactionSrc": "python",
        "transId": "1",
    }

    r = httpx.get(
        "https://onlinetools.ups.com/api/track/v1/details/" + package_id,
        headers=headers,
    ).json()

    latest = r["trackResponse"]["shipment"][0]["package"][0]["activity"][0]

    location: dict = latest["location"]["address"]
    city = location.get("city", NA)
    province = location.get("stateProvince", "")
    country = location.get("country", NA)
    date_object = datetime.datetime.strptime(
        latest["date"] + latest["time"], "%Y%m%d%H%M%S"
    ).astimezone()
    status = latest["status"]["description"]
    code = latest["status"]["type"]

    is_delivered = code == "D"

    return (
        date_object,
        status,
        f"{city} {province}, {country}",
        is_delivered,
        "https://www.ups.com/track?loc=en_ca&tracknum=",
    )


def fedex(package_id: str) -> tuple[datetime.datetime, str, str, bool, str]:
    fedx_url = "https://apis.fedex.com"
    headers = {"content-type": "application/x-www-form-urlencoded"}

    data = {
        "grant_type": "client_credentials",
        "client_id": os.environ.get("FEDEX_CLIENT_ID"),
        "client_secret": os.environ.get("FEDEX_CLIENT_SECRET"),
    }
    r_auth = httpx.post(f"{fedx_url}/oauth/token", headers=headers, data=data).json()

    headers = {
        "content-type": "application/json",
        "authorization": "Bearer " + r_auth["access_token"],
    }

    data = {
        "includeDetailedScans": "True",
        "trackingInfo": [{"trackingNumberInfo": {"trackingNumber": package_id}}],
    }

    r = httpx.post(f"{fedx_url}/track/v1/trackingnumbers", headers=headers, json=data).json()

    scan = r["output"]["completeTrackResults"][0]["trackResults"][0]["scanEvents"][0]
    date_object = datetime.datetime.fromisoformat(scan["date"]).astimezone()
    code = scan["eventType"]
    status = scan["eventDescription"]
    location: dict = scan["scanLocation"]
    city = location.get("city", NA)
    province = location.get("stateOrProvinceCode", NA)
    country = location.get("countryCode", NA)

    is_delivered = code == "DL"

    return (
        date_object,
        status,
        f"{city} {province}, {country}",
        is_delivered,
        "https://www.fedex.com/fedextrack/?trknbr=",
    )


def purolator(package_id: str) -> tuple[datetime.datetime, str, str, bool, str]:
    data = PUROLATOR_START + package_id + PUROLATOR_END

    headers = {
        "Content-Type": "text/xml",
        "SOAPAction": "http://purolator.com/pws/service/v1/TrackPackagesByPin",
    }

    url = "https://webservices.purolator.com/EWS/V1/Tracking/TrackingService.asmx"
    r = httpx.post(
        url,
        auth=(os.environ.get("PUROLATOR_KEY"), os.environ.get("PUROLATOR_PASS")),
        headers=headers,
        data=data,
    ).text

    r_xml = BeautifulSoup(r, "xml")

    error_check = r_xml.find("Error")
    if error_check:
        if error_check.find("Code").text == "2300003":
            logging.info("No scanning details available")
        else:
            logging.info("unknown error: ")
        code = "Awaiting scan..."
        status = "Awaiting scan..."
        date_object = datetime.datetime(2020, 1, 1).astimezone()
        location = "NA"
    else:
        event = r_xml.find("Scan")
        code = event.find("ScanType").text
        status = event.find("Description").text
        datetime_raw = event.find("ScanDate").text + event.find("ScanTime").text
        date_object = datetime.datetime.strptime(datetime_raw, "%Y-%m-%d%H%M%S").astimezone()
        location = event.find("Depot").text

    is_delivered = code == "Delivery"

    return (
        date_object,
        status,
        location,
        is_delivered,
        "https://www.purolator.com/en/shipping/tracker?pin=",
    )


def dhl(package_id: str) -> tuple[datetime.datetime, str, str, bool, str]:
    headers = {"DHL-API-Key": os.environ.get("DHL_API_KEY", "")}
    query_string = {"trackingNumber": package_id}

    r = httpx.get(
        "https://api-eu.dhl.com/track/shipments", headers=headers, params=query_string
    ).json()
    rj = r["shipments"][0]["status"]

    status = rj["status"]
    date_object = datetime.datetime.fromisoformat(rj["timestamp"]).astimezone()
    location = rj["location"]["address"]["addressLocality"]

    is_delivered = status.lower() == "delivered"

    return (
        date_object,
        status,
        location,
        is_delivered,
        "https://www.dhl.com/ca-en/home/tracking/tracking-ecommerce.html?submit=1&tracking-id=",
    )


def canpar(package_id: str) -> tuple[datetime.datetime, str, str, bool, str]:
    data = {"barcode": package_id, "track_shipment": "false"}

    r = httpx.post("https://canship.canpar.com/api/CanparAddons/trackByBarcodeV2", json=data).json()
    rj = r["result"][0]
    event = rj["events"][0]
    city = event["address"]["city"]
    country = event["address"]["country"]
    status = event["code_description_en"]
    date_object = datetime.datetime.strptime(event["local_date_time"], "%Y%m%d %H%M%S").astimezone()
    is_delivered = rj["delivered"]

    return (
        date_object,
        status,
        f"{city} {country}",
        is_delivered,
        "https://www.canpar.com/en/tracking/track.htm?barcode=",
    )


def uniuni(package_id: str) -> tuple[datetime.datetime, str, str, bool, str]:
    params = {"id": package_id, "key": "SMq45nJhQuNR3WHsJA6N"}

    r = httpx.get("https://delivery-api.uniuni.ca/cargo/trackinguniuninew", params=params).json()

    location = status = date_object = ""
    is_delivered = False

    if r["status"] == "SUCCESS":
        rj = r["data"]["valid_tno"][0]["spath_list"][-1]
        location = rj["pathAddr"]
        status = rj["code"]
        try:
            date_object = datetime.datetime.fromisoformat(rj["dateTime"]["localTime"]).astimezone()
        except TypeError:
            try:
                raw = r["data"]["valid_tno"][0]["full_spath_info"]
                raw_date = re.match(r".+?\s(\d\d/\d\d/\d\d\s.+)", raw).group(1).upper()
                date_object = datetime.datetime.strptime(
                    raw_date, "%m/%d/%y %H:%M:%S:%p"
                ).astimezone()
            except TypeError:
                date_object = datetime.datetime(2020, 1, 1).astimezone()
        if "Delivered" in status:
            is_delivered = True

    return (date_object, status, location, is_delivered, "https://www.uniuni.com/tracking/?no=")


def aliexpress(package_id: str) -> tuple[datetime.datetime, str, str, bool, str]:
    r = httpx.get(
        f"https://global.cainiao.com/global/detail.json?mailNos={package_id}&lang=en-US"
    ).json()

    rj = r["module"][0]["latestTrace"]

    status = rj["desc"]
    date_object = datetime.datetime.fromisoformat(rj["timeStr"]).astimezone()
    is_delivered = "delivered" in status.lower()

    return (
        date_object,
        status,
        "N/A",
        is_delivered,
        "https://global.cainiao.com/newDetail.htm?mailNoList=",
    )


function_dict = {1: aliexpress, 2: canpar, 3: cp, 4: dhl, 5: fedex, 6: purolator, 7: uniuni, 8: ups}
