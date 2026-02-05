═══════════════════════════════════════════════════════════════
              HOW TO RUN GAMEFIT - SIMPLE GUIDE
═══════════════════════════════════════════════════════════════

🎯 QUICK ANSWER: Which file do I run?

  OPTION 1: If you have Python installed
    👉 Run: app.py
    
  OPTION 2: If you DON'T have Python
    👉 Run: GameFit.exe (in dist folder)

═══════════════════════════════════════════════════════════════

🚀 METHOD 1: RUN WITH PYTHON (Easiest)
═══════════════════════════════════════════════════════════════

Step 1: Open PowerShell
  • Click Start Menu
  • Type: PowerShell
  • Click: Windows PowerShell

Step 2: Navigate to project folder
  • Copy this command and paste it in PowerShell:
  
    cd "e:\bacup\Programming\Python\GameFit"
  
  • Press ENTER

Step 3: Run the application
  • Copy this command and paste it:
  
    python app.py
  
  • Press ENTER

Step 4: Wait for message like this:
  
  "Running on http://127.0.0.1:5000"
  
  This means the app is running!

Step 5: Open browser
  • Open any browser (Chrome, Edge, Firefox)
  • Type in address bar: http://localhost:5000
  • Press ENTER

Step 6: Use the app!
  • You'll see the GameFit homepage
  • Click "Start System Scan" button
  • Wait for results
  • Done! 🎉

═══════════════════════════════════════════════════════════════

🎮 METHOD 2: RUN WITH EXE (Simplest - No Python needed)
═══════════════════════════════════════════════════════════════

Step 1: Build the EXE (Do this ONCE)
  
  • Open PowerShell in the project folder
  • Copy this command:
  
    build_exe.bat
  
  • Press ENTER
  • Wait 3-5 minutes for build to complete
  • You'll see: "Build complete!"

Step 2: Find the EXE
  
  • In File Explorer, go to: e:\bacup\Programming\Python\New folder\dist
  • Look for: GameFit.exe
  • This is your application!

Step 3: Run it!
  
  • Double-click GameFit.exe
  • Browser opens automatically
  • App loads
  • Click "Start System Scan"
  • Done! 🎉

Step 4: Share it!
  
  • You can copy GameFit.exe and share it with anyone
  • No Python needed on their computer
  • They just double-click and it runs!

═══════════════════════════════════════════════════════════════

📁 FILE GUIDE - What does each file do?
═══════════════════════════════════════════════════════════════

FILES YOU NEED TO RUN:

  app.py ⭐⭐⭐ MAIN FILE - RUN THIS
    • This is the main application
    • Contains Flask server
    • Handles all logic
    • This is what you run!

  build_exe.bat ⭐⭐ ONLY IF BUILDING EXE
    • Builds standalone executable
    • Run this ONCE to create GameFit.exe
    • Then use GameFit.exe instead

FILES YOU DON'T NEED TO RUN:

  hardware_checker.py
    • Used by app.py internally
    • Detects system specs
    • Don't run directly

  test_app.py
    • For testing only
    • Run if you want to test features
    • Not needed for normal use

  debug_app.py
    • For debugging
    • Not needed for normal use

  custom_games.csv
    • Game database
    • Not executable
    • Used by app.py

  requirements.txt
    • List of dependencies
    • Not executable
    • For reference only

  templates/index.html
    • Web page code
    • Not executable
    • Used by app.py

FOLDERS YOU CAN IGNORE:

  __pycache__/
    • Python cache files
    • Auto-generated
    • Can be deleted

  dist/
    • Contains GameFit.exe after building
    • This is your final executable

  .venv/
    • Python environment
    • Already set up
    • Don't touch

═══════════════════════════════════════════════════════════════

✅ COMPLETE STEP-BY-STEP INSTRUCTIONS
═══════════════════════════════════════════════════════════════

OPTION A: Run with Python (Right now, instantly)
────────────────────────────────────────────────

1. Open PowerShell
2. Paste: cd "e:\bacup\Programming\Python\New folder"
3. Press ENTER
4. Paste: python app.py
5. Press ENTER
6. Open browser: http://localhost:5000
7. Click "Start System Scan"
8. Enjoy! 🎮

OPTION B: Build EXE first (then share with anyone)
────────────────────────────────────────────────

1. Open PowerShell
2. Paste: cd "e:\bacup\Programming\Python\New folder"
3. Press ENTER
4. Paste: build_exe.bat
5. Press ENTER
6. Wait 3-5 minutes
7. Go to: dist folder
8. Double-click: GameFit.exe
9. Browser opens automatically
10. Click "Start System Scan"
11. Enjoy! 🎮

═══════════════════════════════════════════════════════════════

❓ TROUBLESHOOTING
═══════════════════════════════════════════════════════════════

Q: "ModuleNotFoundError: No module named 'flask'"
A: Run this in PowerShell:
   pip install flask psutil gputil requests

Q: "App won't start"
A: Make sure you're in the correct folder:
   cd "e:\bacup\Programming\Python\GameFit"

Q: "Browser won't open"
A: Open manually: http://localhost:5000 in your browser

Q: "Can't find GameFit.exe"
A: Make sure you ran build_exe.bat first
   Then check dist/ folder

Q: "App crashes after clicking START"
A: Check your internet connection (needed for API)
   Or check PowerShell for error messages

═══════════════════════════════════════════════════════════════

🎯 REMEMBER:
═══════════════════════════════════════════════════════════════

TO RUN THE APP:
  Option 1: python app.py (if Python installed)
  Option 2: GameFit.exe (if you built it)

THAT'S IT! Just run one of these!

═══════════════════════════════════════════════════════════════

💡 CHEAT SHEET - Copy & Paste Commands
═══════════════════════════════════════════════════════════════

To navigate to folder:
  cd "e:\bacup\Programming\Python\GameFit"

To run the app:
  python app.py

To build EXE:
  build_exe.bat

To run tests:
  python test_app.py

═══════════════════════════════════════════════════════════════

✅ NEXT STEPS:

1. Choose Option A or B (see above)
2. Follow the steps exactly
3. That's all!

═══════════════════════════════════════════════════════════════
