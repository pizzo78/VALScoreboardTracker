# VAL Scoreboard Tracker - Web Application Setup Guide

## 🌐 Web Application Overview

The VAL Scoreboard Tracker has been successfully converted from a desktop application to a modern web application with the following features:

### ✨ Key Features
- **Drag & Drop Interface** - Upload screenshots easily
- **Real-time Processing** - See results immediately
- **Web-based Configuration** - No need to edit config files
- **Batch Processing** - Handle multiple screenshots at once
- **Responsive Design** - Works on desktop and mobile
- **CSV Export** - Download results instantly

## 🚀 Quick Start

### Prerequisites
- Python 3.7 or higher
- Web browser (Chrome, Firefox, Safari, Edge)

### Installation & Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the Web Server**
   ```bash
   python app.py
   ```
   Or use the launcher:
   ```bash
   python run_webapp.py
   ```

3. **Access the Application**
   - Open your browser to: `http://localhost:5000`
   - The application will be available on your local network at: `http://[your-ip]:5000`

## 📁 Project Structure

```
VALScoreboardTracker/
├── app.py                 # Main Flask application
├── run_webapp.py          # Application launcher
├── requirements.txt       # Python dependencies
├── config.ini            # Configuration file
├── Dockerfile            # Docker container setup
├── docker-compose.yml    # Docker Compose configuration
├── templates/            # HTML templates
│   ├── base.html         # Base template
│   ├── index.html        # Upload page
│   └── config.html       # Configuration page
├── static/               # Static assets
│   └── style.css         # Custom CSS styles
├── agent-images/         # Agent recognition images
├── Tesseract-OCR/        # OCR engine (bundled)
└── uploads/              # Temporary upload directory
```

## 🔧 Configuration

### Web Interface Configuration
1. Navigate to the **Configuration** page in the web interface
2. Set your team tag or player names
3. Configure team filtering options
4. Add/remove supported maps
5. Save your settings

### Manual Configuration
Edit `config.ini` directly:
```ini
[General]
team = YOUR_TEAM_TAG
players = ["player1", "player2", "player3"]
teamsorting = false
maps = ["Haven", "Bind", "Ascent", "Icebox", "Split", "Breeze", "Lotus", "Pearl", "Sunset", "Abyss"]
```

## 📱 How to Use

1. **Configure Settings**
   - Go to Configuration page
   - Set your team tag or player names
   - Save settings

2. **Upload Screenshots**
   - Navigate to the Upload page
   - Drag and drop PNG/JPG files or click to browse
   - Screenshots must be 16:9 resolution, English interface

3. **Process Data**
   - Click "Process Screenshots"
   - Wait for analysis to complete
   - View results in real-time

4. **Export Results**
   - Download CSV file
   - Copy data to clipboard
   - Import into your spreadsheet tracker

## 🐳 Docker Deployment

### Using Docker Compose (Recommended)
```bash
docker-compose up -d
```

### Using Docker directly
```bash
# Build the image
docker build -t val-scoreboard-tracker .

# Run the container
docker run -p 5000:5000 -v ./uploads:/app/uploads val-scoreboard-tracker
```

## 🔍 Troubleshooting

### Common Issues

1. **Tesseract OCR not found**
   - The bundled Tesseract should work automatically
   - If issues persist, install system Tesseract: `apt-get install tesseract-ocr` (Linux) or download from GitHub (Windows)

2. **Upload fails**
   - Check file format (PNG, JPG, JPEG only)
   - Ensure file size is under 16MB
   - Verify screenshot is 16:9 resolution with English interface

3. **Agent recognition fails**
   - Ensure agent images are present in `agent-images/` folder
   - Check that agent portraits are clearly visible in screenshots

4. **Port already in use**
   - Change port in `app.py`: `app.run(port=5001)`
   - Or kill existing process using port 5000

### Performance Tips

- **Batch Processing**: Upload multiple screenshots at once for efficiency
- **Image Quality**: Higher quality screenshots = better OCR accuracy
- **Network Access**: Application works on local network for team collaboration

## 🛠 Development

### Tech Stack
- **Backend**: Python Flask
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Image Processing**: OpenCV, Tesseract OCR
- **Agent Recognition**: SIFT/ORB feature matching

### API Endpoints
- `GET /` - Main upload page
- `GET /config` - Configuration page
- `POST /upload` - Process screenshots
- `POST /update_config` - Update configuration

## 📊 Features Comparison

| Feature | Desktop App | Web App |
|---------|-------------|---------|
| File Upload | Folder-based | Drag & Drop |
| Configuration | Manual editing | Web interface |
| Results | CSV + Clipboard | CSV + Web view |
| Batch Processing | ✅ | ✅ |
| Agent Recognition | ✅ | ✅ |
| Map Detection | ✅ | ✅ |
| Team Filtering | ✅ | ✅ |
| Cross-platform | Windows only | Any OS |
| Network Access | Local only | Network-wide |
| Mobile Support | ❌ | ✅ |

## 🎯 Next Steps

The web application is fully functional and ready for use. Consider these enhancements:

- **Database Integration**: Store historical data
- **User Authentication**: Multi-team support
- **Advanced Analytics**: Match statistics and trends
- **API Integration**: Connect with external tools
- **Cloud Deployment**: Host on cloud platforms

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the original README.md for additional context
3. Ensure all dependencies are properly installed
4. Verify Tesseract OCR is working correctly

---

**Status**: ✅ Web application successfully deployed and tested
**Last Updated**: June 6, 2025