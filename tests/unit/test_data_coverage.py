from datetime import date

from spy_research.config import load_research_config
from spy_research.data.coverage import inventory
from spy_research.data.raw_store import RawBarStore


def test_holiday_weekend_missing_and_early_close(tmp_path):
    config = load_research_config()
    rows = inventory(config,RawBarStore(config,root=tmp_path),date(2026,11,26),date(2026,11,29))
    assert len(rows) == 1 and rows[0].session_date == date(2026,11,27)
    assert rows[0].raw_status == "MISSING" and rows[0].expected_minutes == 210


def test_corrupt_partition_is_invalid_not_valid_or_missing(tmp_path):
    config = load_research_config()
    store = RawBarStore(config,root=tmp_path)
    path = store.partition_path(date(2026,8,19))
    path.parent.mkdir(parents=True)
    path.write_bytes(b"corrupt fixture")
    row = inventory(config,store,date(2026,8,19),date(2026,8,19))[0]
    assert row.raw_status == "INVALID" and "CORRUPTED_PARTITION" in row.errors


def test_cli_coverage_does_not_load_credentials(tmp_path,monkeypatch,capsys):
    from spy_research.cli import main
    import spy_research.config as cfg
    monkeypatch.setattr(cfg,"load_settings",lambda *a,**k: (_ for _ in ()).throw(AssertionError("credentials")))
    assert main(["data-coverage","--start","2026-01-01","--end","2026-01-02","--raw-data-root",str(tmp_path),"--processed-data-root",str(tmp_path/"processed")]) == 2
    assert "validated=0" in capsys.readouterr().out
