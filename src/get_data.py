
import urllib.request
import os
import time
from typing import Optional, Union

class GetMenuHTML:
    """
    Handles fetching and caching the menu HTML from a URL, with local file caching.
    """
    CACHE_FILE = os.path.join(os.path.dirname(__file__), "todays_menu.txt")
    CACHE_HOURS = 8

    def __init__(self, url: str):
        self.url: str = url
        self.web_content: Optional[str] = None
        self.fetch_data()

    def request_data_from_web(self) -> Union[str, None]:
        """Fetch data from the web and update the cache file."""
        with urllib.request.urlopen(self.url) as response:
            self.web_content = response.read().decode('utf-8')
        self.save_to_file()
        return self.web_content

    def fetch_data(self) -> str:
        """Get data, using cache if not stale."""
        if self.web_content:
            return self.web_content
        if self.is_cache_stale():
            self.web_content = self.request_data_from_web()
        else:
            self.web_content = self.read_from_file()
        return self.web_content if self.web_content is not None else ""

    def save_to_file(self) -> None:
        """Save current web_content to the cache file."""
        if self.web_content is not None:
            with open(self.CACHE_FILE, 'w', encoding='utf-8') as file:
                file.write(self.web_content)

    def read_from_file(self) -> str:
        """Read content from the cache file."""
        with open(self.CACHE_FILE, 'r', encoding='utf-8') as file:
            return file.read()

    def is_cache_stale(self) -> bool:
        """Check if the cache file is older than CACHE_HOURS hours or missing."""
        if os.path.exists(self.CACHE_FILE):
            file_age = time.time() - os.path.getmtime(self.CACHE_FILE)
            if file_age > self.CACHE_HOURS * 60 * 60:
                return True
            return False
        return True