from typing import Optional
import re


def read_url_from_request(request) -> Optional[str]:
    pass


def is_valid_url(url: str) -> bool:
        # From: https://www.geeksforgeeks.org/dsa/check-if-an-url-is-valid-or-not-using-regular-expression/
        url_pattern = ("((http|https)://)(www.)?" + 
             "[a-zA-Z0-9@:%._\\+~#?&//=]" + 
             "{2,256}\\.[a-z]" + 
             "{2,6}\\b([-a-zA-Z0-9@:%" + 
             "._\\+~#?&//=]*)")
        return re.match(url_pattern, url) is not None


def normalize_url(url: str) -> str:
    pass
