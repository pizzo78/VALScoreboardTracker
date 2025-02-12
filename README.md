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

![ss_1](https://user-images.githubusercontent.com/57774007/220695198-47f6b995-b1e4-4fc8-83f6-46325065e388.png)

This tool has been tested on 16:9 English-language screenshots.

### Sample Output

The output should look something like this:

![image](https://user-images.githubusercontent.com/57774007/220700904-34984cfc-61cd-4004-b12f-9393d50e6664.png)

The output is sorted alphabetically by name, ensuring all players with the same team tag are grouped together.

---

## 📊 Example Scrim Tracker Spreadsheet

We've put together an example Google spreadsheet you can copy to keep track of your stats and fill with data from the tool:

➡️ [Example Scrim Tracker](https://docs.google.com/spreadsheets/d/1N7p1be3Yw2lM5oGfvo3qUTSEXE2f-QyXYMvSeXKH7sc/edit?gid=626882904#gid=626882904)

---

## 📚 References

Lovingly put together by **Felox** ([Twitter/X](https://x.com/felox210)) & **summonN** ([Twitter/X](https://x.com/summonhalfa)).

This version expands upon two forks of an existing tool, updating them and making them accessible to the entire VAL scene.

Special thanks to **Alex 'Aplox' Porter** ([Twitter/X](https://twitter.com/_Aplox)) for publishing the original concept and **isaacaudet** for the agent recognition library.

---

## 🔧 Prerequisites

*Pending: summonN, you have to write this section!* 😆

---

## ❓ FAQ

### 📥 How can I download the tool?
Coming soon!

### 🗺️ How can I add new maps?
To add a new map, add the map name to `VALORANT_MAPS` in the `config.ini` file.

### 🎭 How can I add new agents?
To add a new agent, add a **50x50 PNG portrait** named `agentname.png` to the `/agent-images` folder.

### 💖 How can I support the project?
Donations are a great way to support our work! This project will always remain **open-source and free-to-use**.

<p align="center">
  <form action="https://www.paypal.com/donate" method="post" target="_top">
    <input type="hidden" name="hosted_button_id" value="DXG78P2TZUEJL" />
    <input type="image" src="https://www.paypalobjects.com/en_US/i/btn/btn_donate_SM.gif" border="0" name="submit" title="PayPal - The safer, easier way to pay online!" alt="Donate with PayPal button" />
    <img alt="" border="0" src="https://www.paypal.com/en_IT/i/scr/pixel.gif" width="1" height="1" />
  </form>
</p>


---

### ⭐ If you find this project useful, consider giving it a **star** on GitHub!

---


