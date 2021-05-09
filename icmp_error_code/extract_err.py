import csv, json
from os import listdir
from os.path import isfile, join, dirname, realpath

path = dirname(realpath(__file__))
files_csv = {str(f): join(path, f) for f in listdir(path) if isfile(join(path, f)) and '.csv' in f}
result = {}
for file_name, file_path in files_csv.items():
    a = {}
    with open(file_path, 'r') as f:
        csv_reader = csv.reader(f, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                print(f'Column names are {", ".join(row)}')
                line_count += 1
            else:
                if '-' in row[0]:
                    begin, end = row[0].split('-')
                    for i in range(int(begin), int(end)+1):
                        a[i] = str(row[1])
                else:
                    a[int(row[0])] = str(row[1])
                print(f'\t{row[0]} works in the {row[1]} department, and was born in {row[2]}.')
                line_count += 1
        print(f'Processed {line_count} lines.')
    result[int(file_name.replace('icmp-parameters-codes-', '').replace('.csv', ''))] = a
with open(path+'/error_codes.json','w+') as f:
    json.dump(result, f, ensure_ascii=False, indent=2, sort_keys=True)
