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
        if "{\\'a}" in line:
            line = "á".join(line.split("{\\'a}"))
        if "{\\'i}" in line:
            line = "í".join(line.split("{\\'i}"))
        if "{\\'\\i}" in line:
            line = "í".join(line.split("{\\'\\i}"))
        if "{\\'o}" in line:
            line = "ó".join(line.split("{\\'o}"))
        if "{\\'e}" in line:
            line = "é".join(line.split("{\\'e}"))
        if '\\&' in line:
            line = '&'.join(line.split("\\&"))
        if line == '}':
            info = {}
            for line in cur[1:]:
                key = line.split()[0]
                if key == 'reviews' or key == 'senior-authors':
                    continue
                content = line[len(key):].strip().lstrip("=").rstrip(",").strip()[1:-1]
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
            elif cur[-1].endswith("},") or cur[-1].endswith('",') or cur[-1].startswith("@"):
                cur.append(line)
            else:
                cur[-1] += "\\n" + line
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
            if "\\'" in line:
                line = "\\\\'".join(line.split("\\'"))
            if line.startswith("@"):
                current = []
                name = line.split("{")[1].split(',')[0]
            if current is not None:
                if ' reviews ' in line:
                    pass
                elif ' senior-authors ' in line:
                    pass
                elif ' shortvenue ' in line:
                    pass
                elif ' abstract ' in line:
                    pass
                elif ' archival ' in line:
                    pass
                else:
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
            "bibkey": '{}'.format(entry['ID']),
            "bibtex": '',
            "title": '',
            "date": '',
            "year": '',
            "draft": "false",
            "preprint": "false",
            "archival": "true",
            "authors": '[]',
            "publication_types": '["0"]',
            "publication": '',
            "publication_short": '',
            "abstract": '',
            "abstract_short": '',
            "address": '',
            "doi": '',
            "issue": '',
            "number": '',
            "pages": '',
            "publisher": '',
            "volume": '',
            "math": "true",
            "highlight": "false",
            "image_preview": '',
            "selected": "false",
            "url_pdf": '',
            "url_poster": '',
            "url_interview": '',
            "url_arxiv": '',
            "url_code": '',
            "url_dataset": '',
            "url_project": '',
            "url_slides": '',
            "url_video": '',
            "url_blog": '',
        }
        
        if 'abstract' in entry:
            if entry['abstract'][0] not in string.ascii_uppercase:
                print(entry['abstract'])
            abstract = entry['abstract'].replace('"', '\\"')
            abstract = abstract.replace('\\%', '%')
            if '\n' in abstract:
                info['abstract'] = '"{}"'.format(abstract)
                info['abstract_short'] = '"{}"'.format(abstract)
            else:
                info['abstract'] = '{}'.format(abstract)
                info['abstract_short'] = '{}'.format(abstract)
        
        bibtex = raw_bibtex[entry['ID']]
        info['bibtex'] = '"""{}"""'.format(bibtex.replace('\\%', '%'))

        authors = []
        for author in entry['author']:
            author = author.strip().strip("\\\\*")
            if author == 'Jonathan K. Kummerfeld':
                author = "admin"
            authors.append('\n- {}'.format(author.strip()))
        info['authors'] = ''.join(authors)

        if 'year' in entry:
            year = entry['year']
            info['year'] = str(year)
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
            info['publication'] = entry['booktitle']
        elif entry['ENTRYTYPE'].lower() == 'article':
            info['publication_types'] = '["2"]'
            info['publication'] = entry['journal']
            if entry['journal'] == "ArXiv e-prints" or entry.get('shortvenue', "") == "ArXiv":
                info['preprint'] = 'true'
        elif entry['ENTRYTYPE'].lower() == 'misc':
            info['publication_types'] = '["4"]'
            info['publication'] = entry['archivePrefix']
            if entry['shortvenue'] == "ArXiv":
                info['publication_types'] = '["3"]'
                info['preprint'] = 'true'
        elif entry['ENTRYTYPE'].lower() == 'phdthesis':
            info['publication_types'] = '["7"]'
            info['publication'] = entry['school']
        elif entry['ENTRYTYPE'].lower() == 'techreport':
            info['publication_types'] = '["4"]'
            info['publication'] = entry['institution']

        if entry.get('archival', "") == 'false':
            info['archival'] = 'false'

        if 'shortvenue' in entry:
            info['publication_short'] = entry['shortvenue']
        else:
            info['publication_short'] = info['publication']

        simple_fields = [
            'title', 'address', 'doi', 'issue', 'number', 'pages', 'publisher',
            'volume',
        ]
        for name in simple_fields:
            if name in entry:
                info[name] = '{}'.format(entry[name])

        if 'url' in entry and len(entry['url']) > 0:
            info["url_pdf"] = entry['url']
        elif 'arxiv' in entry:
            info["url_pdf"] = entry['arxiv']

        if 'poster' in entry:
            info["url_poster"] = entry['poster']
        if 'software' in entry:
            info["url_code"] = entry['software']
        if 'data' in entry:
            info["url_dataset"] = entry['data']
        if 'slides' in entry:
            info["url_slides"] = entry['slides']
        if 'video' in entry:
            info["url_video"] = entry['video']

        info['links'] = []
        if 'slidespdf' in entry:
            info["links"].append("\n- name: {}\n  url: {}".format("PDF Slides", entry['slidespdf']))
        if 'interview' in entry:
            info["links"].append("\n- name: {}\n  url: {}".format("Interview", entry['interview']))
        if 'blog_post' in entry:
            info["links"].append("\n- name: {}\n  url: {}".format("Blog Post", entry['blog_post']))
        if 'supplementary' in entry:
            info["links"].append("\n- name: {}\n  url: {}".format("Supplementary Material", entry['supplementary']))
        if 'arxiv' in entry:
            info["links"].append("\n- name: {}\n  url: {}".format("ArXiv", entry['arxiv']))
            info["url_arxiv"] = entry['arxiv']
        info['links'] = ''.join(info['links'])

        # Get citations
        cite_filename = os.path.join(args.bib_dir, entry["ID"], "citations.bib")
        cite_info = ['citations:']
        info['citation_count'] = 0
        try:
            for citation in read_file(cite_filename):
                info['citation_count'] += 1
                title = citation['title'].replace('"', '\\"')
                vals = {}
                vals['title'] = title
                vals['year'] = citation.get('year', '')
                vals['url'] = citation.get('url', '')
                venue = ''
                if citation['ENTRYTYPE'].lower() == 'inproceedings':
                    vals['venue'] = citation['booktitle']
                elif citation['ENTRYTYPE'].lower() == 'article':
                    vals['venue'] = citation['journal'] 
                elif citation['ENTRYTYPE'].lower() == 'phdthesis':
                    vals['venue'] = citation['school'] 
                elif citation['ENTRYTYPE'].lower() == 'techreport':
                    vals['venue'] = citation['institution']
                vals['authors'] = []
                for author in citation['author']:
                    vals['authors'].append(author.strip())
                vals['authors'] = ', '.join(vals['authors'])
                parts = []
                for key, value in vals.items():
                    if ':' in value or '{' in value:
                        value = '"{}"'.format(value)
                    parts.append("  {}: {}".format(key, value))
                parts[0] = '-' + parts[0][1:]
                for part in parts:
                    cite_info.append(part)
                if args.verbose:
                    print("Adding citation:", citation['title'])
        except IOError:
            print(cite_filename, "not found.")

        # Generate

        output = ['---']
        for name in info:
            if name == 'bibtex':
                continue
            if ':' in str(info[name]) and "\n" not in info[name]:
                info[name] = '"{}"'.format(info[name])
            output.append("\n"+ name +": "+ str(info[name]))
        
        output.append("\n".join(cite_info) +"\n")
        
        output.append('\n---')
        pub_info = '\n'.join(output)
        out_directory = os.path.join(args.out_dir, entry['ID'])
        out_filename = os.path.join(out_directory, 'index.md')
        bib_filename = os.path.join(out_directory, 'cite.bib')

        try:
            if args.verbose:
                print("Making '{}'".format(out_directory))
            os.mkdir(out_directory)
        except FileExistsError:
            pass

        try:
            if args.verbose:
                print("Saving '{}'".format(out_filename))
            with open(out_filename, 'w') as pub_file:
                pub_file.write(pub_info)
            if 'bibtex' in info:
                if args.verbose:
                    print("Saving '{}'".format(bib_filename))
                with open(bib_filename, 'w') as bib_file:
                    bib_file.write(info['bibtex'].strip("%").strip('"'))
        except IOError as e:
            print('There was a problem writing to the file.')
            print(e)

if __name__ == '__main__':
    main()
