#!/usr/bin/env python3

import argparse
import os
import io
import string

def authors(content):
    if ',' in content:
        authors = content.split(",")
        if 'and' in authors[-1]:
            last = authors.pop()
            parts = last.split(" amd ")
            for part in parts:
                authors.append(part.strip())
        return authors
    else:
        authors = content.split(" and ")
        authors = [a.strip() for a in authors]
        return authors

def read_file(src):
    citations = []
    cur = []
    for line in open(src):
        line = line.strip()
        if '\\&' in line:
            line = '&'.join(line.split("\\&"))
        if line == '}':
            info = {}
            for line in cur[1:]:
                key = line.split()[0]
                content = line[len(key):].strip()[3:-2]
                if key == 'author':
                    content = authors(content)
                info[key] = content
            info['ENTRYTYPE'] = cur[0].split("{")[0][1:].lower()
            info['ID'] = cur[0].split("{")[1][:-1]
            citations.append(info)
            cur = []
        elif len(line) > 0 or len(cur) > 0:
            if len(cur) == 0:
                if line.startswith("@"):
                    cur.append(line)
            elif cur[-1].endswith("},") or cur[-1].startswith("@"):
                cur.append(line)
            else:
                cur[-1] += "\n" + line
    return citations

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
    bib_data = read_file(bib_filename)

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

    for index, entry in enumerate(bib_data):
        for key in entry:
            if '"' in entry[key]:
                entry[key] = "'".join(entry[key].split('"'))
        if args.verbose:
            print("Making entry {0}: {1}".format(index + 1, entry['ID']))
        
        info = {
            "bibkey": '"{}"'.format(entry['ID']),
            "bibtex": '""',
            "title": '""',
            "date": '""',
            "draft": "false",
            "preprint": "false",
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
            "url_interview": '""',
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
            author = author.strip()
            if author.strip("\\\\*") == 'Jonathan K. Kummerfeld':
                author = "<span style='text-decoration:underline;'>"+ author +"</span>"
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

        if entry['ENTRYTYPE'].lower() == 'inproceedings':
            info['publication_types'] = '["1"]'
            info['publication'] = '"'+ entry['booktitle'] +'"'
        elif entry['ENTRYTYPE'].lower() == 'article':
            info['publication_types'] = '["2"]'
            info['publication'] = '"'+ entry['journal'] +'"'
            if entry['journal'] == "ArXiv e-prints":
                info['preprint'] = 'true'
        elif entry['ENTRYTYPE'].lower() == 'phdthesis':
            info['publication_types'] = '["4"]'
            info['publication'] = '"'+ entry['school'] +'"'
        elif entry['ENTRYTYPE'].lower() == 'techreport':
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

        if 'url' in entry:
            info["url_pdf"] = '"{}"'.format(entry['url'])
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
        if 'video' in entry:
            info["url_video"] = '"{}"'.format(entry['video'])
        if 'interview' in entry:
            info["url_interview"] = '"{}"'.format(entry['interview'])

        # Get citations
        cite_filename = os.path.join(args.bib_dir, entry["ID"], "citations.bib")
        cite_info = []
        try:
            for citation in read_file(cite_filename):
                cite_info.append("\n[[citation]]")
                title = citation['title'].replace('"', '\\"')
                cite_info.append('title = "'+ title +'"')
                cite_info.append('year = "'+ citation['year'] +'"')
                if 'url' in citation:
                    cite_info.append('url = "'+ citation['url'] +'"')
                else:
                    cite_info.append('url = ""')
                if citation['ENTRYTYPE'].lower() == 'inproceedings':
                    cite_info.append('venue = "'+ citation['booktitle'] +'"')
                elif citation['ENTRYTYPE'].lower() == 'article':
                    cite_info.append('venue = "'+ citation['journal'] +'"')
                elif citation['ENTRYTYPE'].lower() == 'phdthesis':
                    cite_info.append('venue = "'+ citation['school'] +'"')
                elif citation['ENTRYTYPE'].lower() == 'techreport':
                    cite_info.append('venue = "'+ citation['institution'] +'"')
                cite_authors = []
                for author in citation['author']:
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

if __name__ == '__main__':
    main()
