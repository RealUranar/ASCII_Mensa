
from get_data import GetMenuHTML
from menu import Menu, MenuItem
from get_data import GetMenuHTML

def find_area_in_html(data: str, start: str, end: str) -> str:
    """
    Extracts a substring from data between the first occurrence of start and end.
    Returns an empty string if not found.
    """
    start_index = data.find(start)
    if start_index == -1:
        return ""
    end_index = data.find(end, start_index)
    if end_index == -1:
        return ""
    return data[start_index + len(start):end_index].strip()


def parse_menu_html(html: str) -> Menu:
    """
    Parses the HTML content and returns a Menu object for the current day.
    """
    current_day = find_area_in_html(html, '<h3 class="active-headline">', '<div class="preventBreak">')
    date_area = find_area_in_html(current_day, '<a', '</a>')
    try:
        date = date_area.split('">')[1].split('</a>')[0]
    except IndexError:
        date = "Unknown Date"

    menu_table = find_area_in_html(current_day, '<table class="menues">', '</table>')
    menu_rows = []
    temp_table = menu_table
    while True:
        start = temp_table.find('<tr')
        end = temp_table.find('</tr>', start)
        if start == -1 or end == -1:
            break
        row_html = temp_table[start:end]
        menu_rows.append(row_html)
        temp_table = temp_table[end:]

    menu = Menu(date)
    for row_html in menu_rows:
        category = find_area_in_html(row_html, 'class="menue-item menue-category">', '</span>')
        menu_item = MenuItem(category=category)

        content_area = find_area_in_html(row_html, f'<span class="menue-nutr">+</span>', '<div class="nutr-info">')
        content_parts = [part.split("<sup>")[0].strip() for part in content_area.split("|")]
        if content_parts and "closed" in content_parts[0].lower():
            menu_item.is_available = False
            menu_item.main = "Closed"
            menu_item.price = "-"
        elif content_parts:
            menu_item.main = content_parts[0]
            for side in content_parts[1:]:
                if side:
                    menu_item.sides.append(side.strip())
            price = find_area_in_html(row_html, 'menue-item menue-price large-price">', '</span>')
            menu_item.price = price
        menu.add_item(menu_item)
    return menu


def main():
    """
    Main entry point: fetches menu HTML, parses it, and displays the menu.
    """
    url = 'https://www.studierendenwerk-aachen.de/speiseplaene/academica-w-en.html'
    html_menu = GetMenuHTML(url)
    web_content = html_menu.fetch_data()
    menu = parse_menu_html(web_content)
    menu.show()


if __name__ == "__main__":
    main()