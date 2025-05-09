# <img src="https://i.imgur.com/e9TqKPz.png" width=25  alt="VALScoreboardTracker Banner"/> VALScoreboardTracker 

<p align="center">
  <img src="https://i.imgur.com/e9TqKPz.png" width=200 alt="VALScoreboardTracker Banner"/>
</p>

<p align="center">
  Extract Valorant end-game scoreboard data from screenshots and convert it into a CSV, optimized for team environments. 
</p>

## 🚀 How to Use

1. Fill the `config.ini` file with your `TEAMTAG` or `PLAYERNAMES` (so the script can filter enemies out!).
2. Place your desired screenshots in the `/screenshots` folder.
3. Run `VALScoreboardTracker.exe`.
4. All the stats from the screenshot are now copied to your clipboard and saved in `scoreboard.csv`!

### Example Screenshot

<p align="center">
  <img src="https://user-images.githubusercontent.com/57774007/220695198-47f6b995-b1e4-4fc8-83f6-46325065e388.png" width=750 alt="VALScoreboardTracker Example Screenshot"/>
</p>

This tool has been tested on 16:9 English-language screenshots.

### Sample Output

The output should look something like this:

<p align="center">
  <img src="https://i.imgur.com/0FKyutH.png" width=1000 alt="VALScoreboardTracker Example Table"/>
</p>

The output is sorted alphabetically by name, ensuring all players with the same team tag are grouped together.

---

## 📊 Example Scrim Tracker Spreadsheet

We've put together an example Google spreadsheet you can copy to keep track of your stats and fill with data from the tool:

### 📝 How to Use

1. Make a copy of the example spreadsheet
2. Run the script with your screenshots locally to get data
3. Use the empty sheet to copy paste data (use ; separator for automatic column separation)
4. Copy the clean data to the main "Stats" sheet
5. Replace the names in the yellow tables with your player names

➡️ [Example Scrim Tracker](https://docs.google.com/spreadsheets/d/1N7p1be3Yw2lM5oGfvo3qUTSEXE2f-QyXYMvSeXKH7sc/edit?gid=626882904#gid=626882904)

<p align="center">
  <img src="https://i.imgur.com/LqoWu6C.png" width=1000 alt="VALScoreboardTracker Example Tracker"/>
</p>
<p align="center">
  <img src="https://i.imgur.com/9H8pRmg.png" width=1000 alt="VALScoreboardTracker Example Tracker"/>
</p>

---

## 📚 References

Lovingly put together by **Felox** ([Twitter/X](https://x.com/felox210)) & **summonN** ([Twitter/X](https://x.com/summonhalfa)).

<sub> Special thanks to [**Aplox**](https://twitter.com/_Aplox) for publishing the original version and **isaacaudet** for the agent recognition library. </sub>

## ❓ FAQ

### 🔄 Is the tool up to date? / Is Agent X / Maps Y supported? 
The tool is currently updated to VALORANT `Patch 10.0`. \
The last added map was `Abyss`.\
The last added agent was `Tejo`.

### 📥 How can I download the tool?
Download the latest version from our [GitHub Releases](https://github.com/Felox210/VALScoreboardTracker/releases/tag/stable) page.

### 🗺️ How can I add new maps?
To add a new map, add the map name to `VALORANT_MAPS` in the `config.ini` file.

### 🎭 How can I add new agents?
To add a new agent, add a **50x50 PNG portrait** named `agentname.png` to the `/agent-images` folder.

### 💖 How can I support the project?
Donations are a great way to support our work! This project will always remain **open-source and free-to-use**.

<p align="center">
  <a href="https://www.paypal.com/donate?hosted_button_id=DXG78P2TZUEJL">
    <img src="https://www.paypalobjects.com/en_US/IT/i/btn/btn_donateCC_LG.gif" alt="Donate with PayPal button" />
  </a>
</p>



