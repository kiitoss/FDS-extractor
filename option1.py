import cv2
import glob
import fitz
import os
import shutil
import numpy as np

def extract_images_from_pdf(pdf_path, output_folder):
    # Open the PDF file
    pdf_document = fitz.open(pdf_path)

    if os.path.exists(output_folder):
        shutil.rmtree(output_folder)

    os.makedirs(output_folder)
    

    # Iterate through each page
    for page_number in range(len(pdf_document)):
        page = pdf_document[page_number]
        image_list = page.get_images(full=True)

        # print(page.get_text("dict"))
        # print(page.get_drawings())


        # Iterate through each image on the page
        for image_index, img in enumerate(image_list):
            width, height = img[2], img[3]
            colorspace = img[5]

            if (width <= 5 or height <= 5):
                print(f"Skipping small image (width: {width}, height: {height})")
                continue
            
            if colorspace == 'DeviceGray':
                print("Skipping grayscale image")
                continue
            
            xref = img[0]
            base_image = pdf_document.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            image_filename = f"page_{page_number + 1}_image_{image_index + 1}.{image_ext}"
            image_filepath = os.path.join(output_folder, image_filename)
            
            # Save the image
            with open(image_filepath, "wb") as image_file:
                image_file.write(image_bytes)


def compare_images(img1_path, img2_path):
    img1 = cv2.imread(img1_path, cv2.IMREAD_COLOR)
    img2 = cv2.imread(img2_path, cv2.IMREAD_COLOR)

    if img1 is None or img2 is None:
        print(f"Error loading images: {img1_path}, {img2_path}")
        return 0.0

    # Resize images to the same size
    dim = (150, 150)
    img1 = cv2.resize(img1, dim)
    img2 = cv2.resize(img2, dim)

    # Compute structural similarity
    score = cv2.norm(img1, img2, cv2.NORM_L2)
    normalized_score = 1 - score / (dim[0] * dim[1])

    return normalized_score

def compare_extracted_images_with_picto(extracted_folder, picto_folder):
    extracted_images = glob.glob(os.path.join(extracted_folder, "*.*"))
    picto_images = glob.glob(os.path.join(picto_folder, "*.*"))

    for extracted_image in extracted_images:
        for picto_image in picto_images:
            similarity = compare_images(extracted_image, picto_image)
            if similarity > 0.5:  # Example threshold for considering images as identical
                print(f"Extracted image {os.path.basename(extracted_image)} is similar to {os.path.basename(picto_image)} with confidence {similarity*100:.2f}%")

if __name__ == "__main__":
    pdf_path = "data/fds-2.pdf"
    output_folder = "extracted_images"
    extract_images_from_pdf(pdf_path, output_folder)

    extracted_folder = "extracted_images"
    picto_folder = "picto"
    compare_extracted_images_with_picto(extracted_folder, picto_folder)
