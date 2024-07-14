from os import listdir
import json
import time

import extractor

PICTOS_PATH = "./picto"
SCALE_PERCENT = 100
DPI = 300
FOLDER = "data"
EXTRACTED_IMAGES_FOLDER = "extracted_images"

MIN_WIDTH = 20
MIN_HEIGHT = 20


def remove_duplicates(array_of_arrays):
    # Convert each sub-array to a tuple and add to a set to remove duplicates
    unique_arrays = set(tuple(sub_array) for sub_array in array_of_arrays)

    # Convert the set of tuples back to a list of lists
    unique_arrays = [list(sub_array) for sub_array in unique_arrays]

    return unique_arrays


if __name__ == "__main__":
    result = []

    initial_time = time.time()

    for pdf in listdir(FOLDER):
        time_1 = time.time()

        path = FOLDER + "/" + pdf
        print(f'--> Processing "{pdf}"...')

        data = extractor.get_product_data(path)

        output_path = EXTRACTED_IMAGES_FOLDER + "/" + pdf
        extractor.extract_images(path, output_path, MIN_WIDTH, MIN_HEIGHT)

        comparisons = extractor.compare_all_images(output_path, PICTOS_PATH)

        possibles = []
        for img_index, value in comparisons.items():
            nb_pictos = len(value)
            if nb_pictos > 0:
                possible = []
                for picto_index in value.keys():
                    possible.append(picto_index)
                possibles.append(possible)
            else:
                possibles.append(value[0].keys())

        data["pictos"] = remove_duplicates(possibles)

        result.append(data)

        print(f"--> Done in {time.time() - time_1:.2f}s\n")

    print("Total time:", time.time() - initial_time)
    print(json.dumps(result, indent=2))
    json.dump(result, open("result.json", "w"), indent=2)
