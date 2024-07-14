import os
import sys
import json
import csv
from typing import Dict, Set, List, Tuple, Union, NamedTuple
import pypdfium2 as pdfium


class PdfData(NamedTuple):
    code: str
    has_picto: bool


MapCodes = Dict[str, Dict[str, Union[str, bool]]]
PdfResult = Dict[str, Union[str, List[str], Set[str]]]


def extract_code_from_pdf_path(pdf_path: str) -> str:
    """Extracts the code from a PDF file path.

    Args:
    - pdf_path (str): The path of the PDF file

    Returns:
    - str: The extracted code (or "???" if not found)
    """
    DELIMITERS = ["_", "-", " "]
    CUSTOM_DELIMITER = "___"

    pdf_name = os.path.basename(pdf_path.replace("\\", "/"))

    for delimiter in DELIMITERS:
        pdf_name = pdf_name.replace(delimiter, CUSTOM_DELIMITER)

    return (
        pdf_name.split(CUSTOM_DELIMITER)[0] if CUSTOM_DELIMITER in pdf_name else "???"
    )


def process_pdf_data(pdf_path: str, map_codes: MapCodes, pages: List[int]=[0]) -> PdfResult:
    """Processes data from a PDF file based on provided map codes.

    Args:
    - pdf_path (str): The path of the PDF file
    - map_codes (MapCodes): Mapping of keywords to category and pictogram presence
    - pages (List[int], optional): List of page numbers to search for keywords (default: [0])

    Returns:
    - PdfResult: Dictionary containing 'pdf' path, 'code' of the PDF, and 'labels' found
    """
    code = extract_code_from_pdf_path(pdf_path)
    result: PdfResult = {"pdf": pdf_path, "code": code, "labels": set()}

    try:
        pdf = pdfium.PdfDocument(pdf_path)
    except Exception as e:
        print(f"Error opening PDF '{pdf_path}': {e}")
        return result

    for id_page in pages:
        page = pdf[id_page]
        textpage = page.get_textpage()

        for keyword, info in map_codes.items():
            if not info.get("has_picto", False):
                continue

            searcher = textpage.search(keyword, match_case=True, match_whole_word=True)
            first_occurrence = searcher.get_next()
            if first_occurrence:
                result["labels"].add(info["category"])

    result["labels"] = list(result["labels"])

    return result


def get_all_pdf_paths(folder_path: str) -> List[str]:
    """Recursively collects all PDF file paths within a folder.

    Args:
    - folder_path (str): The path of the folder to search

    Returns:
    - List[str]: List of paths to PDF files found
    """
    pdf_paths = []

    for path, _, files in os.walk(folder_path):
        for name in files:
            if name.endswith(".pdf"):
                pdf_paths.append(os.path.join(path, name))

    return pdf_paths


def load_map_codes(csv_path: str, delimiter: str = ",") -> MapCodes:
    """Loads CLP codes from a CSV file into a dictionary.

    Args:
    - csv_path (str): The path of the CSV file containing CLP codes
    - delimiter (str, optional): Delimiter used in the CSV file (default: ",")

    Returns:
    - MapCodes: Dictionary mapping keywords to category and pictogram presence
    """
    map_codes = {}

    with open(csv_path, newline="") as csvfile:
        reader = csv.reader(csvfile, delimiter=delimiter)
        next(reader, None)  # skip headers
        for row in reader:
            map_codes[row[0].strip()] = {
                "category": row[1].strip(),
                "has_picto": row[2].strip() == "1",
            }

    return map_codes


def parse_command_line_args() -> Tuple[str, str]:
    """Parses command line arguments and returns folder and CLP codes CSV file paths.

    Returns:
    - Tuple[str, str]: Folder path and CLP codes CSV file path
    """
    if len(sys.argv) < 3:
        print("Usage: python main.py <folder_path> <clp_codes_path>")
        sys.exit(1)

    folder_path = sys.argv[1]
    clp_codes_path = sys.argv[2]

    if not os.path.exists(folder_path):
        print(f'Error: Folder "{folder_path}" not found')
        sys.exit(1)

    if not os.path.exists(clp_codes_path):
        print(f'Error: File "{clp_codes_path}" not found')
        sys.exit(1)

    return folder_path, clp_codes_path


if __name__ == "__main__":
    folder_path, clp_codes_path = parse_command_line_args()

    pdf_results = []

    pdf_paths = get_all_pdf_paths(folder_path)
    map_codes = load_map_codes(clp_codes_path)

    for pdf_path in pdf_paths:
        result = process_pdf_data(pdf_path, map_codes)
        pdf_results.append(result)

    print(json.dumps(pdf_results, indent=2))
