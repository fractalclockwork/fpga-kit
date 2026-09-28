import pytest

from boards import load_board, read_stages
from identity import idcode_match, parse_enum, parse_init
from stage import gate, present_adept_chain, present_nexys


ENUM = """
Found 1 device(s)

Device: Nexys3
    Device Transport Type: 00020001 (USB)
    Product Name:          Nexys3
    Serial Number:         ABC
"""

INIT = """
Initializing scan chain...
Found Device ID: 24002093
Found 1 device(s):
Device 0: XC6SLX16
"""


def test_idcode_ignores_revision():
    assert idcode_match("24002093", "04002093")
    assert not idcode_match("04001093", "04002093")


def test_parse_enum_and_init():
    devices = parse_enum(ENUM)
    assert devices[0]["name"] == "Nexys3"
    chain = parse_init(INIT)
    assert chain[0]["idcode"] == "24002093"
    assert chain[0]["name"] == "XC6SLX16"


def test_nexys_present_pass(tmp_path, monkeypatch):
    monkeypatch.setattr("boards.stage_path", lambda board: tmp_path / board / "stage.json")
    code = present_nexys(load_board("nexys3"), ENUM, INIT)
    assert code == 0


def test_nexys_rejects_other_cable(tmp_path, monkeypatch):
    monkeypatch.setattr("boards.stage_path", lambda board: tmp_path / board / "stage.json")
    other = ENUM.replace("Nexys3", "JtagHs2")
    code = present_nexys(load_board("nexys3"), other, INIT)
    assert code == 1


def test_nexys_accepts_smt2_when_selected(tmp_path, monkeypatch):
    monkeypatch.setattr("boards.stage_path", lambda board: tmp_path / board / "stage.json")
    monkeypatch.setenv("ADEPT_DEVICE", "JtagSmt2")
    enum = ENUM.replace("Nexys3", "JtagSmt2")
    code = present_nexys(load_board("nexys3"), enum, INIT)
    assert code == 0
    record = read_stages("nexys3")["stages"]["present"]
    assert record["device"] == "JtagSmt2"


def test_smt2_workflow_path(tmp_path, monkeypatch):
    from stage import ready_jtag_paths

    board = load_board("nexys3")
    assert ready_jtag_paths(board, "Nexys3") == ["jtag"]
    assert ready_jtag_paths(board, "JtagSmt2") == ["jtag-smt2"]


def test_spartan3_accepts_cable_when_idcode_matches(tmp_path, monkeypatch):
    monkeypatch.setattr("boards.stage_path", lambda board: tmp_path / board / "stage.json")
    enum = "Device: JtagHs2\n    Product Name: Digilent JTAG-HS2\n"
    init = "Found Device ID: 05045093\nFound Device ID: 01414093\nDevice 0: XC3S200\nDevice 1: XCF02S\n"
    code = present_adept_chain(load_board("spartan3"), enum, init, "")
    assert code == 0


def test_later_board_stays_closed_until_nexys_image_passes(tmp_path, monkeypatch):
    monkeypatch.setattr("boards.stage_path", lambda board: tmp_path / board / "stage.json")
    with pytest.raises(SystemExit, match="nexys3 image stage has not passed"):
        gate("spartan3e", "present")


def test_init_pairs_idcodes_from_tdo_end():
    text = """
Found Device ID: 06e5e093
Found Device ID: 05046093
Found Device ID: 01c22093
Found 3 device(s):
    Device 0: XC3S500E
    Device 1: XCF04S
    Device 2: XC2C64A
"""
    chain = parse_init(text)
    assert [(item["name"], item["idcode"]) for item in chain] == [
        ("XC3S500E", "01c22093"),
        ("XCF04S", "05046093"),
        ("XC2C64A", "06e5e093"),
    ]


def test_spartan3e_records_onboard_xilinx_without_adept(tmp_path, monkeypatch):
    monkeypatch.setattr("boards.stage_path", lambda board: tmp_path / board / "stage.json")
    code = present_adept_chain(load_board("spartan3e"), "Found 0 device(s)\n", "", "Bus 001 Device 004: ID 03fd:0008")
    assert code == 0
