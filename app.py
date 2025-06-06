import os
import sys
import cv2
import pytesseract
from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for
from werkzeug.utils import secure_filename
from config_parser import create_config, read_config
from ocr_library import functions as srf
from auto_detection import auto_detect_teams_and_players
import tempfile
import shutil
from datetime import datetime
import csv
import io
import base64

app = Flask(__name__)
app.secret_key = 'valorant_scoreboard_tracker_secret_key'

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_base_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

def setup_tesseract():
    """Setup Tesseract with proper path handling"""
    try:
        if getattr(sys, 'frozen', False):
            tesseract_dir = os.path.join(sys._MEIPASS, 'Tesseract-OCR')
        else:
            tesseract_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Tesseract-OCR')

        if not os.path.exists(tesseract_dir):
            return False
        
        tesseract_exe = os.path.join(tesseract_dir, 'tesseract.exe')
        tessdata_dir = os.path.join(tesseract_dir, 'tessdata')
        
        if os.path.exists(tesseract_exe):
            pytesseract.pytesseract.tesseract_cmd = tesseract_exe
            os.environ['TESSDATA_PREFIX'] = tessdata_dir
            return True
        else:
            # Fallback to system tesseract
            pytesseract.pytesseract.tesseract_cmd = "tesseract"
            return True
            
    except Exception as e:
        print(f"Tesseract setup error: {e}")
        return False

def process_screenshot_raw(file_path, config_data):
    """Process a single screenshot and return raw data without filtering"""
    try:
        maps = config_data['maps']
        
        # Read the image
        image = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
        image_colored = cv2.imread(file_path)
        
        if image is None:
            return None, "Failed to read image file"
        
        # Detect map
        map_name = srf.find_map_name(image, maps)
        
        # Process scoreboard table
        image, image_colored = srf.find_tables(image, image_colored)
        
        # Extract cell information
        cell_images_rows, headshots_images_rows = srf.extract_cell_images_from_table(image, image_colored)
        
        # Identify agents
        agents = srf.identify_agents(headshots_images_rows)
        
        # Read table data with enhanced OCR
        output = srf.read_table_rows(cell_images_rows, headshots_images_rows)
        current_date = datetime.now().strftime("%d/%m/%Y")
        
        # Merge data without filtering
        merged_output = []
        for i, row in enumerate(output):
            if i < len(agents):
                agent = agents[i] if isinstance(agents[i], str) else "Unknown"
                merged_row = [current_date] + row[:1] + [map_name] + [agent] + row[1:]
                merged_output.append(merged_row)
        
        return merged_output, None
        
    except Exception as e:
        return None, f"Error processing screenshot: {str(e)}"

def process_screenshot(file_path, config_data):
    """Process a single screenshot and return the results (legacy function for compatibility)"""
    try:
        maps = config_data['maps']
        
        # Read the image
        image = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
        image_colored = cv2.imread(file_path)
        
        if image is None:
            return None, "Failed to read image file"
        
        # Detect map
        map_name = srf.find_map_name(image, maps)
        
        # Process scoreboard table
        image, image_colored = srf.find_tables(image, image_colored)
        
        # Extract cell information
        cell_images_rows, headshots_images_rows = srf.extract_cell_images_from_table(image, image_colored)
        
        # Identify agents
        agents = srf.identify_agents(headshots_images_rows)
        
        # Read table data with enhanced OCR
        output = srf.read_table_rows(cell_images_rows, headshots_images_rows)
        current_date = datetime.now().strftime("%d/%m/%Y")
        
        # Merge data
        merged_output = []
        for i, row in enumerate(output):
            if i < len(agents):
                agent = agents[i] if isinstance(agents[i], str) else "Unknown"
                merged_row = [current_date] + row[:1] + [map_name] + [agent] + row[1:]
                merged_output.append(merged_row)
        
        # Apply team/player filters
        if config_data['teamSorting']:
            filtered_output = [row for row in merged_output if config_data['team'] in row[1]]
        else:
            config_players = [player.replace(" ", "") for player in config_data['players']]
            filtered_output = [row for row in merged_output if any(player in row[1] for player in config_players)]
        
        return filtered_output, None
        
    except Exception as e:
        return None, f"Error processing screenshot: {str(e)}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/config')
def config_page():
    try:
        config_data = read_config()
        return render_template('config.html', config=config_data)
    except:
        # Create default config if it doesn't exist
        config_data = create_config()
        return render_template('config.html', config=config_data)

