from typing import Dict, Any
from audiobook.common import AutoRepr
from .parser import AudibleParserJsonLD, AudibleParserWeb


class Audible(AutoRepr):
    def __init__(self, asin: str):
        self.asin: str = asin
        json_ld = AudibleParserJsonLD(self.asin)
        print(json_ld)
        if json_ld.url:
            web = AudibleParserWeb(json_ld.url)
            print(web)
        self.json_ld: Dict[str, Any] = {}
