'''
Code formally written by Alexander James Porter (Contact: AlexanderPorter1234@gmail.com) 20/02/2023
Code has been optimised for reading screenshots of final scoreboard in the game VALORANT
Lots of code is utilised from https://github.com/eihli/image-table-ocr#org67b1fc2
'''
import os
import cv2
import pytesseract
from config_parser import create_config, read_config
from scoreboard_reader import functions as srf

#Setting up tesseract - only needs this if you have directly installed tesseract (I think).
pytesseract.pytesseract.tesseract_cmd = "tesseract"

# Get the folder path where the script is running
folder_path = os.path.dirname(os.path.abspath(__file__))

if os.path.exists('config.ini'):
    config_data = read_config()
else:
    config_data = create_config()

# Ensure the old scoreboard is deleted at the start of the program
if os.path.exists('scoreboard.csv'):
    os.remove('scoreboard.csv')

# Iterate over all files in the folder
for filename in os.listdir(folder_path):
    if filename in ["temp_headshot.png", "agent.png"]:
        continue
    if filename.lower().endswith(".png"):
        image = cv2.imread(filename, cv2.IMREAD_GRAYSCALE)
        image_colored = cv2.imread(filename)
        image, image_colored = srf.find_tables(image, image_colored)

        cell_images_rows, headshots_images_rows = srf.extract_cell_images_from_table(image, image_colored)

        agents = srf.identify_agents(headshots_images_rows)
        output = srf.read_table_rows(cell_images_rows)
        merged_output = [
            row[:1] + [agents[i]] + row[1:] if isinstance(agents[i], str) else row[:1] + agents[i] + row[1:]
            for i, row in enumerate(output)
        ]
        print(type(config_data['players']))
        # Filter rows where the team is "NOVO" (assuming team column is index 2)
        if config_data['teamSorting']:
            filtered_output = [row for row in merged_output if config_data['team'] in row[0]]  # Adjust index as needed
        else:
            filtered_output = [row for row in merged_output if any(player in row[0] for player in config_data['players'])]

        srf.write_csv(filtered_output)

print("Done. Output written to scoreboard.csv.")
