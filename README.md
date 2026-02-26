# 🎮 GAMEFIT - CLEAN & ORGANIZED

**Game Compatibility Checker - Check if your PC can run any game!**

═══════════════════════════════════════════════════════════════

## 🚀 START HERE (3 STEPS!)

### Option 1: Run with Python (Right Now!)
```
cd "e:\bacup\Programming\Python\GameFit"
python app.py
```
Then open: **http://localhost:5000**

### Option 3: Run with Batch File (Easy Double-Click)
```
run_app.bat
```
Then open: **http://localhost:5000**

═══════════════════════════════════════════════════════════════

## ⚠️ ABOUT API ERRORS

**You might see RAWG API errors in the console - this is normal!**

- **SSL Errors**: Network connectivity issues (safe to ignore)
- **Timeouts**: API is slow sometimes (games still work without images)
- **NoneType Errors**: API returned unexpected data (handled gracefully)

**The app works perfectly even with these errors!** Games display with default placeholders when API fails.

═══════════════════════════════════════════════════════════════

� **Read `docs/HOW_TO_RUN.md` for complete detailed instructions!**

═══════════════════════════════════════════════════════════════

## 📁 FOLDER STRUCTURE (SUPER CLEAN!)

```
root/
├── app.py ⭐ MAIN FILE - RUN THIS!
├── build_exe.bat - Build executable
├── requirements.txt - Dependencies
│
├── 📚 docs/ - All documentation
│   ├── HOW_TO_RUN.md (READ THIS FIRST!)
│   ├── QUICK_START.md
│   ├── PROJECT_SUMMARY.md
│   ├── SUBMISSION_CHECKLIST.md
│   └── ... other guides
│
├── 📊 data/ - Game database
│   └── custom_games.csv (14 games)
│
├── 🌐 templates/ - Web page
│   └── index.html
│
├── 🎨 static/ - Styling
│   └── style.css
│
└── 💾 dist/ - Created after build_exe.bat
    └── GameFit.exe
```

═══════════════════════════════════════════════════════════════

## 📚 DOCUMENTATION

All guides are in the **`docs/`** folder:

| File | What It Is |
|------|-----------|
| **HOW_TO_RUN.md** | Step-by-step instructions (START HERE!) |
| QUICK_START.md | Quick reference |
| PROJECT_SUMMARY.md | Project details |
| SUBMISSION_CHECKLIST.md | Final verification checklist |

═══════════════════════════════════════════════════════════════

## 🎮 FEATURES

✅ Detects: CPU, RAM, GPU, Storage
✅ Checks: 14 popular games
✅ Beautiful modern UI
✅ One-click system scan
✅ Real game images
✅ Fast & responsive

═══════════════════════════════════════════════════════════════

## 🎯 GAMES (14 Total)

**AAA:** Cyberpunk 2077, Red Dead Redemption 2, The Witcher 3, Elden Ring, Baldur's Gate 3, Dragon's Dogma 2, Starfield


## ➕ ADDING MORE GAMES

You can expand the catalogue without rebuilding the application:

1. **Edit the CSV seed file** (`docs/seed/custom_games.csv`) and restart the
   server (or delete `data/gamefit.db` so `migrate_csv_to_database()` runs
   again).  This is handy for bulk imports.

2. **Use the new API endpoint** to add a single title programmatically:

   ```http
   POST /api/add-game
   Content-Type: application/json

   {
     "name": "Your Game Name",
     "os_min": "Windows 10",
     "cpu_min": "Intel i5-8400",
     "ram_min": "8",
     "gpu_min": "GTX 1050",
     "vram_min": "2",
     "storage_min": "50"
   }
   ```

   The server will insert the record and clear the in-memory cache so the
   game becomes visible immediately when you scan.


## 🎯 GAMES (14 Total)

**AAA:** Cyberpunk 2077, Red Dead Redemption 2, The Witcher 3, Elden Ring, Baldur's Gate 3, Dragon's Dogma 2, Starfield

**Indie:** Stardew Valley, Minecraft

**Online:** Counter-Strike 2, Fortnite, Final Fantasy XIV

**Simulation:** The Sims 4, Palworld

═══════════════════════════════════════════════════════════════

## 🛠️ REQUIREMENTS

- Python 3.14+ (or use GameFit.exe)
- Internet (for game images)

═══════════════════════════════════════════════════════════════

## 📖 COMPLETE DOCUMENTATION

For everything: See **`docs/`** folder

