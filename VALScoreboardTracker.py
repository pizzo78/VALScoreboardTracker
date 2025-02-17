'''
Code formally written by Alexander James Porter (Contact: AlexanderPorter1234@gmail.com) 20/02/2023
Code has been optimised for reading screenshots of final scoreboard in the game VALORANT
Lots of code is utilised from https://github.com/eihli/image-table-ocr#org67b1fc2
'''
import os
import cv2
import pytesseract
from config_parser import create_config, read_config
from ocr_library import functions as srf
import pyperclip
from datetime import datetime

# Setting up tesseract
pytesseract.pytesseract.tesseract_cmd = "tesseract"

# Get the folder path where the script is running
folder_path = os.path.dirname(os.path.abspath(__file__))

# Name of the folder for screenshots
screenshot_folder = os.path.join(folder_path, "screenshots")

if os.path.exists('config.ini'):
    config_data = read_config()
else:
    config_data = create_config()

# Ensure the old scoreboard is deleted at the start of the program
if os.path.exists('scoreboard.csv'):
    os.remove('scoreboard.csv')

# Ensure the screenshot folder exists
if os.path.exists(screenshot_folder) and os.path.isdir(screenshot_folder):
    for filename in os.listdir(screenshot_folder):
        file_path = os.path.join(screenshot_folder, filename)

        if filename.lower().endswith(".png"):
            image = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
            image_colored = cv2.imread(file_path)
            map_name = srf.find_map_name(image)
            image, image_colored = srf.find_tables(image, image_colored)

            cell_images_rows, headshots_images_rows = srf.extract_cell_images_from_table(image, image_colored)

            agents = srf.identify_agents(headshots_images_rows)
            output = srf.read_table_rows(cell_images_rows)
            current_date = datetime.now().strftime("%d/%m/%Y")
            merged_output = [
                [current_date] + row[:1] + [map_name] + row[:1] + [agents[i]] + row[1:] if isinstance(agents[i], str) else [map_name] + row[:1] + agents[i] + row[1:]
                for i, row in enumerate(output)
            ]

            # Filter rows based on team sorting
            if config_data['teamSorting']:
                filtered_output = [row for row in merged_output if config_data['team'] in row[1]]
            else:
                filtered_output = [row for row in merged_output if any(player in row[1] for player in config_data['players'])]

            srf.write_csv(filtered_output)
print("Done. Output written to scoreboard.csv.")

# Read the contents of scoreboard.csv
with open("scoreboard.csv", "r", encoding="utf-8") as file:
    scoreboard_data = file.read()
# Copy to clipboard
pyperclip.copy(scoreboard_data)
print("Contents of scoreboard.csv copied to clipboard.")
