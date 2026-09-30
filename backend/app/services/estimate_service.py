from fastapi import HTTPException
from app.engines.wrap_math import order_meters, paper_area, ribbon_estimate, sheet_length
from app.repositories import boxes, history, papers, settings_repo

def run_estimate(box_id: int, paper_id: int | None, overlap: float | None, wrap_style: str, save: bool, note: str):
    box = boxes.get_box(box_id)
    if not box:
        raise HTTPException(404)
    if box.get("data_quality") == "dirty":
        raise HTTPException(422, "dirty box")
    paper = papers.get_paper(paper_id) if paper_id else None
    if not paper:
        raise HTTPException(422, "paper roll required")
    roll_width = paper.get("roll_width")
    if roll_width is None or float(roll_width) <= 0:
        raise HTTPException(422, "roll width must be positive")
    stock_len = paper.get("stock_len")
    if stock_len is None or float(stock_len) <= 0:
        raise HTTPException(422, "stock length must be positive")
    ov = float(overlap) if overlap is not None else settings_repo.get_overlap()
    calc = paper_area(box["length"], box["width"], box["height"], ov)
    ribbon = ribbon_estimate(box["length"], box["width"], box["height"], wrap_style)
    sheet = sheet_length(calc["paper_m2"], roll_width)
    order = order_meters(sheet, stock_len)
    stock = {
        "paper_id": paper["id"],
        "paper_name": paper["name"],
        "roll_width": float(roll_width),
        "sheet_len": sheet,
        "stock_len": float(stock_len),
        "order_m": order,
    }
    payload = {**calc, **stock, "ribbon": ribbon, "box_id": box_id}
    run_id = history.insert_run(box_id, ov, payload, note) if save else None
    return {"box": box, "paper": paper, "run_id": run_id, **calc, **stock, "ribbon": ribbon}
