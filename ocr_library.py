'''
Code formally written by Alexander James Porter (Contact: AlexanderPorter1234@gmail.com) 20/02/2023
Code has been optimised for reading screenshots of final scoreboard in the game VALORANT
Lots of code is utilised from https://github.com/eihli/image-table-ocr#org67b1fc2
'''
import csv
import math
import difflib
import cv2
import numpy as np
import pytesseract
import logging
from agent_recognition import find_matching_agent, load_images_from_folder
from ocr_improvements import enhanced_ocr

#Setting up tesseract - only needs this if you have directly installed tesseract (I think).
pytesseract.pytesseract.tesseract_cmd = "tesseract"


class functions:

    def get_most_similar(ocr_result, possible_names):
        """Finds the closest match for an OCR result from a list of possible names."""
        closest_match = difflib.get_close_matches(ocr_result, possible_names, n=1, cutoff=0.5)
        return closest_match[0] if closest_match else "Unknown"

    def find_map_name(image, maps):
        """
        Recognizes the map name from a VALORANT scoreboard screenshot.

        Args:
            image: Preprocessed OpenCV image.

        Returns:
            str: Recognized map name or "Unknown" if not found.
        """
        # Apply thresholding to enhance text visibility
        _, thresh = cv2.threshold(image, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # Define a region where the map name is typically located (top-left area)
        map_region = thresh[60:140, 60:300]  # Adjusted for standard VALORANT scoreboard

        # Use Tesseract OCR to extract text
        custom_config = r'--psm 6'  # PSM 6 treats text as a block
        extracted_text = pytesseract.image_to_string(map_region, config=custom_config, lang='eng')
        # print(f"OCR Extracted Text: '{extracted_text.strip()}'") Debug Prints

        # Process extracted text and find a valid map name
        # Remove newlines
        extracted_map_name = extracted_text.replace("\n", " ").strip()
        # Extract only the last word after "MAP - "
        if "MAP -" in extracted_map_name:
            extracted_map_name = extracted_map_name.split("MAP -")[-1].strip()
         # print(f"Extracted Map Name: '{extracted_map_name}'") Debug Prints

        # Apply fuzzy matching to correct OCR errors
        corrected_map_name = functions.get_most_similar(extracted_map_name.capitalize(), maps)
        # print(f"Corrected Map Name: '{corrected_map_name}'") Debug Prints

        return corrected_map_name

    def find_tables(image, image_colored):
        """
        Given an input image, detects and extracts tables from the image.

        Parameters:
        image (numpy.ndarray): Input image

        Returns:
        tables (List[numpy.ndarray]): List of extracted tables

        """
        BLUR_KERNEL_SIZE = (3, 3)
        STD_DEV_X_DIRECTION = 0
        STD_DEV_Y_DIRECTION = 0
        blurred = cv2.GaussianBlur(image, BLUR_KERNEL_SIZE, STD_DEV_X_DIRECTION, STD_DEV_Y_DIRECTION)
        MAX_COLOR_VAL = 255
        BLOCK_SIZE = 15
        SUBTRACT_FROM_MEAN = -2

        img_bin = cv2.adaptiveThreshold(
            ~blurred,
            MAX_COLOR_VAL,
            cv2.ADAPTIVE_THRESH_MEAN_C,
            cv2.THRESH_BINARY,
            BLOCK_SIZE,
            SUBTRACT_FROM_MEAN,
        )
        vertical = horizontal = img_bin.copy()
        SCALE = 5
        image_width, image_height = horizontal.shape
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (int(image_width / SCALE), 1))
        horizontally_opened = cv2.morphologyEx(img_bin, cv2.MORPH_OPEN, horizontal_kernel)
        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, int(image_height / SCALE)))
        vertically_opened = cv2.morphologyEx(img_bin, cv2.MORPH_OPEN, vertical_kernel)

        horizontally_dilated = cv2.dilate(horizontally_opened, cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1)))
        vertically_dilated = cv2.dilate(vertically_opened, cv2.getStructuringElement(cv2.MORPH_RECT, (1, 60)))

        mask = horizontally_dilated + vertically_dilated
        contours, heirarchy = cv2.findContours(
            mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE,
        )

        MIN_TABLE_AREA = 1e5
        contours = [c for c in contours if cv2.contourArea(c) > MIN_TABLE_AREA]
        perimeter_lengths = [cv2.arcLength(c, True) for c in contours]
        epsilons = [0.1 * p for p in perimeter_lengths]
        approx_polys = [cv2.approxPolyDP(c, e, True) for c, e in zip(contours, epsilons)]
        bounding_rects = [cv2.boundingRect(a) for a in approx_polys]

        # The link where a lot of this code was borrowed from recommends an
        # additional step to check the number of "joints" inside this bounding rectangle.
        # A table should have a lot of intersections. We might have a rectangular image
        # here though which would only have 4 intersections, 1 at each corner.
        # Leaving that step as a future TODO if it is ever necessary.
        images = [image[y:y+h, x:x+w] for x, y, w, h in bounding_rects]
        images_colored = [image_colored[y:y+h, x:x+w] for x, y, w, h in bounding_rects]
        return images[0], images_colored[0]

    def extract_cell_images_from_table(image,image_colored):
        """
        Extracts cell images from a table image.

        Parameters:
        image (numpy.ndarray): A table image.

        Returns:
        cell_images_rows (list): A list of lists containing numpy.ndarray representing cell images.
        """
        BLUR_KERNEL_SIZE = (1, 1)
        STD_DEV_X_DIRECTION = 0
        STD_DEV_Y_DIRECTION = 0
        blurred = cv2.GaussianBlur(image, BLUR_KERNEL_SIZE, STD_DEV_X_DIRECTION, STD_DEV_Y_DIRECTION)
        MAX_COLOR_VAL = 255
        BLOCK_SIZE = 13
        SUBTRACT_FROM_MEAN = -1

        img_bin = cv2.adaptiveThreshold(
            ~blurred,
            MAX_COLOR_VAL,
            cv2.ADAPTIVE_THRESH_MEAN_C,
            cv2.THRESH_BINARY,
            BLOCK_SIZE,
            SUBTRACT_FROM_MEAN,
        )
        vertical = horizontal = img_bin.copy()
        SCALE = 9
        image_width, image_height = horizontal.shape
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (int(image_width / SCALE), 1))
        horizontally_opened = cv2.morphologyEx(img_bin, cv2.MORPH_OPEN, horizontal_kernel)
        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, int(image_height / SCALE)))
        vertically_opened = cv2.morphologyEx(img_bin, cv2.MORPH_OPEN, vertical_kernel)

        horizontally_dilated = cv2.dilate(horizontally_opened, cv2.getStructuringElement(cv2.MORPH_RECT, (1038, 1)))
        vertically_dilated = cv2.dilate(vertically_opened, cv2.getStructuringElement(cv2.MORPH_RECT, (1, 60)))

        mask = horizontally_dilated + vertically_dilated
        contours, heirarchy = cv2.findContours(
            mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE,
        )

        perimeter_lengths = [cv2.arcLength(c, True) for c in contours]
        epsilons = [0.05 * p for p in perimeter_lengths]
        approx_polys = [cv2.approxPolyDP(c, e, True) for c, e in zip(contours, epsilons)]

        # Filter out contours that aren't rectangular. Those that aren't rectangular
        # are probably noise.
        approx_rects = [p for p in approx_polys if len(p) == 4]
        bounding_rects = [cv2.boundingRect(a) for a in approx_polys]

        # Filter out rectangles that are too narrow or too short.
        MIN_RECT_WIDTH = 40
        MIN_RECT_HEIGHT = 10
        bounding_rects = [
            r for r in bounding_rects if MIN_RECT_WIDTH < r[2] and MIN_RECT_HEIGHT < r[3]
        ]

        # The largest bounding rectangle is assumed to be the entire table.
        # Remove it from the list. We don't want to accidentally try to OCR
        # the entire table.
        largest_rect = max(bounding_rects, key=lambda r: r[2] * r[3])
        bounding_rects = [b for b in bounding_rects if b is not largest_rect]

        cells = [c for c in bounding_rects]
        def cell_in_same_row(c1, c2):
            c1_center = c1[1] + c1[3] - c1[3] / 2
            c2_bottom = c2[1] + c2[3]
            c2_top = c2[1]
            return c2_top < c1_center < c2_bottom

        orig_cells = [c for c in cells]
        rows = []
        while cells:
            first = cells[0]
            rest = cells[1:]
            cells_in_same_row = sorted(
                [
                    c for c in rest
                    if cell_in_same_row(c, first)
                ],
                key=lambda c: c[0]
            )

            row_cells = sorted([first] + cells_in_same_row, key=lambda c: c[0])
            rows.append(row_cells)
            cells = [
                c for c in rest
                if not cell_in_same_row(c, first)
            ]

        # Sort rows by average height of their center.
        def avg_height_of_center(row):
            centers = [y + h - h / 2 for x, y, w, h in row]
            return sum(centers) / len(centers)

        rows.sort(key=avg_height_of_center)
        cell_images_rows = []
        headshot_images_rows = []
        for row in rows:
            cell_images_row = []
            headshot_images_row = []
            for x, y, w, h in row:
                headshot_offset = 55
                headshot_images_row.append(image_colored[y:y+h, x:x+headshot_offset])
                offset = 55
                x = x + offset
                w = w - offset
                cell_images_row.append(image[y:y+h, x:x+w])
            cell_images_rows.append(cell_images_row)
            headshot_images_rows.append(headshot_images_row)


        # return
        return cell_images_rows, headshot_images_rows

    def crop_to_text(image):
        """
        Crop an image to contain only the text region.

        Args:
            image: An input grayscale image.

        Returns:
            A cropped grayscale image containing only the text region.
        """
        MAX_COLOR_VAL = 255
        BLOCK_SIZE = 15
        SUBTRACT_FROM_MEAN = -2

        img_bin = cv2.adaptiveThreshold(
            ~image,
            MAX_COLOR_VAL,
            cv2.ADAPTIVE_THRESH_MEAN_C,
            cv2.THRESH_BINARY,
            BLOCK_SIZE,
            SUBTRACT_FROM_MEAN,
        )

        img_h, img_w = image.shape
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (int(img_w * 0.5), 1))
        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, int(img_h * 0.7)))
        horizontal_lines = cv2.morphologyEx(img_bin, cv2.MORPH_OPEN, horizontal_kernel)
        vertical_lines = cv2.morphologyEx(img_bin, cv2.MORPH_OPEN, vertical_kernel)
        both = horizontal_lines + vertical_lines
        cleaned = img_bin - both

        # Get rid of little noise.
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        opened = cv2.morphologyEx(cleaned, cv2.MORPH_OPEN, kernel)
        opened = cv2.dilate(opened, kernel)

        contours, hierarchy = cv2.findContours(opened, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        bounding_rects = [cv2.boundingRect(c) for c in contours]
        NUM_PX_COMMA = 6
        MIN_CHAR_AREA = 5 * 9
        char_sized_bounding_rects = [(x, y, w, h) for x, y, w, h in bounding_rects if w * h > MIN_CHAR_AREA]
        if char_sized_bounding_rects:
            minx, miny, maxx, maxy = math.inf, math.inf, 0, 0
            for x, y, w, h in char_sized_bounding_rects:
                minx = min(minx, x)
                miny = min(miny, y)
                maxx = max(maxx, x + w)
                maxy = max(maxy, y + h)
            x, y, w, h = minx, miny, maxx - minx, maxy - miny
            cropped = image[y:min(img_h, y+h+NUM_PX_COMMA), x:min(img_w, x+w)]
        else:
            # If we morphed out all of the text, assume an empty image.
            cropped = MAX_COLOR_VAL * np.ones(shape=(20, 100), dtype=np.uint8)
        bordered = cv2.copyMakeBorder(cropped, 5, 5, 5, 5, cv2.BORDER_CONSTANT, None, 255)
        return bordered

    def image_process(image):

        """
        Applies a series of image processing techniques to enhance the visibility of text in an image.

        Args:
            image: A NumPy array representing an image.

        Returns:
            A NumPy array representing the processed image.

        Raises:
            None
        """
        # Resize the image to make the text more visible
        scale_percent = 1000 # Increase the size by 1000%
        width = int(image.shape[1] * scale_percent / 100)
        height = int(image.shape[0] * scale_percent / 100)
        dim = (width, height)
        rs_image = cv2.resize(image, dim, interpolation = cv2.INTER_AREA)

        # Define the kernel size for dilation
        kernel = np.ones((5, 5), np.uint8)

        # Apply dilation on the grayscale image
        dilated = cv2.dilate(rs_image, kernel, iterations=1)

        # Apply Gaussian Blur to reduce noise in the image
        blurred = cv2.GaussianBlur(dilated, (3, 3), 0)

        # Apply thresholding to the grayscale image
        threshold = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

        #Remove noise
        no_noise = cv2.medianBlur(threshold,9)

        inverted_image = cv2.bitwise_not(no_noise)

        #write out image
        return inverted_image

    def ocr_image(image: np.ndarray, config: str = '', lang: str = '') -> str:
        """
        Perform OCR (Optical Character Recognition) on an image using Tesseract.

        Args:
            image (numpy.ndarray): The image to perform OCR on.
            config (str): Optional Tesseract configuration parameters.
            lang (str): Optional language code for Tesseract to use.

        Returns:
            str: The recognized text in the image.
        """
        return pytesseract.image_to_string(
            image,
            config=config,
            lang=lang
        )

    def row_seperator(image, BLUR_KERNEL_SIZE_input):
        """
        Separates the rows of a table in an image using various computer vision techniques.

        Args:
        - image: The input image in which to detect the table rows.

        Returns:
        - cells: A list of bounding rectangles representing the cells of the table.
        """
        BLUR_KERNEL_SIZE = BLUR_KERNEL_SIZE_input
        STD_DEV_X_DIRECTION = 0
        STD_DEV_Y_DIRECTION = 0
        blurred = cv2.GaussianBlur(image, BLUR_KERNEL_SIZE, STD_DEV_X_DIRECTION, STD_DEV_Y_DIRECTION)
        MAX_COLOR_VAL = 255
        BLOCK_SIZE = 11
        SUBTRACT_FROM_MEAN = -1

        img_bin = cv2.adaptiveThreshold(
            ~blurred,
            MAX_COLOR_VAL,
            cv2.ADAPTIVE_THRESH_MEAN_C,
            cv2.THRESH_BINARY,
            BLOCK_SIZE,
            SUBTRACT_FROM_MEAN,
        )
        #cv2.imwrite('yoyo.png',img_bin)
        vertical = horizontal = img_bin.copy()
        SCALE = 20
        image_width, image_height = horizontal.shape
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (int(image_width / SCALE), 1))
        horizontally_opened = cv2.morphologyEx(img_bin, cv2.MORPH_OPEN, horizontal_kernel)
        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, int(image_height / SCALE)))
        vertically_opened = cv2.morphologyEx(img_bin, cv2.MORPH_OPEN, vertical_kernel)

        horizontally_dilated = cv2.dilate(horizontally_opened, cv2.getStructuringElement(cv2.MORPH_RECT, (1038, 1)))
        vertically_dilated = cv2.dilate(vertically_opened, cv2.getStructuringElement(cv2.MORPH_RECT, (1, 60)))

        mask = horizontally_dilated + vertically_dilated
        contours, heirarchy = cv2.findContours(
            img_bin, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE,
        )

        perimeter_lengths = [cv2.arcLength(c, True) for c in contours]
        epsilons = [0.05 * p for p in perimeter_lengths]
        approx_polys = [cv2.approxPolyDP(c, e, True) for c, e in zip(contours, epsilons)]

        # Filter out contours that aren't rectangular. Those that aren't rectangular
        # are probably noise.
        approx_rects = [p for p in approx_polys if len(p) == 4]
        bounding_rects = [cv2.boundingRect(a) for a in approx_polys]


        # Filter out rectangles that are too narrow or too short.
        MIN_RECT_WIDTH = 9
        MIN_RECT_HEIGHT = 14
        bounding_rects = [
            r for r in bounding_rects if MIN_RECT_WIDTH < r[2] and MIN_RECT_HEIGHT < r[3]
        ]

        # The largest bounding rectangle is assumed to be the entire table.
        # Remove it from the list. We don't want to accidentally try to OCR
        # the entire table.
        largest_rect = max(bounding_rects, key=lambda r: r[2] * r[3])
        bounding_rects = [b for b in bounding_rects if b is not largest_rect]

        #Filter out the smallest rectangle that overlaps with another
        bounding_rects=functions.get_non_overlapping_rectangles(bounding_rects)

        cells = [c for c in bounding_rects]

        return cells

    def image_resize(image: np.ndarray, scale_percent: int) -> np.ndarray:
        """
        Resizes the input image by a given scale percentage.

        Args:
            image: A numpy array representing an image.
            scale_percent: An integer value indicating the percentage to scale the image by.

        Returns:
            A numpy array representing the resized image.
        """

        # Resize the image to make the text more visible
        scale_percent = scale_percent
        width = int(image.shape[1] * scale_percent / 100)
        height = int(image.shape[0] * scale_percent / 100)
        dim = (width, height)
        resized_image = cv2.resize(image, dim, interpolation = cv2.INTER_AREA)
        return resized_image

    def get_non_overlapping_rectangles(rectangles):
        """
        Given a list of rectangles, returns a list of non-overlapping rectangles.

        Parameters:
        rectangles (list): A list of tuples representing the rectangles, with each tuple containing four values:
                            the x-coordinate of the top-left corner, the y-coordinate of the top-left corner,
                            the width of the rectangle, and the height of the rectangle.

        Returns:
        list: A list of tuples representing the non-overlapping rectangles, with each tuple containing four values:
              the x-coordinate of the top-left corner, the y-coordinate of the top-left corner,
              the width of the rectangle, and the height of the rectangle.
        """
        non_overlapping_rectangles = []
        overlapping_rectangles = []
        for i, rect1 in enumerate(rectangles):
            overlaps = False
            for j, rect2 in enumerate(rectangles):
                if i != j:
                    if rect1[0] < rect2[0] + rect2[2] and rect1[0] + rect1[2] > rect2[0] and rect1[1] < rect2[1] + rect2[3] and rect1[1] + rect1[3] > rect2[1]:
                        overlaps = True
                        if rect1[2] * rect1[3] > rect2[2] * rect2[3]:
                            larger_rect = rect1
                            smaller_rect = rect2
                        else:
                            larger_rect = rect2
                            smaller_rect = rect1
                        break
            if overlaps:
                overlapping_rectangles.append(smaller_rect)
            else:
                non_overlapping_rectangles.append(rect1)
                larger_rect = rect1
            non_overlapping_rectangles.append(larger_rect)
        for rect in overlapping_rectangles:
            if rect in non_overlapping_rectangles:
                non_overlapping_rectangles.remove(rect)
        non_overlapping_rectangles = list(set(non_overlapping_rectangles))
        return non_overlapping_rectangles

    def read_table_rows(cell_images_rows, headshot_images_rows=None):
        """
        Reads each player's stats from a table represented by a list of rows images.
        Enhanced with leet speak detection and highlighted player recognition.

        Parameters:
        cell_image_rows (list): A list of rows images, each containing cells representing a player's stats.
        headshot_images_rows (list): A list of headshot images for highlighted player detection.

        Returns:
        output (list): A list of lists, where each sublist contains the player's name and stats in string format.
        """
        n=0
        output=[]
        scale = 10
        logging.info("Reading each players stats with enhanced OCR, please wait.")
        
        for i, row in enumerate(cell_images_rows):
            temp_output=[]
            n+=1
            # cv2.imwrite("debug/test_rows" +str(n) + ".png", row[0]) # for debugging
            image=row[0]
            
            # Check if this player is highlighted (yellow background)
            is_highlighted = False
            if headshot_images_rows and i < len(headshot_images_rows):
                try:
                    is_highlighted, _ = enhanced_ocr.detect_highlighted_player(
                        headshot_images_rows[i][0], row
                    )
                    if is_highlighted:
                        logging.info(f"Detected highlighted player in row {n}")
                except Exception as e:
                    logging.warning(f"Failed to detect highlighting for row {n}: {e}")

            #Seperate rows
            cells=functions.row_seperator(image,(9,9))
            cells=sorted(cells,key=lambda x:x[0])

            #Seperate the cells
            cells = [c for c in cells if c[0] > (0.24*(row[0].shape[1]))]

            #Get cells again if did not capture them all
            if len(cells) != 8:
                cells=functions.row_seperator(image,(11,11))
                cells=sorted(cells,key=lambda x:x[0])
                cells = [c for c in cells if c[0] > (0.24*(row[0].shape[1]))]

            #Process image for OCR
            image=functions.image_process(image)
            name_region=image[0:100*scale,0:300*scale]
            
            # Enhanced name OCR with leet speak detection
            try:
                # Preprocess the name image
                processed_name = enhanced_ocr.preprocess_name_image(name_region, is_highlighted)
                
                # Use enhanced OCR
                ocr_name = enhanced_ocr.enhanced_ocr_name(processed_name, is_highlighted)
                
                if not ocr_name or ocr_name.strip() == "":
                    # Fallback to original method
                    ocr_name = functions.ocr_image(
                        name_region,
                        '-c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789/_ --psm 7',
                        'eng+kor+jpn+chi_sim'
                    )
                    
            except Exception as e:
                logging.warning(f"Enhanced OCR failed for row {n}, using fallback: {e}")
                # Fallback to original OCR
                ocr_name = functions.ocr_image(
                    name_region,
                    '-c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789/_ --psm 7',
                    'eng+kor+jpn+chi_sim'
                )
            
            if str(ocr_name).strip() == "":
                ocr_name = "err"
            
            # Add highlighting indicator to name if detected
            final_name = str(ocr_name).strip()
            if is_highlighted and not final_name.startswith("[H]"):
                final_name = f"[H] {final_name}"  # [H] indicates highlighted player
                
            temp_output.append(final_name)
            logging.info(f"Name: {final_name}" + (" (HIGHLIGHTED)" if is_highlighted else ""))

            #OCR each cell to get numbers
            for c, cnt in enumerate(cells):
                x, y, w, h = cnt
                cropped=image[scale*y:scale*(y+h), scale*x:scale*(x+w)]
                cropped=functions.image_resize(cropped,20)
                # Define the kernel size for dilation
                kernel = np.ones((1, 1), np.uint8)
                # Apply dilation on the grayscale image
                cropped = cv2.dilate(cropped, kernel, iterations=1)
                #cropped = cv2.copyMakeBorder(cropped, 2, 2, 2, 2, cv2.BORDER_CONSTANT, None, 0)
                #cv2.imwrite("crop"+str(c)+".png",cropped)
                ocr_cropped=functions.ocr_image(cropped, '-c tessedit_char_whitelist=0123456789 --psm 7', 'eng')
                temp_output.append(str(ocr_cropped).strip())
            temp_output = [e for e in temp_output if e]
            output.append(temp_output)
        # remove the sorting step
        # output = sorted(output,  key=lambda x: x[0])
        return output

    def write_csv(output):
        """
        Writes the output list to a CSV file named "scoreboard.csv".

        Parameters:
        output (list): A list of lists containing the data to write to the CSV file.

        Returns:
        None
        """
        #Write the output file in csv format.
        with open('scoreboard.csv', 'a', newline='') as f:
            writer = csv.writer(f,delimiter=';')
            writer.writerows(output)


    def identify_agents(headshots_images_rows):
        """
        Identifies agents from the headshot images.

        Parameters:
        headshots (List[numpy.ndarray]): A list of headshot images.

        Returns:
        List[str]: A list of agent names.
        """
        # Load reference images and agent names
        reference_folder = './agent-images'
        reference_images, agent_names = load_images_from_folder(reference_folder)

        identified_agents = []
        n=0
        temp_image_path = './temp_headshot.png'
        for row in headshots_images_rows:
            n+=1
            # Save the headshot temporarily
            cv2.imwrite(temp_image_path, row[0])

            # Identify the agent
            agent_name = find_matching_agent(temp_image_path, reference_images, agent_names)
            agent_name = agent_name.capitalize() # Capitalization of Agent Name
            identified_agents.append(agent_name)
        # remove temp_headshot.png
        # os.remove(temp_image_path)

        return identified_agents