**👉 Start with: `docs/HOW_TO_RUN.md`**

```bash
# Install PyInstaller
pip install pyinstaller

# Build executable
pyinstaller --onefile --windowed --name="GameFit" ^
    --add-data "templates;templates" ^
    --add-data "static;static" ^
    --add-data "custom_games.csv;." ^
    app.py

# Result: dist/GameFit.exe
```

## 🎯 How It Works

1. **Click "Start System Scan"** button on home page
2. **Application analyzes** your PC's hardware
3. **Compares** your specs with game requirements
4. **Displays** compatible games with requirements
5. **Shows** game images and specifications

## 🛠️ Technology Stack

| Component | Technology |
|-----------|-----------|
| Backend | Python 3.11+ |
| Web Framework | Flask |
| Frontend | HTML5, CSS3, JavaScript |
| Styling | Tailwind CSS |
| Icons | FontAwesome |
| System Info | psutil, GPUtil |
| APIs | RAWG Game API |
| Packaging | PyInstaller |

## 📋 Project Structure

```
GameFit/
├── app.py                      # Main Flask application
├── utils/                      # Utility modules
│   └── hardware_checker.py     # System analysis module
├── data/                       # Runtime data
│   └── gamefit.db              # Canonical SQLite database (do not commit large DBs if undesired)
├── templates/
│   └── index.html              # Web UI
├── static/
│   └── style.css               # Styling (if needed)
├── .venv/                      # Virtual environment
├── scripts/                    # Build and helper scripts
│   └── build_exe.bat
└── requirements.txt            # Python dependencies
```

## 📊 Games in Database

1. Red Dead Redemption 2
2. Cyberpunk 2077
3. Elden Ring
4. Stardew Valley
5. Minecraft
6. The Witcher 3
7. Baldur's Gate 3
8. Starfield
9. Palworld
10. Dragon's Dogma 2
11. Final Fantasy XIV
12. Counter-Strike 2
13. Fortnite
14. The Sims 4

*(Database is expandable - add more games to `custom_games.csv`)*

## 🔧 System Requirements

- **OS**: Windows 7 or later
- **Python**: 3.7+ (only if running from source)
- **RAM**: 2GB minimum
- **Storage**: 50MB

## 📝 Adding More Games

1. Open `custom_games.csv`
2. Add a new row with game details:
   ```
   Game Name,Windows 10,Windows 11,CPU,CPU,RAM,RAM,GPU,GPU,VRAM,VRAM,Storage,Storage,Release Date
   ```
3. Save and restart the application

## 🎓 For Final Year Project

This application demonstrates:

- ✅ **Backend Development** - Flask web framework
- ✅ **Frontend Development** - Modern responsive UI
- ✅ **System Programming** - Hardware detection
- ✅ **API Integration** - External game API
- ✅ **Data Management** - CSV database handling
- ✅ **Desktop Deployment** - PyInstaller packaging
- ✅ **UX/UI Design** - Professional interface
- ✅ **Software Architecture** - MVC pattern

## 📖 Documentation

See `FINAL_YEAR_PROJECT_GUIDE.md` for detailed information about:
- Architecture
- Deployment options
- Building installers
- Creating a professional package
- Project report guidelines

## 🐛 Troubleshooting

### "No compatible games found"
- Your PC specifications are below game minimums
- This is normal for integrated graphics
- Try adding games with lower requirements

### Application won't start
- Ensure Python 3.7+ is installed
- Check internet connection for game images
- Run from project directory
- Check that `custom_games.csv` exists

### EXE won't run
- Ensure Windows Defender allows it
- Run as Administrator if needed
- Check system requirements above

## 👨‍💻 Developer Info

- **Project**: GameFit - Game Compatibility Checker
- **Purpose**: Final Year Project
- **Version**: 1.0
- **Author**: Your Name
- **License**: MIT

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Read `FINAL_YEAR_PROJECT_GUIDE.md`
3. Review `app.py` code comments

## 🎁 Future Enhancements

- [ ] Expand game database
- [ ] Add performance benchmarking
- [ ] Export results as PDF
- [ ] Settings/preferences panel
- [ ] Performance history tracking
- [ ] Multiplayer game detection
- [ ] Hardware upgrade suggestions
- [ ] Community game ratings

## 📄 License

MIT License - Feel free to use and distribute

---

**Ready to use?**

1. **Development**: Run `python app.py`
2. **Production**: Double-click `GameFit.exe`
3. **Build**: Run `build_exe.bat`

Enjoy! 🚀
