from skimage.metrics import structural_similarity as ssim

import pypdfium2 as pdfium
import fitz
import os
import PIL
import io 
import shutil
import cv2

IDENTIFIERS = {
    'name': 'Nom du produit',
    'code': 'Code du produit',
    'ufi': 'UFI'
}

def get_product_data(pdf_path, pages=[0]):
    pdf = pdfium.PdfDocument(pdf_path)
    version = pdf.get_version()
    n_pages = len(pdf)
    
    page = pdf[0]

    data = {}
    
    textpage = page.get_textpage()

    for key, value in IDENTIFIERS.items():
        searcher = textpage.search(value, match_case=False, match_whole_word=False)
        first_occurence = searcher.get_next()
        
        if (not first_occurence):
            data[key] = None
            continue
    
        index, count = first_occurence

        sentence = textpage.get_text_range(index, index + count).split('\n')[0]
        content = sentence.split(':')[-1].strip()
        data[key] = content

    return {
        'pdf': pdf_path,
        'version': version,
        'n_pages': n_pages,
        'data': data
    }

def extract_images(pdf_path, output_path, min_width, min_height):
    pdf = fitz.open(pdf_path)

    if os.path.exists(output_path):
        shutil.rmtree(output_path)
    os.makedirs(output_path)
    os.makedirs(f"{output_path}/skiped")
    
    page = pdf[0]
    
    # Get images (png, jpg...)
    images = page.get_images()
    if images:
        for i, img in enumerate(images, start=1):
            skiped = False
            
            width, height = img[2], img[3]
            
            if width < min_width or height < min_height:
                skiped = True

            data = pdf.extract_image(img[0])
            with PIL.Image.open(io.BytesIO(data.get('image'))) as image:
                output_filename = f"{output_path}/{"skiped/" if skiped else ""}image_{i+1}"
                image.save(f'{output_filename}.{data.get("ext")}', mode='wb')
    
    # Get drawings (svg...)
    drawings = page.get_drawings()
    if drawings:
        for i, drawing in enumerate(drawings):
            skiped = False
            
            bbox = drawing['rect']
            width, height = bbox[2] - bbox[0], bbox[3] - bbox[1]
            
            if width < min_width or height < min_height:
                skiped = True
            
            matrix = fitz.Matrix(1, 1)
            clip = fitz.Rect(bbox) 
            pix = page.get_pixmap(matrix=matrix, clip=clip)
            
            output_filename = f"{output_path}/{"skiped/" if skiped else ""}drawing_{i+1}.png"
            pix.save(output_filename)

def get_image_similarity(sift, imageA, imageB):
    # Find keypoints and descriptors with SIFT
    _, descriptorsA = sift.detectAndCompute(imageA, None)
    _, descriptorsB = sift.detectAndCompute(imageB, None)

    # FLANN parameters
    FLANN_INDEX_KDTREE = 1
    index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
    search_params = dict(checks=50)

    # Initialize the FLANN-based matcher
    flann = cv2.FlannBasedMatcher(index_params, search_params)

    # Match descriptors
    matches = flann.knnMatch(descriptorsA, descriptorsB, k=2)

    # Apply the ratio test
    good_matches = []
    for m, n in matches:
        if m.distance < 0.7 * n.distance:
            good_matches.append(m)
    
    if len(matches) == 0:
        similarity_score = 0
    else:
        similarity_score = len(good_matches) / len(matches)
    
    # Determine if the images are similar based on a threshold
    similarity_threshold = 0.2  # You can adjust this threshold
    return {
        'same': similarity_score > similarity_threshold,
        'score': similarity_score,
        'matches': len(good_matches),
        'total_matches': len(matches),
    }

def load_folder_images(folder_path):
    images = []
    for image in os.listdir(folder_path):
        image_path = os.path.join(folder_path, image)
        if not os.path.isfile(image_path):
            continue
        images.append({
            'name': image,
            'image': cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            })
    return images

def compare_all_images(extracted_images_path, pictos_path):
    picto_images = load_folder_images(pictos_path)
    images = load_folder_images(extracted_images_path)
    
    # Initialize the SIFT detector
    sift = cv2.SIFT_create()
    
    data = {}
    for image in images:
        image_data = {}
        for picto in picto_images:
            similarity = get_image_similarity(sift, image['image'], picto['image'])
            if not similarity['same']:
                continue
            image_data[picto['name']] = similarity

        if len(image_data) > 0:
            data[image['name']] =  image_data

    return data
