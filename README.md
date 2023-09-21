## XML SAX parser for UFED/Cellebrite.

[![Continuous Integration](https://github.com/casework/CASE-Implementation-UFED-XML/actions/workflows/cicd.yml/badge.svg)](https://github.com/casework/CASE-Implementation-UFED-XML/actions/workflows/cicd.yml)
![CASE Version](https://img.shields.io/badge/CASE%20Version-1.2.0-green)

The parser extracts some digital traces (Cyber items) from XML reports generated by UFED Physical Analyser (version 7.x) and convert them into UCO/CASE as JSON-LD files.
=======
The parser extracts the most relevat digital traces (cyber items) from XML reports generated by UFED Physical Analyser (version 7.x) and convert them into UCO/CASE as JSON-LD files.

The UFED parser is able to process any report, regardless their size, it has been developed using **Python, version 3.x** and based on **SAX** (Simple API for XML).

The UFED parser is composed of two different modules:

* parser_UFEDtoCASE (XML parser program)
* UFEDtoJSON.py (data converter into CASE-JSON-LD files)
* CASE_generator.py (classes to generate JSON-LD files borrowed from the case_builder library developed within the INSPECTr project - Intelligence Network and Secure Platform for Evidence Correlation and Transfer, GA n. 833276). The library will be available soon on CASE repo.

## Requirements
The tool has been developed in Python version 3.x and here are some required modules:

* xml.sax (SAX classes)
* argparse (args input management)
* os (operating system utilities)
* codecs (UTF-8 and other codec management)
* re (regular expressions management)
* uuid (global unique identifier management)
* datetime
* timeit
* time 
* json

## Usage

```js
> *parser_UFEDtoCASE.py  [-h]*
>                       *-r INFILEXML*
>                       *-o OUTPUT_CASE_JSON*
```
where:

```js
* -h, --help (show the help message and exit)
* -r | --report INFILEXML (the UFED XML report to be converted into CASE, compulsary)
* -o | --output OUTPUT_CASE_JSON (CASE-JSON-LD file to be generated, compulsory)
```

## Mobile Forensic Data set
The UFED parser has been developed and tested relying on a huge collection of mobile forensic dataset. This is composed of images made available on the Computer Forensic Reference Data Sets  (CFReDS) Project and also on those provided by Cellebrite within he Catch The Flag annual competition.

## CASE representation: JSON-LD files
All the XML reports have been processed to generate the corresponding CASE representation of the following Cyber items:

* Calendar
* Call
* Cell Site
* Chat (Whatsapp, Skype, etc.)
* Contact
* Cookie
* Device Connectivity (Bluetooth connections)
* Email
* Event (Device)
* File
* Installed Applications
* Location (Device)
* Searched item (drafting namespace)
* Social Media Activity (drafting namespace)
* SMS
* URL History
* Web Bookmarks
* Wifi Connection 
* Chain of Evidence (relationships between a Digital Trace and the File/Db from which it was extracted)
* Context
  * Device info
  * Tool
  * Performer
  * Provenance Record
  * Investigative Acquisition
  * Investigative Extraction

## XML reports

The repo also includes the XMLreports folder containing examples of reports from Cellebrite UFED PA.

## Drafting TTL

The TTL describing the additional ontology classes based on the drafting namespace

## Development status

This repository follows [CASE community guidance on describing development status](https://caseontology.org/resources/github_policies.html#development-statuses), by adherence to noted support requirements.

The status of this repository is:

4 - Beta
