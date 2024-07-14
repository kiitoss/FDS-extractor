import os
import sys
import json
import csv
import pypdfium2 as pdfium

FOLDER = 'data'
CODES = 'clp-codes.csv'

def get_data(pdf_path, map_codes):
    pdf_name = pdf_path.replace('\\', '/')
    code = pdf_name.split('/')[-1].replace(' ', '_').replace('-', '_').split('_')[0]
    if '.pdf' in code:
        code = '???'

    data = {
        'pdf': pdf_name,
        'code': code,
        'labels': set()
    }

    try:
        pdf = pdfium.PdfDocument(pdf_path)
    except Exception as e:
        print(f'Error: {e}')
        return data
    
    page = pdf[0]
    textpage = page.get_textpage()

    for key, value in map_codes.items():
        if not value['has_picto']:
            continue

        searcher = textpage.search(key, match_case=True, match_whole_word=True)
        first_occurence = searcher.get_next()
        if first_occurence:
            data['labels'].add(value['category'])

    data['labels'] = list(data['labels'])

    return data

def get_all_pdf_paths(folder):
    pdf_paths = []

    for path, _, files in os.walk(folder):
        for name in files:
            if name.endswith('.pdf'):
                pdf_paths.append(os.path.join(path, name))
    
    return pdf_paths

def get_map_codes(csv_path, delimiter=','):
    map_codes = {}

    with open(csv_path, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=delimiter)
        next(reader, None)  # skip the headers
        for row in reader:
            map_codes[row[0].strip()] = {
                'category': row[1].strip(),
                'has_picto': row[2].strip() == "1"
            }
    
    return map_codes

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: python main.py <folder_path> <clp_codes_path>')
        sys.exit(1)

    folder_path = sys.argv[1]
    clp_codes_path = sys.argv[2]

    if not os.path.exists(folder_path):
        print(f'Error: Folder "{folder_path}" not found')
        sys.exit(1)
    
    if not os.path.exists(clp_codes_path):
        print(f'Error: File "{clp_codes_path}" not found')
        sys.exit(1)
    
    result = []
    
    pdf_paths = get_all_pdf_paths(folder_path)
    map_codes = get_map_codes(clp_codes_path)

    for pdf_path in pdf_paths:
        data = get_data(pdf_path, map_codes)
        result.append(data)
            
    print(json.dumps(result, indent=2))
    # json.dump(result, open('result.json', 'w'), indent=2)
