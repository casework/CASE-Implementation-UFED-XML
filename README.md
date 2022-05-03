## XML SAX parser for UFED/Cellebrite.

The parser extracts some digital traces (Cyber items) from XML reports generated by UFED Physical Analyser (version 7.x) and convert them into UCO/CASE as JSON-LD files.

The UFED parser is able to process any report, regardless their size, it has been developed using **Python, version 3.x** and based on **SAX** (Simple API for XML).

The UFED parser is composed of two different modules:

* parser_UFEDtoCASE (main program)
* caseJson.py (class for generating CASE-JSON-LD files)

## Requirements
The tool has been developed in Python version 3.x and here are some required modules:

* xml.sax (SAX classes)
* string (string utilities)
* argparse (args input management)
* os (operating system utilities)
* codecs (UTF-8 and other codec management)
* re (regular expressions management)
* uuid (global unique identifier management)
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
* Cell Tower (drafting)
* Chat (Whatsapp, Skype, etc.)
* Contact
* Cookie
* Email
* Event
* File
* Searched item (drafting)
* Social Media Activity (drafting)
* SMS
* URL History
* Wifi Connection (drafting)
* Chain of Evidence
* Context
  * Device info
  * Tool
  * Performer
  * Provenance Record
  * Investigative Acquisition
  * Investigative Extraction


## XML reports

The repo also includes the XMLreports folder containing examples of reports from Cellebrite UFED PA.

## Development status

This repository follows [CASE community guidance on describing development status](https://caseontology.org/resources/github_policies.html#development-statuses), by adherence to noted support requirements.

The status of this repository is:

4 - Beta
