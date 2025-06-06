# Auto-Detection Feature Guide

## 🤖 Automatic Team and Player Detection

The VAL Scoreboard Tracker now features intelligent auto-detection that automatically identifies teams and players from VALORANT screenshots, eliminating the need for manual configuration in most cases.

## ✨ How It Works

### 1. **Pattern Recognition**
The system analyzes player names to identify common team tag patterns:
- **Prefix Tags**: `TSM player`, `SEN player`, `NOVO player`
- **Separator Tags**: `TSM_player`, `TSM.player`, `TSM-player`, `TSM|player`
- **Common Prefixes**: Detects 2-5 character team prefixes automatically

### 2. **Team Grouping**
- Groups players with similar name patterns
- Requires minimum 2 players per team
- Maximum 5 players per team (VALORANT standard)
- Handles mixed teams and ungrouped players intelligently

### 3. **Smart Filtering**
- **Team Tag Mode**: When clear team tags are detected, filters by tag
- **Player Name Mode**: When no clear tags exist, filters by exact player matches
- **Fallback Mode**: If detection fails, includes all players

## 🎯 Detection Examples

### Example 1: Clear Team Tags
**Input Players:**
- `TSM wardell`
- `TSM subroza` 
- `TSM hazed`
- `C9 leaf`
- `C9 xeppaa`

**Detection Result:**
- **Team TSM**: 3 players (Team tag filtering enabled)
- **Team C9**: 2 players
- **Filter Mode**: Team tag filtering with largest team (TSM)

### Example 2: Mixed Patterns
**Input Players:**
- `player1`
- `player2`
- `NOVO_insider`
- `NOVO_KATU`
- `randomPlayer`

**Detection Result:**
- **Team NOVO**: 2 players
- **Team Mixed**: 3 other players
- **Filter Mode**: Player name filtering with NOVO team

### Example 3: No Clear Teams
**Input Players:**
- `alice`
- `bob`
- `charlie`
- `david`
- `eve`

**Detection Result:**
- **Team1**: All 5 players
- **Filter Mode**: Include all players (no filtering)

## 🔧 Technical Implementation

### Core Components

1. **`auto_detection.py`** - Main detection engine
   - `TeamDetector` class with pattern recognition
   - `extract_potential_team_tags()` - Finds team tags using regex
   - `detect_teams_from_names()` - Groups players into teams
   - `analyze_match_data()` - Processes multiple matches

2. **Updated `app.py`** - Web application integration
   - `process_screenshot_raw()` - Extracts data without filtering
   - Auto-detection in upload workflow
   - Smart filtering based on detection results

3. **Enhanced Frontend** - User interface improvements
   - Auto-detection results display
   - Team breakdown visualization
   - Detection summary information

### Detection Patterns

```python
team_tag_patterns = [
    r'^([A-Z]{2,5})\s+',  # "TSM player"
    r'^([A-Z]{2,5})_',    # "TSM_player"
    r'^([A-Z]{2,5})\.',   # "TSM.player"
    r'^([A-Z]{2,5})-',    # "TSM-player"
    r'^([A-Z]{2,5})\|',   # "TSM|player"
]
```

## 📊 Web Interface Features

### Auto-Detection Card
- **Detection Summary**: Shows what was detected and how
- **Team Breakdown**: Visual display of detected teams
- **Filter Configuration**: Shows which filtering method was used
- **Player Count**: Total players found and filtered

### Processing Results
- **Raw Count**: Total players found in screenshots
- **Filtered Count**: Players remaining after auto-filtering
- **Status Indicators**: Success/error status for each file

## ⚙️ Configuration Override

While auto-detection works automatically, manual configuration is still available:

### When to Use Manual Config
- **Specific Team Focus**: Want to track only one specific team
- **Custom Player Lists**: Have exact player names to track
- **Detection Issues**: Auto-detection doesn't work correctly for your data

### Manual Override Process
1. Go to Configuration page
2. Set team tag or player names manually
3. Save configuration
4. Manual settings will override auto-detection

## 🎮 Usage Workflow

### Simple Workflow (Auto-Detection)
1. **Upload Screenshots** - Drag & drop VALORANT scoreboard images
2. **Automatic Processing** - System detects teams and players
3. **Review Results** - See detection summary and team breakdown
4. **Download Data** - Get filtered CSV with relevant players only

### Advanced Workflow (Manual Override)
1. **Configure Settings** - Set specific team tags or player names
2. **Upload Screenshots** - Process with manual configuration
3. **Get Targeted Results** - Data filtered by your specifications

## 🔍 Troubleshooting

### Common Detection Issues

**Issue**: No teams detected
- **Cause**: Player names don't follow common patterns
- **Solution**: Use manual configuration with exact player names

**Issue**: Wrong team selected
- **Cause**: Multiple teams detected, largest selected automatically
- **Solution**: Use manual configuration to specify desired team

**Issue**: Players missing from results
- **Cause**: OCR errors in player name recognition
- **Solution**: Check screenshot quality, ensure 16:9 resolution

### Detection Quality Tips

1. **Screenshot Quality**: Higher resolution = better OCR accuracy
2. **Name Clarity**: Ensure player names are clearly visible
3. **Consistent Naming**: Teams with consistent tag patterns work best
4. **Multiple Screenshots**: More data improves detection accuracy

## 📈 Performance Benefits

### Before Auto-Detection
- Manual configuration required for each team
- Need to know exact player names in advance
- Separate setup for different teams/tournaments
- Risk of missing players due to typos

### After Auto-Detection
- Zero configuration for most use cases
- Automatically adapts to new teams/players
- Works with any tournament or match data
- Intelligent fallback for edge cases

## 🚀 Future Enhancements

Potential improvements for auto-detection:

1. **Learning System**: Remember detected teams across sessions
2. **Confidence Scoring**: Show detection confidence levels
3. **Manual Corrections**: Allow users to correct detection results
4. **Tournament Mode**: Detect tournament brackets and team matchups
5. **Player Database**: Build database of known players and teams

## 📝 API Response Format

The auto-detection results are included in the upload response:

```json
{
  "results": [...],
  "csv_content": "...",
  "total_records": 10,
  "auto_detection": {
    "enabled": true,
    "summary": "Detected team 'TSM' with 3 players",
    "detected_teams": {
      "TSM": ["TSM wardell", "TSM subroza", "TSM hazed"],
      "C9": ["C9 leaf", "C9 xeppaa"]
    },
    "config_used": {
      "team_sorting": true,
      "team_tag": "TSM",
      "player_count": 3
    }
  }
}
```

---

**Status**: ✅ Auto-detection feature fully implemented and tested
**Compatibility**: Works with existing manual configuration as fallback
**Performance**: Processes detection in real-time during upload