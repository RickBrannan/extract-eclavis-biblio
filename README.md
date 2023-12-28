# extract-eclavis-biblio
Python code to extract [NASSCAL e-Clavis](https://www.nasscal.com/e-clavis-christian-apocrypha/) bibliography entries

# Background

The [NASSCAL e-Clavis](https://www.nasscal.com/e-clavis-christian-apocrypha/) is a “comprehensive bibliography of Christian Apocrypha research assembled and maintained by members of the North American Society for the Study of Christian Apocryphal Literature (NASSCAL).”

However, the bibliographic entries within the e-Clavis are not easily used. The goal of this code is to isloate each individual bibliographic entry and some context for use in later processing of the data into a BibTex format or something similar for importation into Zotero.

# License

The Python code in this repo is licensed under the MIT license. See the [LICENSE](LICENSE.md) file for details.

The NASSCAL e-Clavis itself is licensed under CC-BY-4.0 license. The data extracted from the e-Clavis that is hosted in this repository is offered under the same CC-BY-4.0 license.

# Code

There is one script, `extract.py`, that scrapes the NASSCAL e-Clavis website and extracts the bibliograhical data. We archive the HTML that we scraped, and we also create JSON from the HTML.

# JSON Schema

The JSON is based on Python dataclasses used to aggregate the data.

## ApocryphalWriting object

<table>
<tr><td><b>Property</b></td><td><b>Type</b></td><td><b>Description</b></td></tr>
<tr><td>`nasscal_url`</td><td>string</td><td>URL to the web page for the apocyrphal writing</td></tr>
<tr><td>`nasscal_title`</td><td>string</td><td>String representing best available title for the work</td></tr>
<tr><td>`filename`</td><td>string</td><td>String with the extension-free filename (matches both HTML and JSON)</td></tr>
<tr><td>`latin_title`</td><td>string</td><td>The formal title of the work in Latin</td></tr>
<tr><td>`abbrev`</td><td>string</td><td>Formal abbreviation for the work</td></tr>
<tr><td>`alt_titles`</td><td>list[string]</td><td>List of alternate titles for the work</td></tr>
<tr><td>`clavis_number`</td><td>int</td><td>Where available, a number representing the e-Clavis number for the work.</td></tr>
<tr><td>`category`</td><td>string</td><td>Category of the writing (e.g. "Apocalypse", "Apocryphal Act")</td></tr>
<tr><td>`compiler`</td><td>string</td><td>A representation of the individual(s) responsible for the e-Clavis entry.</td></tr>
<tr><td>`bibliography_entries`</td><td>list[BibliographyEntry]</td><td>A list of BibliographyEntry objects with information useful for determining bibliographic information</td></tr>
</table>

## BibliographyEntry object

<table>
<tr><td><b>Property</b></td><td><b>Type</b></td><td><b>Description</b></td></tr>
<tr><td>`line_html`</td><td>string</td><td>The HTML of the bibliographic entry from the e-Clavis page</td></tr>
<tr><td>`line_text`</td><td>string</td><td>A plain-text representation of the bibliographic entry from the e-Clavis page</td></tr>
<tr><td>`language`</td><td>string</td><td>An English representation of the language. These may later be mapped to their ISO-639 value.</td></tr>
<tr><td>`manuscripta_apocryphorum_urls`</td><td>list[string]</td><td>A list of Manuscripta Apocryphorum URLs associated with the BibliographyEntry</td></tr>
<tr><td>`other_urls`</td><td>list[string]</td><td>A list of URLs associated with the BibliographyEntry</td></tr>
</table>
