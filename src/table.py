
import shutil
import textwrap
from typing import List, Optional, Any

class AnsiColors:
    HEADER_BG = "\x1b[1m\x1b[34m"
    RESET = "\x1b[0m"
    CAT = "\x1b[33m"       # yellow
    PRICE = "\x1b[32m"     # green
    BAD = "\x1b[31m"       # red
    DIM = "\x1b[2m"

def generate_menu_table(
    title: str,
    items: List[Any],
    use_color: bool = True,
    max_width: Optional[int] = None,
    category_label: str = "Category",
    main_label: str = "Main",
    sides_label: str = "Sides",
    price_label: str = "Price",
) -> str:
    """
    Build a compact ASCII table (optionally colored with ANSI codes).
    """
    class NoColor:
        HEADER_BG = ""
        RESET = ""
        CAT = ""
        PRICE = ""
        BAD = ""
        DIM = ""
    colors = AnsiColors if use_color else NoColor

    # Layout configuration
    if max_width is None:
        try:
            max_width = shutil.get_terminal_size().columns
        except Exception:
            max_width = 100
    max_width = max(72, min(140, max_width))

    col_min = { "category": 12, "main": 16, "sides": 16, "price": 8 }
    col_weight = { "category": 1.0, "main": 1.4, "sides": 1.2, "price": 0.6 }

    vbar = "|"
    hbar = "-"
    corner = "+"
    cell_pad = 1
    total_inner_vbars = 4

    def _normalize_sides(s):
        if s is None:
            return "-"
        if isinstance(s, (list, tuple)):
            s = ", ".join(map(str, s))
        s = str(s).strip()
        return s if s else "-"

    # Prepare content rows
    content_rows = []
    for it in items:
        cat = getattr(it, 'category', '-')
        price = getattr(it, 'price', '-') or "-"
        is_available = getattr(it, 'is_available', True)
        if not is_available:
            main = "Not available today"
            sides = "-"
        else:
            main = getattr(it, 'main', '-')
            sides = _normalize_sides(getattr(it, 'sides', '-'))
        content_rows.append((cat, main, sides, price))

    labels = (category_label, main_label, sides_label, price_label)
    def longest(col_idx, seq):
        return max(len(s.split("\n")[0]) if isinstance(s, str) else len(str(s)) for s in seq)

    col_data = list(zip(*([labels] + content_rows)))
    base_widths = [
        max(col_min["category"], longest(0, col_data[0])),
        max(col_min["main"],     longest(1, col_data[1])),
        max(col_min["sides"],    longest(2, col_data[2])),
        max(col_min["price"],    longest(3, col_data[3])),
    ]

    fixed_nontext = total_inner_vbars + 2 + (cell_pad * 2 * 4)
    current_total = sum(base_widths) + fixed_nontext
    if max_width is not None and current_total < max_width:
        extra = max_width - current_total
        weights = [col_weight["category"], col_weight["main"], col_weight["sides"], col_weight["price"]]
        wsum = sum(weights)
        for i in range(4):
            add = int(round(extra * (weights[i] / wsum)))
            base_widths[i] += add
        overshoot = (sum(base_widths) + fixed_nontext) - max_width
        for i in range(4):
            if overshoot <= 0:
                break
            take = min(overshoot, 1)
            base_widths[i] -= take
            overshoot -= take

    cat_w, main_w, sides_w, price_w = base_widths

    def wrap_cell(s, width):
        s = "" if s is None else str(s)
        if not s:
            return [""]
        # Wrap without breaking words; keep long tokens intact if needed
        return textwrap.wrap(s, width=width, break_long_words=False, break_on_hyphens=True) or [""]

    def paint_cell(text, colname, unavailable=False):
        if unavailable and colname == "main":
            return f"{colors.BAD}{text}{colors.RESET}"
        if colname == "category":
            return f"{colors.CAT}{text}{colors.RESET}"
        if colname == "price":
            # leave '-' uncolored
            return f"{colors.PRICE}{text}{colors.RESET}" if text.strip() != "-" else text
        return text

    def make_rule(char="-"):
        return corner + char * (cat_w + 2*cell_pad) + corner + \
               char * (main_w + 2*cell_pad) + corner + \
               char * (sides_w + 2*cell_pad) + corner + \
               char * (price_w + 2*cell_pad) + corner

    def make_header_bar(text):
        bar = make_rule("-")
        inner = vbar + " " * (cat_w + 2*cell_pad) + vbar + " " * (main_w + 2*cell_pad) + \
                vbar + " " * (sides_w + 2*cell_pad) + vbar + " " * (price_w + 2*cell_pad) + vbar
        # Center title across full width (between leftmost and rightmost corners)
        full_width = len(bar) - 2
        centered = text.center(full_width)
        if use_color:
            return f"{colors.HEADER_BG}{bar}{colors.RESET}\n{colors.HEADER_BG}|{centered}|{colors.RESET}\n{colors.HEADER_BG}{bar}{colors.RESET}"
        else:
            return f"{bar}\n|{centered}|\n{bar}"

    # ---------- Build table ----------
    out = []

    # Title bar
    out.append(make_header_bar(title))

    # Header row
    out.append(
        vbar
        + " " * cell_pad + f"{category_label:<{cat_w}}" + " " * cell_pad + vbar
        + " " * cell_pad + f"{main_label:<{main_w}}"     + " " * cell_pad + vbar
        + " " * cell_pad + f"{sides_label:<{sides_w}}"   + " " * cell_pad + vbar
        + " " * cell_pad + f"{price_label:<{price_w}}"   + " " * cell_pad + vbar
    )
    out.append(make_rule(hbar))

    # Data rows
    for (cat, main, sides, price) in content_rows:
        unavailable = (main == "Not available today")
        # Wrap each cell to its column width
        cat_lines  = wrap_cell(cat,   cat_w)
        main_lines = wrap_cell(main,  main_w)
        sides_lines= wrap_cell(sides, sides_w)
        price_lines= wrap_cell(price, price_w)
        height = max(len(cat_lines), len(main_lines), len(sides_lines), len(price_lines))

        # Pad lists to equal height
        def pad(lines, h): return lines + [""] * (h - len(lines))
        cat_lines, main_lines, sides_lines, price_lines = (
            pad(cat_lines, height), pad(main_lines, height), pad(sides_lines, height), pad(price_lines, height)
        )

        # Emit physical rows
        for i in range(height):
            cat_txt   = paint_cell(f"{cat_lines[i]:<{cat_w}}",   "category", unavailable)
            main_txt  = paint_cell(f"{main_lines[i]:<{main_w}}", "main",     unavailable)
            sides_txt = paint_cell(f"{sides_lines[i]:<{sides_w}}","sides",    unavailable)
            price_txt = paint_cell(f"{price_lines[i]:<{price_w}}","price",    unavailable)

            out.append(
                vbar
                + " " * cell_pad + cat_txt   + " " * cell_pad + vbar
                + " " * cell_pad + main_txt  + " " * cell_pad + vbar
                + " " * cell_pad + sides_txt + " " * cell_pad + vbar
                + " " * cell_pad + price_txt + " " * cell_pad + vbar
            )
        out.append(make_rule(hbar))

    return "\n".join(out)


# ---------------- Example usage with your data ----------------
if __name__ == "__main__":
    menu_title = "Menu for Friday, 22.08.2025"
    menu_items = [
        {"category": "Vegetarian", "main": "Chick peas spinach curry", "sides": "Sweet potato cubes", "price": "2,20 €"},
        {"category": "Classics", "main": "Fish bake \"Italiano\"", "sides": "Mustard sauce", "price": "2,80 €"},
        {"category": "Express", "main": None, "sides": None, "price": None},  # Not available
        {"category": "Burger Classics", "main": "Veggie burger", "sides": "French fries, Soft drink 0,33 L", "price": "5,10 €"},
        {"category": "Burger of the week", "main": "Chicken burger", "sides": "French fries, Soft drink 0,33 L", "price": "5,10 €"},
    ]

    print(generate_menu_table(menu_title, menu_items, use_color=True))
