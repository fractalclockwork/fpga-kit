from pathlib import Path

from parse_ise_reports import build_report


SRP = """
Number of Slices:                      12 out of 2278
Number of Slice Registers:             10
Number of Slice LUTs:                  20
Number of bonded IOBs:                 3
Total REAL time to Xst completion: 4 secs
"""

SRP_S3 = """
Number of 4 input LUTs:               8
Number of Slice Flip Flops:           7
Total REAL time to Xst completion: 3 secs
"""

PAR = """
Total REAL time to Placer completion: 2 secs
Total REAL time to Router completion: 9 secs
Total REAL time to PAR completion: 12 secs
Timing Score: 0
"""

TWR = "All constraints were met.\n"


def test_parser_covers_both_families(tmp_path: Path):
    srp = tmp_path / "a.srp"
    par = tmp_path / "a.par"
    twr = tmp_path / "a.twr"
    srp.write_text(SRP)
    par.write_text(PAR)
    twr.write_text(TWR)
    report = build_report(str(srp), str(par), str(twr))
    assert report["synthesis_metrics"]["utilization"]["luts_used"] == 20
    assert report["synthesis_metrics"]["utilization"]["slice_registers_used"] == 10
    assert report["place_and_route_metrics"]["router_time"] == "9 secs"
    assert report["timing_ok"] is True

    srp.write_text(SRP_S3)
    older = build_report(str(srp), str(par), str(twr))
    assert older["synthesis_metrics"]["utilization"]["luts_used"] == 8
    assert older["synthesis_metrics"]["utilization"]["slice_registers_used"] == 7


def test_nonzero_score_fails(tmp_path: Path):
    srp = tmp_path / "a.srp"
    par = tmp_path / "a.par"
    srp.write_text(SRP)
    par.write_text(PAR.replace("Timing Score: 0", "Timing Score: 12"))
    report = build_report(str(srp), str(par), None)
    assert report["timing_ok"] is False
