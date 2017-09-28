#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This script takes a directory with a BibTeX .bib file and creates a set of .md
files for use in the Academic theme for Hugo (a general-purpose, static-site
generating web framework). Each file incorporates the data for a single
publication.

Written for and tested using python 3.6.2

Requires: bibtexparser

This is a modified form of code written by Mark Coster.
Copyright (C) 2017 Mark Coster
"""

import argparse
import os
import string

import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import *

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("bib_dir", help="Directory with publication info as publications.bib and one directory per pub containing citation info.")
    parser.add_argument('out_dir', nargs='?', default='publication',
                        help="output directory")
    parser.add_argument("-v", "--verbose", help="increase output verbosity",
                        action="store_true")
    args = parser.parse_args()

    if args.verbose:
        print("Verbosity turned on")
        print("Opening {}".format(args.bib_dir))

    bib_filename = os.path.join(args.bib_dir, "publications.bib")
    try:
        with open(bib_filename) as bib_file:
            parser = BibTexParser()
            parser.customization = customizations
            bib_data = bibtexparser.load(bib_file, parser=parser)
    except IOError:
        print('There was a problem opening the file.')

    raw_bibtex = {}
    with open(bib_filename) as bib_file:
        current = None
        name = None
        for line in bib_file:
            if line.startswith("@"):
                current = []
                name = line.split("{")[1].split(',')[0]
            if current is not None:
                current.append(line)
            if line.startswith("}"):
                raw_bibtex[name] = ''.join(current)

    if not os.path.exists(args.out_dir):
        if args.verbose:
            print("Creating directory '{}'".format(args.out_dir))
        os.makedirs(args.out_dir)

    for index, entry in enumerate(bib_data.entries):
        if args.verbose:
            print("Making entry {0}: {1}".format(index + 1, entry['ID']))
###            print(entry)
        
        info = {
            "bibkey": '"{}"'.format(entry['ID']),
            "bibtex": '""',
            "title": '""',
            "date": '""',
            "draft": "false",
            "authors": '['""']',
            "publication_types": '["0"]',
            "publication": '""',
            "publication_short": '""',
            "abstract": '""',
            "abstract_short": '""',
            "address": '""',
            "doi": '""',
            "issue": '""',
            "number": '""',
            "pages": '""',
            "publisher": '""',
            "volume": '""',
            "math": "true",
            "highlight": "false",
            "image_preview": '""',
            "selected": "false",
            "url_pdf": '""',
            "url_poster": '""',
            "url_code": '""',
            "url_dataset": '""',
            "url_project": '""',
            "url_slides": '""',
            "url_video": '""',
        }
        
        if 'abstract' in entry:
            if entry['abstract'][0] not in string.ascii_uppercase:
                print(entry['abstract'])
            abstract = entry['abstract'].replace('"', '\\"')
            abstract = abstract.replace('\\%', '%')
            if '\n' in abstract:
                info['abstract'] = '"""{}"""'.format(abstract)
                info['abstract_short'] = '"""{}"""'.format(abstract)
            else:
                info['abstract'] = '"{}"'.format(abstract)
                info['abstract_short'] = '"{}"'.format(abstract)
        
        bibtex = raw_bibtex[entry['ID']]
        info['bibtex'] = '"""{}"""'.format(bibtex.replace('\\%', '%'))

        authors = []
        for author in entry['author']:
            parts = author.split(",")
            author = ' '.join(parts[1:]) +" "+ parts[0]
            authors.append('"{}"'.format(author.strip()))
        info['authors'] = '[{}]'.format(', '.join(authors))

        if 'year' in entry:
            year = entry['year']
            month = '01'
            if 'month' in entry:
                if entry['month'].lower() == 'january': month = '01'
                elif entry['month'].lower() == 'february': month = '02'
                elif entry['month'].lower() == 'march': month = '03'
                elif entry['month'].lower() == 'april': month = '04'
                elif entry['month'].lower() == 'may': month = '05'
                elif entry['month'].lower() == 'june': month = '06'
                elif entry['month'].lower() == 'july': month = '07'
                elif entry['month'].lower() == 'august': month = '08'
                elif entry['month'].lower() == 'september': month = '09'
                elif entry['month'].lower() == 'october': month = '10'
                elif entry['month'].lower() == 'november': month = '11'
                elif entry['month'].lower() == 'december': month = '12'
            info['date'] = '"{}-{}-01"'.format(year, month)

        if entry['ENTRYTYPE'] == 'inproceedings':
            info['publication_types'] = '["1"]'
            info['publication'] = '"'+ entry['booktitle'] +'"'
        elif entry['ENTRYTYPE'] == 'article':
            info['publication_types'] = '["2"]'
            info['publication'] = '"'+ entry['journal']['name'] +'"'
        elif entry['ENTRYTYPE'] == 'phdthesis':
            info['publication_types'] = '["4"]'
            info['publication'] = '"'+ entry['school'] +'"'
        elif entry['ENTRYTYPE'] == 'techreport':
            info['publication_types'] = '["4"]'
            info['publication'] = '"'+ entry['institution'] +'"'

        if 'shortvenue' in entry:
            info['publication_short'] = '"'+ entry['shortvenue'] +'"'
        else:
            info['publication_short'] = info['publication']

        simple_fields = [
            'title', 'address', 'doi', 'issue', 'number', 'pages', 'publisher',
            'volume',
        ]
        for name in simple_fields:
            if name in entry:
                info[name] = '"{}"'.format(entry[name])

        if 'link' in entry:
            for content in entry['link']:
                if 'url' in content:
                    info["url_pdf"] = '"{}"'.format(content['url'])
        if 'poster' in entry:
            info["url_poster"] = '"{}"'.format(entry['poster'])
        if 'software' in entry:
            info["url_code"] = '"{}"'.format(entry['software'])
        if 'data' in entry:
            info["url_dataset"] = '"{}"'.format(entry['data'])
        if 'slides' in entry:
            info["url_slides"] = '"{}"'.format(entry['slides'])
        if 'slidespdf' in entry:
            info["url_slides_pdf"] = '"{}"'.format(entry['slidespdf'])

        # Get citations
        cite_filename = os.path.join(args.bib_dir, entry["ID"], "citations.bib")
        cite_info = []
        try:
            with open(cite_filename) as cite_file:
                parser = BibTexParser()
                parser.customization = customizations
                cite_data = bibtexparser.load(cite_file, parser=parser)
                for index, citation in enumerate(cite_data.entries):
                    cite_info.append("\n[[citation]]")
                    title = citation['title'].replace('"', '\\"')
                    cite_info.append('title = "'+ title +'"')
                    cite_info.append('year = "'+ citation['year'] +'"')
                    if 'url' in citation:
                        cite_info.append('url = "'+ citation['url'] +'"')
                    else:
                        cite_info.append('url = ""')
                    if citation['ENTRYTYPE'] == 'inproceedings':
                        cite_info.append('venue = "'+ citation['booktitle'] +'"')
                    elif citation['ENTRYTYPE'] == 'article':
                        cite_info.append('venue = "'+ citation['journal']['name'] +'"')
                    elif citation['ENTRYTYPE'] == 'phdthesis':
                        cite_info.append('venue = "'+ citation['school'] +'"')
                    elif citation['ENTRYTYPE'] == 'techreport':
                        cite_info.append('venue = "'+ citation['institution'] +'"')
                    cite_authors = []
                    for author in citation['author']:
                        parts = author.split(",")
                        author = ' '.join(parts[1:]) +" "+ parts[0]
                        cite_authors.append(author.strip())
                    cite_info.append('author = "'+ ', '.join(cite_authors) +'"')
        except IOError:
            print(cite_filename, "not found.")

        # Generate

        output = ['+++']
        for name in info:
            output.append(name +" = "+ info[name])
        
        output.append("\n".join(cite_info) +"\n")
        
        output.append('\n+++')
        pub_info = '\n'.join(output)
        out_filename = os.path.join(args.out_dir, entry['ID'] +'.md')

        try:
            if args.verbose:
                print("Saving '{}'".format(out_filename))
            with open(out_filename, 'w') as pub_file:
                pub_file.write(pub_info)
        except IOError:
            print('There was a problem writing to the file.')


def customizations(record):
    """Use some functions delivered by the library

    :param record: a record
    :returns: -- customized record
    """
    record = type(record)
    record = author(record)
    record = editor(record)
    record = journal(record)
    record = keyword(record)
    record = link(record)
    record = doi(record)
    record = convert_to_unicode(record)
    return record

if __name__ == '__main__':
    main()
