import os
import fitz
import cv2
import numpy as np

def convert_pdf_to_images(pdf_path, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    doc = fitz.open(pdf_path)
    pages = []
    for i in range(len(doc)):
        page = doc[i]
        pix = page.get_pixmap()
        pages.append(pix)
    page_image_paths = []
    for i, page in enumerate(pages):
        page_path = os.path.join(output_folder, f'page_{i+1}.png')
        page.save(page_path, 'PNG')
        page_image_paths.append(page_path)
    return page_image_paths

def match_pictograms_to_pages(page_image_paths, picto_folder):
    picto_files = [os.path.join(picto_folder, f) for f in os.listdir(picto_folder) if os.path.isfile(os.path.join(picto_folder, f))]
    matches = {}

    for picto_file in picto_files:
        picto_img = cv2.imread(picto_file, cv2.IMREAD_GRAYSCALE)
        picto_name = os.path.basename(picto_file)
        matches[picto_name] = []

        for page_path in page_image_paths:
            page_img = cv2.imread(page_path, cv2.IMREAD_GRAYSCALE)

            # Perform template matching
            result = cv2.matchTemplate(page_img, picto_img, cv2.TM_CCOEFF_NORMED)
            threshold = 0.8  # You can adjust this threshold
            loc = np.where(result >= threshold)

            if len(loc[0]) > 0:
                page_num = int(os.path.basename(page_path).split('_')[1].split('.')[0])
                matches[picto_name].append(page_num)

    return matches

# Example usage
pdf_path = "data/fds-1.pdf"
output_folder = "extracted_images"
picto_folder = "picto"

# Convert PDF pages to images
page_image_paths = convert_pdf_to_images(pdf_path, output_folder)

# Match pictograms to PDF pages
matches = match_pictograms_to_pages(page_image_paths, picto_folder)

# Print the results
for picto, pages in matches.items():
    print(f"Pictogram {picto} found on pages: {sorted(set(pages))}")
