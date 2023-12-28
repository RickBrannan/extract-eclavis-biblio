# from bs4 import BeautifulSoup
import copy
import re

from lxml import etree
import requests
import config
from shared.shared_classes import *
from src import DATAPATH, ROOT
from dataclasses import dataclass


# ok, do we use saved data or scrape new data?
use_local_data = False

base_url = "https://www.nasscal.com/e-clavis-christian-apocrypha/"
primary_url = "https://www.nasscal.com/"
folder_url = "e-clavis-christian-apocrypha/"
response = requests.get(base_url, headers={"User-Agent": "biblio-extract"})
htmlparser = etree.HTMLParser(remove_pis=True, remove_comments=True, remove_blank_text=True)
tree = etree.fromstring(response.text, htmlparser)

links = {}
for link in tree.xpath("//article/div[@class='entry-content']/p/a"):
    # hm, how to handle 1 Apocr. Apoc. Jn which is in
    if link.attrib['href'].startswith(base_url):
        print(f"link: {link.attrib['href']}; text: {link.text}")
        links[link.attrib['href']] = link.text
    elif link.attrib['href'].startswith(primary_url):
        if not re.search("manuscripta", link.attrib['href']):
            print(f"link: {link.attrib['href']}; text: {link.text}")
            links[link.attrib['href']] = link.text

# ok, now cycle links that include the baseurl and extract bibliography data
for link_url in links:
    link_toc_title = links[link_url]
    filename = re.sub(base_url, "", link_url)
    if filename.startswith(primary_url):
        filename = re.sub(primary_url, "", filename)
    filename = re.sub(r"/$", "", filename) # trim trailing '/' if it's there
    # load into the ApocryphalWriting dataclass
    apoc = ApocryphalWriting(link_url, link_toc_title, filename)
    # get the page
    if not use_local_data:
        response = requests.get(link_url, headers={"User-Agent": "biblio-extract"})
        html_file = DATAPATH / "html" / "scraped" / f"{apoc.filename}.html"
        html_file.write_text(response.text, encoding="utf-8")

    # ok, read in file (perhaps just saved) and do stuff
    html_file = DATAPATH / "html" / "scraped" / f"{apoc.filename}.html"
    print(f"Loading: {apoc.filename}.html ... ")
    html = html_file.read_text(encoding="utf-8")
    if not re.search("<article", html):
        print(f"{html_file}: no article found. Skipping")
        continue
    # read it in
    tree = etree.fromstring(html, htmlparser)
    # now cycle the data and fill out the object as necessary.
    article = tree.xpath(".//article")[0]
    # get the title from the doc
    article_title = article.xpath(".//header/h1")[0].text
    if apoc.nasscal_toc_title != article_title:
        apoc.alt_titles = []
        apoc.alt_titles.append(copy.copy(apoc.nasscal_toc_title))
        apoc.nasscal_toc_title = article_title
    # get latin title from the doc
    latin_title = article.xpath(".//div/p/strong")[0].text
    apoc.latin_title = latin_title
    # ok, now cycle paragraphs of the div and pick stuff we want until
    # we get to 'BIBLIOGRAPHY'. Then we check line by line to gather citations.

    in_bibliography = False
    bibliography_language = "English"
    bibliography_entry_type = "Edition"
    for para in article.xpath("//div/p"):
        para_xml = etree.tostring(para, encoding="unicode").strip()
        para_text = re.sub(r"<[^>]+>", "", para_xml)  # is this good enough?
        para_text = re.sub(r"\n", " ", para_text)

        if para.text is not None:
            if re.search(r"^Standard abbreviation:", para.text):
                # is it in 'em'? or 'i'? Or not at all?
                if para.xpath(".//em"):
                    apoc.abbrev = para.xpath(".//em")[0].text
                elif para.xpath(".//i"):
                    apoc.abbrev = para.xpath(".//i")[0].text
                else:
                    apoc.abbrev = re.sub(r"^Standard abbreviation:\s*", "", para.text)
            elif re.search(r"^Other titles:", para.text):
                # is it in 'em'? or 'i'? Or not at all?
                for title in para.xpath(".//em"):
                    apoc.alt_titles.append(title.text)
                for title in para.xpath(".//i"):
                    apoc.alt_titles.append(title.text)
            elif re.search(r"^Clavis numbers:.*ECCA\s*\d+", para_text):
                    apoc.clavis_number = int(re.sub(r"^.*ECCA\s*(\d+).*$", r"\1", para_text))
            elif re.search(r"^Category:", para.text):
                apoc.category = re.sub(r"^Category:\s*", "", para.text)
            elif re.search(r"^Compiled by", para.text):
                apoc.compiler = re.sub(r"^Compiled by\s*", "", para.text)
                apoc.compiler = re.sub(r"\s*\(.*$", "", apoc.compiler)

        if re.search(r"BIBLIOGRAPHY", para_text, flags=re.IGNORECASE):
            in_bibliography = True
            apoc.bibliography_entries = []

        if in_bibliography:
            # do stuff. is it a subheading, or an entry?
            # what type of entry (manuscript?)
            if re.search(r"^\d+\.\d+\.\d+", para_text):
                # bibliography language heading :fingers-crossed:
                language = re.sub(r"^\d+\.\d+\.\d+\s*", "", para_text)
                bibliography_language = re.sub(r"\s*\(.*$", "", language.strip())
            elif re.search(r"^\d+\.\d+\s*", para_text):
                bibliography_entry_type = re.sub(r"^\d+\.\d+\s*", "", para_text.strip())
                if bibliography_entry_type == "Manuscripts and Editions":
                    bibliography_entry_type = "Edition"
                elif bibliography_entry_type == "Modern Translations":
                    bibliography_entry_type = "Translation"
                elif bibliography_entry_type == "General Works":
                    bibliography_entry_type = "Other"
                # also, reset this bad boy
                bibliography_language = "English"

            if re.search(r"^\d+\.", para_text):
                continue

            biblio = BibliographyEntry(para_xml, para_text, bibliography_language, bibliography_entry_type, [], [])

            # there's no way this is consistent; what other options are witnessed?
            if re.search(r"<p[^>]*padding-left: [43]0px;", para_xml):
                biblio.entry_type = "Manuscript"

            for link in para.xpath(".//a"):
                if re.search("manuscripta-apocryphorum", link.attrib['href']):
                    biblio.manuscripta_apocryphorum_urls.append(link.attrib['href'])
                    biblio_entry_type = "Manuscript"
                else:
                    biblio.other_urls.append(link.attrib['href'])
            apoc.bibliography_entries.append(biblio)

    # ok, now we need to dump the data as JSON
    print(f'Dumping: {apoc.filename}.json ... ')
    with open(f"{DATAPATH}/json/{apoc.filename}.json", 'w', encoding='utf-8') as outfile:
        # need to dance a little to remove the empty elements from the WordLevelData objects
        apoc_data = json.dumps(apoc, indent=2, cls=EntityDataEncoder, ensure_ascii=False)
        cleaned_apoc_data = json.loads(apoc_data, object_hook=remove_empty_elements)
        json.dump(cleaned_apoc_data, outfile, indent=2, ensure_ascii=False)

