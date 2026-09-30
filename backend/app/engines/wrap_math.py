import math


def paper_area(length: float, width: float, height: float, overlap: float = 1.15) -> dict:
    L, W, H = float(length), float(width), float(height)
    if min(L, W, H) <= 0:
        raise ValueError("box dimensions must be positive")
    base = 2 * (L * W + L * H + W * H)
    need = base * float(overlap)
    return {"box_surface": round(base, 3), "overlap": float(overlap), "paper_m2": round(need, 3)}


def ribbon_estimate(length: float, width: float, height: float, wrap_style: str = "cross") -> dict:
    """Helper: approximate ribbon length in meters (not stored as primary metric)."""
    L, W, H = float(length), float(width), float(height)
    girth = 2 * (W + H)
    if wrap_style == "band":
        meters = girth + 0.3
    else:
        meters = girth * 2 + L + 0.5
    return {"wrap_style": wrap_style, "ribbon_m": round(meters, 2)}


def sheet_length(paper_m2: float, roll_width: float) -> float:
    """下料长: cutting length (m) folded out of the roll width for a given area."""
    area = float(paper_m2)
    width = float(roll_width)
    if area <= 0:
        raise ValueError("paper area must be positive")
    if width <= 0:
        raise ValueError("roll width must be positive")
    return round(area / width, 3)


def order_meters(sheet_len: float, stock_len: float) -> float:
    """订货米托底: one roll covers the cutting length -> order the cutting length;
    otherwise round up to a whole-roll multiple of the nominal roll length."""
    sheet = float(sheet_len)
    stock = float(stock_len)
    if sheet <= 0:
        raise ValueError("sheet length must be positive")
    if stock <= 0:
        raise ValueError("stock length must be positive")
    if sheet <= stock:
        return round(sheet, 3)
    rolls = math.ceil(sheet / stock - 1e-9)
    return round(rolls * stock, 3)
