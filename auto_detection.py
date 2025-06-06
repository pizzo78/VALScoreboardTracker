"""
Automatic Team and Player Detection Module
Analyzes VALORANT scoreboard screenshots to automatically detect teams and players
"""

import re
from collections import Counter, defaultdict
from typing import List, Dict, Tuple, Set
import difflib
from ocr_improvements import enhanced_ocr

class TeamDetector:
    """Automatically detects teams and players from VALORANT scoreboard data"""
    
    def __init__(self):
        # Common team tag patterns
        self.team_tag_patterns = [
            r'^([A-Z]{2,5})\s+',  # Team tag at start (e.g., "TSM player")
            r'^([A-Z]{2,5})_',    # Team tag with underscore (e.g., "TSM_player")
            r'^([A-Z]{2,5})\.',   # Team tag with dot (e.g., "TSM.player")
            r'^([A-Z]{2,5})-',    # Team tag with dash (e.g., "TSM-player")
            r'^([A-Z]{2,5})\|',   # Team tag with pipe (e.g., "TSM|player")
        ]
        
        # Common separators between team tags and player names
        self.separators = [' ', '_', '.', '-', '|', ':']
        
        # Minimum players needed to consider a team
        self.min_team_size = 2
        
        # Maximum team size in VALORANT
        self.max_team_size = 5

    def clean_player_name(self, name: str) -> str:
        """Clean and normalize player names with leet speak handling"""
        if not name or name.strip() == "":
            return ""
        
        # Remove highlighting indicator if present
        if name.startswith("[H] "):
            name = name[4:]
        
        # Handle leet speak normalization in parentheses
        if "(" in name and ")" in name:
            # Extract both original and normalized versions
            parts = name.split("(")
            if len(parts) == 2:
                original = parts[0].strip()
                normalized = parts[1].replace(")", "").strip()
                # Use the longer/more complete version
                name = original if len(original) >= len(normalized) else normalized
        
        # Remove common OCR artifacts but keep leet speak characters
        name = re.sub(r'[^\w\s\-_\.\|@!$+]', '', name)
        name = name.strip()
        
        # Remove extra whitespace
        name = re.sub(r'\s+', ' ', name)
        
        # Also store normalized version for better matching
        normalized = enhanced_ocr.normalize_leet_speak(name)
        
        # Return original name but store both for matching
        return name

    def extract_potential_team_tags(self, player_names: List[str]) -> Dict[str, List[str]]:
        """Extract potential team tags from player names"""
        team_candidates = defaultdict(list)
        
        for name in player_names:
            clean_name = self.clean_player_name(name)
            if not clean_name:
                continue
                
            # Try each pattern to extract team tags
            for pattern in self.team_tag_patterns:
                match = re.match(pattern, clean_name, re.IGNORECASE)
                if match:
                    potential_tag = match.group(1).upper()
                    if len(potential_tag) >= 2:  # Minimum tag length
                        team_candidates[potential_tag].append(clean_name)
                        break
            
            # Also check for common prefixes (first 2-4 characters)
            if len(clean_name) >= 3:
                for length in range(2, min(5, len(clean_name))):
                    prefix = clean_name[:length].upper()
                    if prefix.isalpha():
                        # Check if this could be a team tag
                        remaining = clean_name[length:]
                        if remaining and remaining[0] in self.separators:
                            team_candidates[prefix].append(clean_name)
        
        return team_candidates

    def normalize_for_matching(self, name: str) -> List[str]:
        """Generate multiple versions of a name for better matching"""
        versions = [name]
        
        # Add leet speak normalized version
        normalized = enhanced_ocr.normalize_leet_speak(name)
        if normalized != name.lower():
            versions.append(normalized)
        
        # Add version without special characters
        clean_version = re.sub(r'[^a-zA-Z0-9]', '', name)
        if clean_version and clean_version not in versions:
            versions.append(clean_version)
        
        return versions

    def detect_teams_from_names(self, player_names: List[str]) -> Dict[str, List[str]]:
        """Detect teams based on player name patterns with leet speak support"""
        if not player_names:
            return {}
        
        # Clean all names and create mapping for original names
        name_mapping = {}  # cleaned -> original
        clean_names = []
        
        for original_name in player_names:
            if original_name:
                cleaned = self.clean_player_name(original_name)
                if cleaned:
                    clean_names.append(cleaned)
                    name_mapping[cleaned] = original_name
        
        if len(clean_names) < 2:
            return {"Team1": list(name_mapping.values())}
        
        # Extract potential team tags with leet speak awareness
        team_candidates = self.extract_potential_team_tags_enhanced(clean_names)
        
        # Filter candidates by minimum team size
        valid_teams = {}
        for tag, players in team_candidates.items():
            if len(players) >= self.min_team_size and len(players) <= self.max_team_size:
                # Map back to original names
                original_players = [name_mapping.get(p, p) for p in players]
                valid_teams[tag] = original_players
        
        # If no clear teams found, try to group by similarity
        if not valid_teams:
            similarity_groups = self.group_by_similarity(clean_names)
            for team_name, players in similarity_groups.items():
                original_players = [name_mapping.get(p, p) for p in players]
                valid_teams[team_name] = original_players
        
        # Handle remaining ungrouped players
        all_grouped_players = set()
        for players in valid_teams.values():
            all_grouped_players.update(players)
        
        ungrouped_original = [name for name in player_names if name not in all_grouped_players]
        if ungrouped_original:
            if len(ungrouped_original) >= self.min_team_size:
                valid_teams["Mixed"] = ungrouped_original
            else:
                # Add to smallest existing team or create new team
                if valid_teams:
                    smallest_team = min(valid_teams.keys(), key=lambda k: len(valid_teams[k]))
                    valid_teams[smallest_team].extend(ungrouped_original)
                else:
                    valid_teams["Team1"] = ungrouped_original
        
        return valid_teams

    def extract_potential_team_tags_enhanced(self, player_names: List[str]) -> Dict[str, List[str]]:
        """Enhanced team tag extraction with leet speak support"""
        team_candidates = defaultdict(list)
        
        for name in player_names:
            clean_name = name
            if not clean_name:
                continue
            
            # Generate multiple versions for matching
            name_versions = self.normalize_for_matching(clean_name)
            
            # Try each version with each pattern
            tag_found = False
            for version in name_versions:
                if tag_found:
                    break
                    
                for pattern in self.team_tag_patterns:
                    match = re.match(pattern, version, re.IGNORECASE)
                    if match:
                        potential_tag = match.group(1).upper()
                        if len(potential_tag) >= 2:  # Minimum tag length
                            team_candidates[potential_tag].append(clean_name)
                            tag_found = True
                            break
            
            # Also check for common prefixes if no tag found
            if not tag_found and len(clean_name) >= 3:
                for length in range(2, min(5, len(clean_name))):
                    prefix = clean_name[:length].upper()
                    if prefix.isalnum():  # Allow alphanumeric prefixes
                        # Check if this could be a team tag
                        remaining = clean_name[length:]
                        if remaining and remaining[0] in self.separators:
                            team_candidates[prefix].append(clean_name)
                            break
        
        return team_candidates

    def group_by_similarity(self, player_names: List[str]) -> Dict[str, List[str]]:
        """Group players by name similarity when no clear team tags exist"""
        if len(player_names) <= 5:
            return {"Team1": player_names}
        
        # Try to find common patterns or prefixes
        groups = defaultdict(list)
        
        # Group by first few characters
        for name in player_names:
            if len(name) >= 2:
                prefix = name[:2].upper()
                groups[prefix].append(name)
        
        # Filter groups and create teams
        valid_groups = {}
        team_counter = 1
        
        for prefix, players in groups.items():
            if len(players) >= self.min_team_size:
                valid_groups[f"Team{team_counter}"] = players
                team_counter += 1
        
        # Handle remaining players
        all_grouped = set()
        for players in valid_groups.values():
            all_grouped.update(players)
        
        remaining = [name for name in player_names if name not in all_grouped]
        if remaining:
            if len(remaining) >= self.min_team_size:
                valid_groups[f"Team{team_counter}"] = remaining
            elif valid_groups:
                # Add to first team
                first_team = list(valid_groups.keys())[0]
                valid_groups[first_team].extend(remaining)
            else:
                valid_groups["Team1"] = remaining
        
        return valid_groups

    def analyze_match_data(self, all_match_data: List[List]) -> Dict:
        """Analyze multiple matches to build comprehensive team/player database"""
        all_players = []
        
        # Extract all player names from all matches
        for match_data in all_match_data:
            for row in match_data:
                if len(row) > 1:  # Ensure we have player name
                    player_name = row[1] if len(row) > 1 else ""
                    if player_name and player_name != "err":
                        all_players.append(player_name)
        
        # Remove duplicates while preserving order
        unique_players = list(dict.fromkeys(all_players))
        
        # Detect teams
        detected_teams = self.detect_teams_from_names(unique_players)
        
        # Create analysis summary
        analysis = {
            "total_unique_players": len(unique_players),
            "detected_teams": detected_teams,
            "team_count": len(detected_teams),
            "all_players": unique_players,
            "team_summary": {}
        }
        
        # Create team summary
        for team_name, players in detected_teams.items():
            analysis["team_summary"][team_name] = {
                "player_count": len(players),
                "players": players,
                "most_common_tag": self.extract_most_common_tag(players)
            }
        
        return analysis

    def extract_most_common_tag(self, players: List[str]) -> str:
        """Extract the most common team tag from a list of players"""
        tags = []
        
        for player in players:
            for pattern in self.team_tag_patterns:
                match = re.match(pattern, player, re.IGNORECASE)
                if match:
                    tags.append(match.group(1).upper())
                    break
        
        if tags:
            return Counter(tags).most_common(1)[0][0]
        
        return ""

    def get_auto_config(self, analysis: Dict) -> Dict:
        """Generate automatic configuration based on analysis"""
        if not analysis["detected_teams"]:
            return {
                "teamSorting": False,
                "team": "",
                "players": analysis["all_players"],
                "auto_detected": True,
                "detection_summary": "No clear teams detected, using all players"
            }
        
        # If only one team detected, use player-based filtering
        if len(analysis["detected_teams"]) == 1:
            team_name = list(analysis["detected_teams"].keys())[0]
            players = analysis["detected_teams"][team_name]
            team_tag = analysis["team_summary"][team_name]["most_common_tag"]
            
            if team_tag and len(team_tag) >= 2:
                return {
                    "teamSorting": True,
                    "team": team_tag,
                    "players": players,
                    "auto_detected": True,
                    "detection_summary": f"Detected team '{team_tag}' with {len(players)} players"
                }
            else:
                return {
                    "teamSorting": False,
                    "team": "",
                    "players": players,
                    "auto_detected": True,
                    "detection_summary": f"Detected {len(players)} players, no clear team tag"
                }
        
        # Multiple teams detected - use the largest team
        largest_team = max(analysis["detected_teams"].keys(), 
                          key=lambda k: len(analysis["detected_teams"][k]))
        players = analysis["detected_teams"][largest_team]
        team_tag = analysis["team_summary"][largest_team]["most_common_tag"]
        
        if team_tag and len(team_tag) >= 2:
            return {
                "teamSorting": True,
                "team": team_tag,
                "players": players,
                "auto_detected": True,
                "detection_summary": f"Multiple teams detected, using largest team '{team_tag}' with {len(players)} players"
            }
        else:
            return {
                "teamSorting": False,
                "team": "",
                "players": players,
                "auto_detected": True,
                "detection_summary": f"Multiple teams detected, using largest group with {len(players)} players"
            }

def auto_detect_teams_and_players(match_data_list: List[List]) -> Dict:
    """
    Main function to automatically detect teams and players from match data
    
    Args:
        match_data_list: List of match data (each match is a list of player rows)
    
    Returns:
        Dictionary with auto-detected configuration
    """
    detector = TeamDetector()
    analysis = detector.analyze_match_data(match_data_list)
    config = detector.get_auto_config(analysis)
    
    # Add detailed analysis for debugging/info
    config["detailed_analysis"] = analysis
    
    return config