@app.route('/update_config', methods=['POST'])
def update_config():
    try:
        team = request.form.get('team', '')
        players_str = request.form.get('players', '')
        team_sorting = request.form.get('teamSorting') == 'on'
        maps_str = request.form.get('maps', '')
        
        # Parse players list
        players = [p.strip().strip('"') for p in players_str.split(',') if p.strip()]
        
        # Parse maps list
        maps = [m.strip().strip('"') for m in maps_str.split(',') if m.strip()]
        
        # Update config file
        config_content = f"""[General]
team = {team}
players = {players}
teamsorting = {str(team_sorting).lower()}
maps = {maps}
"""
        
        with open('config.ini', 'w') as f:
            f.write(config_content)
        
        flash('Configuration updated successfully!', 'success')
        return redirect(url_for('config_page'))
        
    except Exception as e:
        flash(f'Error updating configuration: {str(e)}', 'error')
        return redirect(url_for('config_page'))

@app.route('/upload', methods=['POST'])
def upload_files():
    if 'files' not in request.files:
        return jsonify({'error': 'No files provided'}), 400
    
    files = request.files.getlist('files')
    
    if not files or all(file.filename == '' for file in files):
        return jsonify({'error': 'No files selected'}), 400
    
    # Setup Tesseract
    if not setup_tesseract():
        return jsonify({'error': 'Failed to initialize Tesseract OCR'}), 500
    
    # Load configuration (fallback only)
    try:
        config_data = read_config()
    except:
        config_data = create_config()
    
    results = []
    all_raw_data = []  # Store raw data for auto-detection
    all_processed_data = []
    
    # Create uploads directory if it doesn't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # First pass: Process all screenshots to extract raw data
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            # Process the screenshot without filtering
            raw_data, error = process_screenshot_raw(file_path, config_data)
            
            if error:
                results.append({
                    'filename': filename,
                    'status': 'error',
                    'error': error
                })
            else:
                results.append({
                    'filename': filename,
                    'status': 'success',
                    'raw_count': len(raw_data)
                })
                all_raw_data.extend(raw_data)
            
            # Clean up uploaded file
            try:
                os.remove(file_path)
            except:
                pass
    
    # Auto-detect teams and players from all raw data
    auto_config = {}
    detection_summary = "No data processed"
    
    if all_raw_data:
        try:
            auto_config = auto_detect_teams_and_players([all_raw_data])
            detection_summary = auto_config.get('detection_summary', 'Auto-detection completed')
            
            # Apply auto-detected filtering
            if auto_config.get('teamSorting', False) and auto_config.get('team'):
                # Filter by team tag
                team_tag = auto_config['team']
                filtered_data = [row for row in all_raw_data if team_tag.lower() in row[1].lower()]
            else:
                # Filter by player names
                player_names = auto_config.get('players', [])
                if player_names:
                    filtered_data = []
                    for row in all_raw_data:
                        player_name = row[1].lower().replace(" ", "")
                        for target_player in player_names:
                            target_clean = target_player.lower().replace(" ", "")
                            if target_clean in player_name or player_name in target_clean:
                                filtered_data.append(row)
                                break
                else:
                    # No filtering, use all data
                    filtered_data = all_raw_data
            
            all_processed_data = filtered_data
            
            # Update results with filtered counts
            for result in results:
                if result['status'] == 'success':
                    # Count how many records from this file made it through filtering
                    result['filtered_count'] = len([row for row in filtered_data if row])
                    
        except Exception as e:
            # Fallback to no filtering if auto-detection fails
            all_processed_data = all_raw_data
            detection_summary = f"Auto-detection failed: {str(e)}, using all data"
    
    # Generate CSV content
    csv_content = ""
    if all_processed_data:
        output = io.StringIO()
        writer = csv.writer(output, delimiter=';')
        writer.writerows(all_processed_data)
        csv_content = output.getvalue()
        output.close()
    
    return jsonify({
        'results': results,
        'csv_content': csv_content,
        'total_records': len(all_processed_data),
        'auto_detection': {
            'enabled': True,
            'summary': detection_summary,
            'detected_teams': auto_config.get('detected_teams', {}),
            'config_used': {
                'team_sorting': auto_config.get('teamSorting', False),
                'team_tag': auto_config.get('team', ''),
                'player_count': len(auto_config.get('players', []))
            }
        }
    })

@app.route('/download_csv')
def download_csv():
    # This would be called with CSV data from the frontend
    csv_data = request.args.get('data', '')
    
    if not csv_data:
        return "No data to download", 400
    
    # Create a temporary file
    output = io.StringIO()
    output.write(csv_data)
    output.seek(0)
    
    return send_file(
        io.BytesIO(output.getvalue().encode()),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'valorant_scoreboard_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    )

if __name__ == '__main__':
    # Ensure required directories exist
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    # Initialize Tesseract
    setup_tesseract()
    
    app.run(debug=True, host='0.0.0.0', port=5000)