import sys
import cv2
import numpy as np
import pytesseract
import subprocess
import math
import csv
from tqdm import tqdm
from PIL import Image, ImageFilter
from ocr_library import functions as srf
import os
import pyperclip  # For clipboard functionality

# Setting up tesseract - only needs this if you have directly installed tesseract (I think).
pytesseract.pytesseract.tesseract_cmd = "tesseract"

# Get the folder path where the script is running
folder_path = os.path.dirname(os.path.abspath(__file__))

# Ensure the old scoreboard is deleted at the start of the program
if os.path.exists('scoreboard.csv'):
    os.remove('scoreboard.csv')

# Function to read settings from a file
def load_settings(settings_file):
    settings = {}
    if os.path.exists(settings_file):
        with open(settings_file, 'r') as file:
            for line in file:
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    settings[key.strip()] = value.strip()
    return settings

# Load settings from the local file
settings_file = os.path.join(folder_path, 'settings')
settings = load_settings(settings_file)

# Get the team filter from the settings file, with "NOVO" as the default
team_filter = settings.get("TEAM_FILTER", "NOVO")

# Iterate over all files in the folder
for filename in os.listdir(folder_path):
    if filename.lower().endswith(".png"):
        image = cv2.imread(filename, cv2.IMREAD_GRAYSCALE)
        image = srf.find_tables(image)
        # cv2.imwrite("table.png", image)

        # Extracts each row of elements from the table
        cell_images_rows = srf.extract_cell_images_from_table(image)

        # Reads the extracted rows and converts them to a list of lists
        output = srf.read_table_rows(cell_images_rows)
        
        # Filter rows where the team matches the specified filter (assuming team column is index 0)
        filtered_output = [row for row in output if team_filter in row[0]]  # Adjust index as needed

        # Write to CSV
        srf.write_csv(filtered_output)

        # Copy to clipboard as text
        filtered_output_text = "\n".join([", ".join(row) for row in filtered_output])
        pyperclip.copy(filtered_output_text)

print("Done. Output written to scoreboard.csv and copied to clipboard.")
input()
