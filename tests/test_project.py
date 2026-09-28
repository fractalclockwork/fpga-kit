from project import prepare_run


def test_nexys_project_names_the_part(tmp_path):
    run = prepare_run("nexys3", tmp_path)
    text = (run / "project.xst").read_text()
    assert "xc6slx16-3csg324" in text
    assert "heartbeat_top" in text
    assert (run / "project.ucf").read_text().startswith('NET "clk"')
