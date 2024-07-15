import os
import csv
import pypdfium2 as pdfium

CODES = [
    "H200",
    "H201",
    "H202",
    "H203",
    "H204",
    "H205",
    "H206",
    "H207",
    "H208",
    "H220",
    "H221",
    "H222",
    "H223",
    "H224",
    "H225",
    "H226",
    "H228",
    "H229",
    "H230",
    "H231",
    "H232",
    "H240",
    "H241",
    "H241",
    "H242",
    "H250",
    "H251",
    "H252",
    "H260",
    "H261",
    "H270",
    "H271",
    "H272",
    "H280",
    "H281",
    "H290",
    "H300",
    "H301",
    "H302",
    "H304",
    "H310",
    "H311",
    "H312",
    "H314",
    "H315",
    "H317",
    "H318",
    "H319",
    "H330",
    "H331",
    "H332",
    "H334",
    "H335",
    "H336",
    "H340",
    "H341",
    "H350",
    "H350i",
    "H351",
    "H360",
    "H360F",
    "H360D",
    "H360FD",
    "H360Fd",
    "H360Df",
    "H361",
    "H361f",
    "H361d",
    "H361fd",
    "H362",
    "H370",
    "H371",
    "H372",
    "H373",
    "H400",
    "H410",
    "H411",
    "H412",
    "H413",
    "H420",
]


def extract_code_from_pdf_path(pdf_path: str) -> str:
    DELIMITERS = ["_", "-", " "]
    CUSTOM_DELIMITER = "___"

    pdf_name = os.path.basename(pdf_path.replace("\\", "/"))

    for delimiter in DELIMITERS:
        pdf_name = pdf_name.replace(delimiter, CUSTOM_DELIMITER)

    return (
        pdf_name.split(CUSTOM_DELIMITER)[0] if CUSTOM_DELIMITER in pdf_name else "???"
    )


def get_pdf_data(pdf_path: str, pages: [int] = [0]):
    code = extract_code_from_pdf_path(pdf_path)
    result = {"pdf": pdf_path, "code": code, "labels": set()}

    try:
        pdf = pdfium.PdfDocument(pdf_path)
    except Exception as e:
        print(f"Error opening PDF '{pdf_path}': {e}")
        return result

    for id_page in pages:
        page = pdf[id_page]
        textpage = page.get_textpage()

        for keyword in CODES:
            searcher = textpage.search(keyword, match_case=True, match_whole_word=True)
            first_occurrence = searcher.get_next()
            if first_occurrence:
                result["labels"].add(keyword)

    result["labels"] = list(result["labels"])

    return result


def get_all_pdf_paths(folder_path: str) -> [str]:
    pdf_paths = []

    for path, _, files in os.walk(folder_path):
        for name in files:
            if name.endswith(".pdf"):
                pdf_paths.append(os.path.join(path, name))

    return pdf_paths


def extract_data(folder_path: str):
    pdf_paths = get_all_pdf_paths(folder_path)
    data = [get_pdf_data(pdf_path) for pdf_path in pdf_paths]

    with open(f"{folder_path}/labels.csv", mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["pdf", "code", "label"])
        for entry in data:
            for label in entry["labels"]:
                writer.writerow([entry["pdf"], entry["code"], label])

    with open(f"{folder_path}/detailed_labels.csv", mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["pdf", "code"] + CODES)
        for entry in data:
            row = [entry["pdf"], entry["code"]]
            row.extend([1 if label in entry["labels"] else 0 for label in CODES])
            writer.writerow(row)
