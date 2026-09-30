import pytest
from app.engines.wrap_math import order_meters, paper_area, ribbon_estimate, sheet_length

def test_book_box():
    r = paper_area(0.30, 0.20, 0.15, 1.15)
    assert r["box_surface"] == 0.27
    assert r["paper_m2"] == 0.31

def test_ribbon_cross():
    rb = ribbon_estimate(0.30, 0.20, 0.15, "cross")
    assert rb["ribbon_m"] > 0.5

def test_sheet_length_folds_roll_width():
    assert sheet_length(0.31, 1.0) == 0.31
    assert sheet_length(0.31, 0.7) == 0.443

def test_sheet_length_rejects_nonpositive_roll_width():
    with pytest.raises(ValueError):
        sheet_length(0.31, 0)
    with pytest.raises(ValueError):
        sheet_length(0.31, -0.5)

def test_order_fits_one_roll_takes_sheet_len():
    assert order_meters(0.31, 50.0) == 0.31
    assert order_meters(0.5, 0.5) == 0.5

def test_order_rounds_up_to_whole_roll_multiple():
    assert order_meters(1.2, 0.5) == 1.5
    assert order_meters(0.443, 0.2) == 0.6

def test_order_exact_multiple_not_rounded_further():
    assert order_meters(1.0, 0.5) == 1.0
    assert order_meters(0.6, 0.2) == 0.6

def test_order_rejects_nonpositive_inputs():
    with pytest.raises(ValueError):
        order_meters(0.3, 0)
    with pytest.raises(ValueError):
        order_meters(0.3, -1.0)
    with pytest.raises(ValueError):
        order_meters(0, 1.0)
