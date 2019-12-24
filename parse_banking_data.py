import csv
import os
from argparse import ArgumentParser
from datetime import datetime

CSV_OUT_NAME = 'result.csv'
RESULT_FIELDNAMES = ['bank', 'date', 'type', 'amount', 'from', 'to']
FIELDNAMES_MAPPING = {
    'timestamp': 'date',
    'date_readable': 'date',
    'transaction': 'type',
    'amounts': 'amount',
    'euro': 'amount'
}
GENERAL_DATE_FORMAT = '%d %b %Y'
DATE_FORMATS = {
    'bank1.csv': '%b %d %Y',
    'bank2.csv': '%d-%m-%Y',
    'bank3.csv': '%d %b %Y',
}


class ParsingResultBuilder:
    def __init__(self, csv_list, *args, **kwargs):
        self.csv_list = csv_list
        super().__init__(*args, **kwargs)

    def concat_csv_files(self):
        raise NotImplemented


class CSVParsingResultBuilder(ParsingResultBuilder):
    def concat_csv_files(self):
        with open(CSV_OUT_NAME, 'w', newline='') as csv_out:
            writer = csv.DictWriter(f=csv_out, fieldnames=RESULT_FIELDNAMES, extrasaction='ignore')
            writer.writeheader()
            for file in self.csv_list:
                with open(file, newline='') as csv_file:
                    reader = csv.DictReader(csv_file)
                    rows = generalize_rows(reader, FIELDNAMES_MAPPING, csv_file.name,
                                           DATE_FORMATS.get(csv_file.name))
                    writer.writerows(rows)

    print(f'You can check the result in {CSV_OUT_NAME}')


class JSONParsingResultBuilder(ParsingResultBuilder):
    pass


class XMLParsingResultBuilder(ParsingResultBuilder):
    pass


def generalize_rows(reader, mapping, file_name, date_format=None):
    rows_list = []
    for row in reader:
        row = dict(row)
        row['bank'] = os.path.splitext(file_name)[0]

        for key in row.keys():
            if key in mapping.keys():
                if key == 'euro':
                    row[mapping.get(key)] = f'{row.pop(key)}.{row.get("cents")}'
                else:
                    row[mapping.get(key)] = row.pop(key)

        if date_format:
            row['date'] = datetime.strptime(row['date'], date_format).strftime(GENERAL_DATE_FORMAT)

        rows_list.append(row)
    return rows_list


def parse_csv_files(result_type='csv'):
    type_to_builder_mapper = {
        'csv': CSVParsingResultBuilder,
        'json': JSONParsingResultBuilder,
        'xml': XMLParsingResultBuilder
    }

    csv_dir = os.getcwd()
    dir_tree = next(os.walk(csv_dir))

    csv_list = []

    for filenames in dir_tree:
        for file in filenames:
            if file.endswith('.csv'):
                csv_list.append(file)

    ResultBuilder = type_to_builder_mapper.get(result_type, CSVParsingResultBuilder)
    ResultBuilder(csv_list).concat_csv_files()


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-t', '--type', dest='type',
                        help='which TYPE to use for representing the result', metavar='TYPE')

    parsed_args = parser.parse_args()
    parse_csv_files(result_type=parsed_args.get('type', 'csv').lower())
