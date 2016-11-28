import csv
import re
from operator import itemgetter, attrgetter

# doc_id, vol_id, doc_title, vol_title, date, reference, barcode, series, control

# I should really figure out how to use Pandas for stuff like this...


def results_summary():
    total_references = 0
    total_barcodes = 0
    total_documents = 0
    total_dates = 0
    volumes = {}
    barcodes = {}
    references = []
    unmatched_references = []
    with open('documents.csv', 'rb') as documents:
        reader = csv.reader(documents)
        for row in reader:
            total_documents += 1
            try:
                volumes[row[3]]['total'] += 1
            except KeyError:
                vol_num = re.search(r'Volume (\d+):', row[3]).group(1)
                volumes[row[3]] = {}
                volumes[row[3]]['total'] = 1
                volumes[row[3]]['references'] = 0
                volumes[row[3]]['barcodes'] = 0
                volumes[row[3]]['number'] = int(vol_num)
                volumes[row[3]]['volume'] = row[3]
                volumes[row[3]]['dates'] = 0
            if row[4]:
                volumes[row[3]]['dates'] += 1
                total_dates += 1
            if row[5]:
                volumes[row[3]]['references'] += 1
                total_references += 1
                if row[5] not in references:
                    references.append(row[5])
            if row[6]:
                volumes[row[3]]['barcodes'] += 1
                total_barcodes += 1
                if row[6] not in barcodes:
                    barcodes[row[6]] = [row[6], row[7], row[8]]
            if row[5] and not row[6]:
                if row[5] not in unmatched_references:
                    unmatched_references.append(row[5])
    with open('barcodes.csv', 'wb') as barcodes_csv:
        barcodes = sorted(barcodes.values(), key=itemgetter(1, 2))
        for barcode in barcodes:
            writer = csv.writer(barcodes_csv)
            writer.writerow(barcode)
    with open('unmatched_references.txt', 'wb') as ref_file:
        for reference in sorted(unmatched_references):
            ref_file.write('{}\n'.format(reference))
    print '{} documents'.format(total_documents)
    print '{} dates found ({}% of documents)'.format(total_dates, int(round(float(total_dates) / total_documents * 100)))
    print '{} NAA references found ({}% of documents)'.format(total_references, int(round(float(total_references) / total_documents * 100)))
    print '{} NAA barcodes found ({}% of documents, {}% of references)'.format(total_barcodes, int(round(float(total_barcodes) / total_documents * 100)), int(round(float(total_barcodes) / total_references * 100)))
    print '{} unique NAA references found'.format(len(references))
    print '{} unique NAA barcodes found'.format(len(barcodes))
    volumes = sorted(volumes.values(), key=itemgetter('number'))
    for volume in volumes:
        print '\n{}:'.format(volume['volume'].upper())
        print '    {} documents'.format(volume['total'])
        print '    {} dates found ({}% of documents)'.format(volume['dates'], int(round(float(volume['dates']) / volume['total'] * 100)))
        print '    {} NAA references found ({}% of documents)'.format(volume['references'], int(round(float(volume['references']) / volume['total'] * 100)))
        try:
            print '    {} NAA barcodes found ({}% of documents, {}% of references)'.format(volume['barcodes'], int(round(float(volume['barcodes']) / volume['total'] * 100)), int(round(float(volume['barcodes']) / volume['references'] * 100)))
        except ZeroDivisionError:
            print '    0 NAA barcodes found (0% of documents 0% of references)'


def get_dates():
    totals = {}
    volumes = {}
    with open('documents.csv', 'rb') as documents:
        reader = csv.reader(documents)
        for row in reader:
            if row[4]:
                vol_id = re.search(r'Volume (\d+):', row[3]).group(1)
                try:
                    totals[row[4][:7]] += 1
                except KeyError:
                    totals[row[4][:7]] = 1
                try:
                    volumes[row[4][:7]][vol_id] += 1
                except KeyError:
                    try:
                        volumes[row[4][:7]][vol_id] = 1
                    except KeyError:
                        volumes[row[4][:7]] = {}
                        volumes[row[4][:7]][vol_id] = 1
    totals = [[month, total] for month, total in totals.items()]
    totals = sorted(totals, key=itemgetter(0))
    with open('dates.csv', 'wb') as dates_csv:
        writer = csv.writer(dates_csv)
        for total in totals:
            writer.writerow(total)
    volumes = [[month, vols] for month, vols in volumes.items()]
    volumes = sorted(volumes, key=itemgetter(0))
    with open('dates-byvol.csv', 'wb') as datesbyvol_csv:
        writer = csv.writer(datesbyvol_csv)
        header = ['Volume {}'.format(num) for num in range(1, 29)]
        header.insert(0, 'Month')
        writer.writerow(header)
        for month in volumes:
            row = [None] * 29
            row[0] = month[0]
            for vol, total in month[1].items():
                row[int(vol)] = total
            writer.writerow(row)

