import re
import os
import requests
from bs4 import BeautifulSoup
import html2text
import calendar
import csv
from dateutil.parser import parse
from recordsearch_tools.client import RSSearchClient
import time

ROOT_URL = 'http://dfat.gov.au/about-us/publications/historical-documents/Pages/historical-documents.aspx'


def slugify(title):
    '''
    Turn index titles into a safe filename.
    '''
    return re.sub(r'\W+', '-', title.lower())


def find_naa_reference(text):
    item = None
    reference = None
    pattern = re.compile(r'\[\s*(?:AA|NAA|PM&C)\s*:\s*(.*)\]')
    try:
        reference = pattern.search(text).group(1)
    except AttributeError:
        pass
    else:
        parts = reference.split(',')
        if not parts:
            parts = reference.split(' ')
        if len(parts) > 1:
            series = parts[0].strip().replace(' ', '')
            control = parts[1].strip()
            client = RSSearchClient()
            client.search(series=series, control=control)
            if client.results:
                item = client.results[0]
                barcode = item['identifier']
                text = re.sub(r'\[(\s*(?:AA|NAA|PM&C)\s*:\s*.*)\]', r'[ [\g<1>](http://www.naa.gov.au/cgi-bin/Search?O=I&Number={}) ]'.format(barcode), text)
        reference = reference.encode('utf-8')
    return reference, item, text


def get_volumes():
    volumes = []
    response = requests.get(ROOT_URL)
    soup = BeautifulSoup(response.text)
    content = soup.find('div', class_='contentarea')
    links = content.find_all('a')
    for link in links:
        if 'Pages/volume' in link['href'] or 'Pages/default' in link['href']:
            volumes.append({'title': link.string.strip(), 'url': link['href']})
    return volumes


def get_volume(url):
    documents = []
    response = requests.get('http://dfat.gov.au/' + url)
    soup = BeautifulSoup(response.text)
    content = soup.find('div', class_='contentarea')
    links = content.find_all('a')
    # problem with vol 22
    if not links:
        content = soup.find('div', class_='webpart')
        links = content.find_all('a')
    for link in links:
        try:
            if '/Pages/' in link['href']:
                documents.append({'title': link.string.strip(), 'url': link['href']})
        except KeyError:
            with open('errors.txt', 'ab') as errors:
                errors.write('{}\n'.format(link.string.strip()))
    return documents


def get_document(url):
    document = {}
    # for vol 22
    if 'http://dfat.gov.au/' not in url:
        url = 'http://dfat.gov.au/' + url
    response = requests.get(url)
    soup = BeautifulSoup(response.content)
    try:
        document['title'] = soup.find('h1', class_='meta-title').string.strip()
    except AttributeError:
        # for volume 22
        with open('errors.txt', 'ab') as errors:
            errors.write('{}\n'.format(url))
    else:
        try:
            document['details'] = soup.find('p', class_='meta-article-additionalText').string.strip()
        except AttributeError:
            pass
        content = soup.find('div', class_='contentarea')
        parser = html2text.HTML2Text()
        parser.body_width = 0
        parser.unicode_snob = True
        text = parser.handle(unicode(content).replace('\n', ''))
        months = '|'.join(calendar.month_name[1:])
        date_pattern = re.compile(r'(\d{1,2}(?:th|rd|st|nd)*\s+(?:' + months + '),*\s+19\d{2})')
        if 'details' in document:
            dates = date_pattern.findall(document['details'])
            if not dates:
                dates = date_pattern.findall(text)
        else:
            dates = date_pattern.findall(text)
        if dates:
            try:
                document['date'] = parse(dates[0])
            except ValueError:
                document['date'] = None
        else:
            document['date'] = None
        reference, item, text = find_naa_reference(text)
        document['reference'] = reference
        if item:
            document['item'] = item
        document['text'] = text
    return document


def harvest_all():
    volumes = get_volumes()
    doc_id = 1
    for volume in volumes:
        vol_dir = os.path.join('volumes', slugify(volume['title']))
        vol_id = re.search(r'Volume (\d+):', volume['title']).group(1)
        if not os.path.exists(vol_dir):
            os.makedirs(vol_dir)
        documents = get_volume(volume['url'])
        for page in documents:
            doc_path = '{}.md'.format(os.path.join(vol_dir, slugify(page['title'])))
            if not os.path.exists(doc_path):
                document = get_document(page['url'])
                if document:
                    with open(doc_path, 'wb') as doc_file:
                        doc_file.write('---\n')
                        doc_file.write('title: "{}"\n'.format(document['title'].encode('utf-8')))
                        doc_file.write('volume: "{}"\n'.format(volume['title'].encode('utf-8')))
                        doc_file.write('doc_id: {}\n'.format(doc_id))
                        doc_file.write('vol_id: {}\n'.format(vol_id))
                        if document['date']:
                            isodate = document['date'].strftime('%Y-%m-%d')
                            doc_file.write('doc_date: {}\n'.format(isodate))
                        else:
                            isodate = None
                        barcode = document.get('item', {}).get('identifier')
                        series = document.get('item', {}).get('series')
                        control = document.get('item', {}).get('control_symbol')
                        if barcode:
                            doc_file.write('barcode: {}\n'.format(barcode))
                        doc_file.write('---\n\n')
                        doc_file.write('# {}\n\n'.format(document['title'].encode('utf-8')))
                        if 'details' in document:
                            doc_file.write('## {}\n\n'.format(document['details'].encode('utf-8')))
                        doc_file.write(document['text'].encode('utf-8'))
                        with open('documents.csv', 'ab') as csv_file:
                            writer = csv.writer(csv_file)
                            writer.writerow([doc_id, vol_id, document['title'].encode('utf-8'), volume['title'].encode('utf-8'), isodate, document['reference'], barcode, series, control])
                    time.sleep(0.5)
            doc_id += 1



