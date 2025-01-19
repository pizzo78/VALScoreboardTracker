'''
Code formally written by Alexander James Porter (Contact: AlexanderPorter1234@gmail.com) 20/02/2023
Code has been optimised for reading screenshots of final scoreboard in the game VALORANT
Lots of code is utilised from https://github.com/eihli/image-table-ocr#org67b1fc2
'''
import sys
import cv2
import numpy as np
import pytesseract
import subprocess
import math
import csv
from tqdm import tqdm
from PIL import Image,ImageFilter
from scoreboard_reader import functions as srf
import os

#Setting up tesseract - only needs this if you have directly installed tesseract (I think).
pytesseract.pytesseract.tesseract_cmd = "tesseract"

# Get the folder path where the script is running
folder_path = os.path.dirname(os.path.abspath(__file__))

# Ensure the old scoreboard is deleted at the start of the program
if os.path.exists('scoreboard.csv'):
    os.remove('scoreboard.csv')

# Iterate over all files in the folder
for filename in os.listdir(folder_path):
    if filename.lower().endswith(".png"):
        image = cv2.imread(filename, cv2.IMREAD_GRAYSCALE)
        image = srf.find_tables(image)
        #cv2.imwrite("table.png",image)

        #Extracts each row of elements from the table
        cell_images_rows = srf.extract_cell_images_from_table(image)

        #Reads the extracted rows and converts them to a list of lists.
        output = srf.read_table_rows(cell_images_rows)
        # Filter rows where the team is "NOVO" (assuming team column is index 2)
        filtered_output = [row for row in output if "NOVO" in row[0]]  # Adjust index as needed

        srf.write_csv(filtered_output)

print("Done. Output written to scoreboard.csv.")
