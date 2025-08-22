
from dataclasses import dataclass, field
from typing import List, Optional
from table import generate_menu_table

@dataclass
class MenuItem:
    """
    Represents a single menu item.
    """
    category: str
    main: Optional[str] = None
    sides: List[str] = field(default_factory=list)
    price: Optional[str] = None
    is_available: bool = True

@dataclass
class Menu:
    """
    Represents a menu for a specific date.
    """
    date: str
    items: List[MenuItem] = field(default_factory=list)

    def add_item(self, item: MenuItem) -> None:
        self.items.append(item)

    def get_items(self) -> List[MenuItem]:
        return self.items

    def __str__(self) -> str:
        lines = []
        for item in self.items:
            lines.append(f"Category: {item.category}")
            if item.is_available:
                main = item.main if item.main else "-"
                sides = ', '.join(item.sides) if item.sides else "-"
                price = item.price if item.price else "-"
                lines.append(f"Main: {main}")
                lines.append(f"Sides: {sides}")
                lines.append(f"Price: {price}")
            else:
                lines.append("This item is not available today.")
            lines.append("-" * 20)
        return "\n".join(lines)

    def show(self, use_color: bool = True, max_width: Optional[int] = None) -> None:
        """
        Print the menu as an ASCII table.
        """
        title = f"Menu for {self.date}:"
        menu_str = generate_menu_table(title, self.items, use_color=use_color, max_width=max_width)
        print(menu_str)