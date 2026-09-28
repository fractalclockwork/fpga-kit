import hil


class FakeSerial:
    def __init__(self, lines, pong="PONG,nexys3  ,00000010\n"):
        self.lines = [line.encode() for line in lines]
        self.pong = pong.encode()
        self.written = b""
        self.sent = False

    def readline(self):
        if not self.sent:
            if self.lines:
                return self.lines.pop(0)
            return b""
        self.sent = False
        return self.pong

    def write(self, data):
        self.written += data
        self.sent = True

    def close(self):
        return None


def test_ping_records_both_timestamps():
    port = FakeSerial(["HELLO,nexys3  ,0000000A\n"])
    records = hil.run_uart_hil(
        "fake",
        115200,
        "nexys3",
        "HELLO,nexys3",
        opener=lambda: port,
    )
    assert port.written == b"PING\n"
    assert records[0]["expected"] == "PONG"
    assert records[0]["fpga_cycles"] == 0x10
    assert records[0]["host_monotonic_ns"] > 0


def test_hil_logs_include_junit(tmp_path):
    records = [
        hil.hil_record("PING", "PONG", "PONG,nexys3  ,00000010", 0x10, 123)
    ]
    hil.write_hil_logs(tmp_path, records)
    assert (tmp_path / "hil.jsonl").read_text().startswith('{"sent": "PING"')
    xml = (tmp_path / "junit.xml").read_text()
    assert 'name="PONG"' in xml
    assert "failures=\"0\"" in xml
    hil.write_hil_logs(tmp_path, [], failures=["no PONG after PING"])
    failed = (tmp_path / "junit.xml").read_text()
    assert "failures=\"1\"" in failed
    assert "no PONG after PING" in failed


def test_cycle_count_must_move_forward():
    port = FakeSerial(["HELLO,nexys3  ,00000020\n"], pong="PONG,nexys3  ,00000001\n")
    try:
        hil.run_uart_hil("fake", 115200, "nexys3", "HELLO,nexys3", opener=lambda: port)
    except AssertionError as exc:
        assert "backwards" in str(exc)
    else:
        raise AssertionError("expected a backwards cycle count to fail")
