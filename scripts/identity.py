"""Parse Adept output and compare device type."""

import re


def normalize_idcode(value):
    text = str(value).strip().lower()
    if text.startswith("0x"):
        text = text[2:]
    return text


def idcode_match(found, expected):
    mask = 0x0FFFFFFF
    return (int(normalize_idcode(found), 16) & mask) == (int(normalize_idcode(expected), 16) & mask)


def parse_enum(text):
    devices = []
    current = None
    for line in text.splitlines():
        match = re.match(r"\s*Device:\s+(\S+)", line)
        if match and "Transport" not in line and "ID" not in line:
            current = {"name": match.group(1)}
            devices.append(current)
            continue
        if current is None:
            continue
        product = re.match(r"\s*Product Name:\s+(.+)", line)
        if product:
            current["product"] = product.group(1).strip()
        serial = re.match(r"\s*Serial Number:\s+(\S+)", line)
        if serial:
            current["serial"] = serial.group(1)
    return devices


def parse_init(text):
    ids = [normalize_idcode(item) for item in re.findall(r"Found Device ID:\s*([0-9A-Fa-fx]+)", text)]
    names = re.findall(r"Device\s+(\d+):\s+(\S+)", text)
    # ID lines are shift order, TDO end first. Device 0 is the TDI end.
    ordered = list(reversed(ids)) if names else list(ids)
    chain = []
    for index, name in names:
        entry = {"index": int(index), "name": name}
        if int(index) < len(ordered):
            entry["idcode"] = ordered[int(index)]
        chain.append(entry)
    if not chain and ids:
        chain = [{"index": i, "name": "", "idcode": code} for i, code in enumerate(ids)]
    return chain


def chain_has_idcode(chain, expected):
    for device in chain:
        if "idcode" in device and idcode_match(device["idcode"], expected):
            return device
    return None
