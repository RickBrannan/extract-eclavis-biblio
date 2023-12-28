import os
import regex as re
import pandas as pd
import json as json
import unicodedata
from json import JSONEncoder
from lxml import etree
from dataclasses import dataclass, field


@dataclass
class BibliographyEntry:
    line_html: str
    line_text: str
    language: str = ""
    entry_type: str = "Edition"  # edition or manuscript? enum?
    manuscripta_apocryphorum_urls: list = field(default_factory=list)
    other_urls: list = field(default_factory=list)


@dataclass
class ApocryphalWriting:
    nasscal_url: str
    nasscal_title: str
    filename: str
    latin_title: str = ""
    abbrev: str = ""
    alt_titles: list = field(default_factory=list)
    clavis_number: int = 0
    category: str = ""
    compiler: str = "Tony Burke, York University"
    bibliography_entries: list = field(default_factory=list) # these use the `BibliographicEntry` dataclass
    # date?


# we need to make a custom encoder to handle the dataclass
class EntityDataEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__

def remove_empty_elements(d):
    """recursively remove empty lists, empty dicts, or None elements from a dictionary"""
    # thank you, https://gist.github.com/nlohmann/c899442d8126917946580e7f84bf7ee7
    def empty(x):
        return x is None or x == {} or x == [] or x == ""

    if not isinstance(d, (dict, list)):
        return d
    elif isinstance(d, list):
        return [v for v in (remove_empty_elements(v) for v in d) if not empty(v)]
    else:
        return {k: v for k, v in ((k, remove_empty_elements(v)) for k, v in d.items()) if not empty(v)}


