from app.db import connect

def list_papers():
    c = connect()
    try:
        return [dict(r) for r in c.execute("SELECT * FROM papers ORDER BY id").fetchall()]
    finally:
        c.close()

def get_paper(pid):
    c = connect()
    try:
        r = c.execute("SELECT * FROM papers WHERE id=?", (pid,)).fetchone()
        return dict(r) if r else None
    finally:
        c.close()

def update_paper(pid, roll_width, stock_len):
    """只改标称: update nominal roll specs; stored runs are never touched."""
    c = connect()
    try:
        cur = c.execute(
            "UPDATE papers SET roll_width=?, stock_len=? WHERE id=?",
            (float(roll_width), float(stock_len), pid),
        )
        c.commit()
        return cur.rowcount > 0
    finally:
        c.close()
