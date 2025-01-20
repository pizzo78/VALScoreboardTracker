# VALORANT_scoreboard_reader
Python tool using tesseract to OCR screenshots of a valorant end game scoreboard and turn it into a csv file.

Originally written by Alex 'Aplox' Porter (twitter.com/_Aplox) and expanded upon.

This repository containts two files. 

1. File with the class and all of the functions (ocr_library.py)
2. File for running the OCR tool to gain a csv file (scorereader.py)


## How to use
The first thing you need is a screenshot of a scoreboard like this:
![ss_1](https://user-images.githubusercontent.com/57774007/220695198-47f6b995-b1e4-4fc8-83f6-46325065e388.png)
The tool has been tested on English and Turkish language screenshots.
The tool only works on screenshots in 16:9 aspect ratio currently. Unfortunately more testing is required to work with stretched resolution screenshots.

The script will scan all the image files in the folder.

The tool then splits the image by row and then each row by cell.
Each cell is then passed through tesseract and converted to a string which can be output.

The output is as a csv file and also copied to the clipboard.

The output should look something like this: <br>
![image](https://user-images.githubusercontent.com/57774007/220700904-34984cfc-61cd-4004-b12f-9393d50e6664.png)<br>
The output will be filtered to only include entries that include your team's tag (you can set it via the settings.txt file)

## Prerequsites
Firstly you need tesseract-OCR. Instructions to install here: <br>
https://medium.com/@ahmedbr/how-to-implement-pytesseract-properly-d6e2c2bc6dda <br>

All dependancies may be installed using the following command:
<code> pip3 install -r "requirements.txt" </code>

## FAQ
Coming soon?
