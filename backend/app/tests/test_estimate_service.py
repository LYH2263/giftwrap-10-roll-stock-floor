import os
import tempfile

os.environ["DATA_DIR"] = tempfile.mkdtemp(prefix="giftwrap-test-")

import pytest
from fastapi import HTTPException

from app import seed
from app.db import connect
from app.engines.wrap_math import order_meters, sheet_length
from app.repositories import history, papers
from app.services import estimate_service


@pytest.fixture(autouse=True)
def fresh_db():
    seed.init_db()
    c = connect()
    for t in ("calc_runs", "boxes", "papers", "settings"):
        c.execute(f"DELETE FROM {t}")
    c.commit()
    c.close()
    seed.init_db()
    yield


def first_paper():
    return papers.list_papers()[0]


def test_preview_returns_stock_fields_without_row():
    p = first_paper()
    r = estimate_service.run_estimate(1, p["id"], None, "cross", False, "")
    assert r["run_id"] is None
    assert r["sheet_len"] == sheet_length(r["paper_m2"], p["roll_width"])
    assert r["stock_len"] == p["stock_len"]
    assert r["order_m"] == order_meters(r["sheet_len"], p["stock_len"])
    assert history.list_runs() == []


def test_save_pins_stock_fields_and_list_matches_detail():
    p = first_paper()
    r = estimate_service.run_estimate(1, p["id"], None, "cross", True, "")
    assert r["run_id"]
    listed = history.list_runs()
    assert len(listed) == 1
    detail = history.get_run(r["run_id"])
    assert detail is not None
    for view in (listed[0]["result"], detail["result"]):
        assert view["order_m"] == r["order_m"]
        assert view["sheet_len"] == r["sheet_len"]
        assert view["stock_len"] == r["stock_len"]


def test_missing_paper_fails_without_row():
    with pytest.raises(HTTPException):
        estimate_service.run_estimate(1, None, None, "cross", True, "")
    with pytest.raises(HTTPException):
        estimate_service.run_estimate(1, 9999, None, "cross", True, "")
    assert history.list_runs() == []


def test_nonpositive_roll_width_fails_without_row():
    p = first_paper()
    papers.update_paper(p["id"], 0, 50.0)
    with pytest.raises(HTTPException):
        estimate_service.run_estimate(1, p["id"], None, "cross", True, "")
    assert history.list_runs() == []


def test_nonpositive_stock_len_fails_without_row():
    p = first_paper()
    papers.update_paper(p["id"], 1.0, 0)
    with pytest.raises(HTTPException):
        estimate_service.run_estimate(1, p["id"], None, "cross", True, "")
    assert history.list_runs() == []


def test_missing_stock_len_fails_without_row():
    p = first_paper()
    c = connect()
    c.execute("UPDATE papers SET stock_len=NULL WHERE id=?", (p["id"],))
    c.commit()
    c.close()
    with pytest.raises(HTTPException):
        estimate_service.run_estimate(1, p["id"], None, "cross", True, "")
    assert history.list_runs() == []


def test_whole_roll_roundup_end_to_end():
    p = first_paper()
    papers.update_paper(p["id"], 0.7, 0.2)
    r = estimate_service.run_estimate(1, p["id"], None, "cross", False, "")
    assert r["sheet_len"] == 0.443
    assert r["order_m"] == 0.6


def test_dry_run_with_write_time_params_matches_saved_run():
    p = first_paper()
    saved = estimate_service.run_estimate(1, p["id"], None, "cross", True, "")
    again = estimate_service.run_estimate(1, p["id"], None, "cross", False, "")
    assert again["order_m"] == saved["order_m"]
    assert again["sheet_len"] == saved["sheet_len"]


def test_nominal_edit_keeps_history_pinned_and_new_orders_use_new_specs():
    p = first_paper()
    saved = estimate_service.run_estimate(1, p["id"], None, "cross", True, "")
    papers.update_paper(p["id"], p["roll_width"], 0.2)
    detail = history.get_run(saved["run_id"])
    assert detail["result"]["order_m"] == saved["order_m"]
    assert detail["result"]["stock_len"] == saved["stock_len"]
    listed = history.list_runs()[0]
    assert listed["result"]["order_m"] == detail["result"]["order_m"]
    fresh = estimate_service.run_estimate(1, p["id"], None, "cross", False, "")
    assert fresh["stock_len"] == 0.2
    assert fresh["order_m"] == order_meters(fresh["sheet_len"], 0.2)
    assert fresh["order_m"] != saved["order_m"]
