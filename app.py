from flask import Flask, render_template, jsonify, request
import csv
import json
import platform
import psutil
import sqlite3
import os
try:
    import GPUtil
except Exception:
    GPUtil = None
import requests
import sys
import logging
import webbrowser
import time
import shutil
import threading


# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Handle PyInstaller bundled paths
if getattr(sys, 'frozen', False):
    app.template_folder = os.path.join(sys._MEIPASS, 'templates')
    app.static_folder = os.path.join(sys._MEIPASS, 'static')

RAWG_API_KEY = "c75f5df597d54311b52df3ad15bd4a7d"
# Handle PyInstaller bundled data path
if getattr(sys, 'frozen', False):
    # Running as bundled exe - include seed CSV if bundled
    DATASET = os.path.join(sys._MEIPASS, "docs", "seed", "custom_games.csv")
    DB_PATH = os.path.join(sys._MEIPASS, "data", "gamefit.db")
else:
    # Use canonical DB; keep seed CSV in docs/seed for edits
    DATASET = os.path.join("docs", "seed", "custom_games.csv")
    DB_PATH = os.path.join("data", "gamefit.db")

# ========== PERFORMANCE OPTIMIZATION: Caching & DB Pooling =========
# Global database connection (pooling) - reuse instead of creating new ones
db_connection = None

# System info cache (expires after 60 seconds)
_system_cache = {"data": None, "timestamp": 0}
SYSTEM_CACHE_EXPIRY = 60  # seconds

# Games cache (loaded once on startup)
GAMES_CACHE = []
GAMES_CACHE_DETAILS = {}  # Pre-loaded game details from JSON
# ====================================================================

# ========== DATABASE CONNECTION POOLING =========
def get_db_connection():
    """Get or create a persistent database connection (pooling)"""
    global db_connection
    try:
        if db_connection is None:
            db_connection = sqlite3.connect(DB_PATH, check_same_thread=False, timeout=10)
            db_connection.row_factory = sqlite3.Row
            # Enable query optimization
            db_connection.execute("PRAGMA cache_size = 10000")
            db_connection.execute("PRAGMA synchronous = NORMAL")
            logger.info("Database connection pool initialized")
        return db_connection
    except Exception as e:
        logger.error(f"Failed to create DB connection: {e}")
        return sqlite3.connect(DB_PATH, check_same_thread=False)

# Database initialization
def init_database():
    """Initialize the SQLite database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            os_min TEXT,
            os_rec TEXT,
            cpu_min TEXT,
            cpu_rec TEXT,
            ram_min TEXT,
            ram_rec TEXT,
            gpu_min TEXT,
            gpu_rec TEXT,
            vram_min TEXT,
            vram_rec TEXT,
            storage_min TEXT,
            storage_rec TEXT,
            release_date TEXT
        )
    ''')
    
    conn.commit()
    # Don't close - we're using connection pooling

def migrate_csv_to_database():
    """Migrate games from CSV to SQLite database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if database already has games
        cursor.execute('SELECT COUNT(*) FROM games')
        if cursor.fetchone()[0] > 0:
            logger.info("Database already populated, skipping migration")
            return
        
        logger.info(f"Migrating games from {DATASET} to database...")
        
        with open(DATASET, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    cursor.execute('''
                        INSERT INTO games (name, os_min, os_rec, cpu_min, cpu_rec, 
                                          ram_min, ram_rec, gpu_min, gpu_rec, 
                                          vram_min, vram_rec, storage_min, storage_rec, release_date)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        row['name'],
                        row['os_min'],
                        row.get('os_rec', ''),
                        row['cpu_min'],
                        row['cpu_rec'],
                        row['ram_min'],
                        row['ram_rec'],
                        row['gpu_min'],
                        row['gpu_rec'],
                        row['vram_min'],
                        row['vram_rec'],
                        row['storage_min'],
                        row['storage_rec'],
                        row.get('release_date', '')
                    ))
                except sqlite3.IntegrityError:
                    # Game already exists, skip
                    pass
                except Exception as e:
                    logger.warning(f"Error migrating game: {e}")
        
        conn.commit()
        logger.info("Migration completed successfully")
    except Exception as e:
        logger.error(f"Migration failed: {e}")

def get_all_games():
    """Get all games from the database with in-memory caching"""
    global GAMES_CACHE
    
    # Return cached games if available
    if GAMES_CACHE:
        return GAMES_CACHE
    
    # Load from database if not cached
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM games')
        GAMES_CACHE = [dict(row) for row in cursor.fetchall()]
        logger.info(f"Loaded {len(GAMES_CACHE)} games into memory cache")
        return GAMES_CACHE
    except Exception as e:
        logger.error(f"Error fetching games: {e}")
        return []


def add_game_to_db(game_data):
    """Insert a new game record and invalidate the cache."""
    global GAMES_CACHE
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR IGNORE INTO games (name, os_min, os_rec, cpu_min, cpu_rec,
                                      ram_min, ram_rec, gpu_min, gpu_rec,
                                      vram_min, vram_rec, storage_min, storage_rec, release_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            game_data.get('name',''),
            game_data.get('os_min',''),
            game_data.get('os_rec',''),
            game_data.get('cpu_min',''),
            game_data.get('cpu_rec',''),
            game_data.get('ram_min',''),
            game_data.get('ram_rec',''),
            game_data.get('gpu_min',''),
            game_data.get('gpu_rec',''),
            game_data.get('vram_min',''),
            game_data.get('vram_rec',''),
            game_data.get('storage_min',''),
            game_data.get('storage_rec',''),
            game_data.get('release_date','')
        ))
        conn.commit()
        GAMES_CACHE = []  # invalidate cache
        logger.info(f"Added new game to DB: {game_data.get('name')}")
        return True
    except Exception as e:
        logger.error(f"Failed to add game: {e}")
        return False

def format_cpu_info(raw_cpu_string):
    """
    Format raw CPU string into user-friendly format
    Examples: "Intel Core i3-2310M (2C/4T)" or "AMD Ryzen 5 3600 (6C/12T)"
    """
    try:
        import subprocess
        import re
        # Try PowerShell to get actual CPU model  
        ps_command = 'Get-WmiObject Win32_Processor -Property Name | Select-Object -ExpandProperty Name'
        result = subprocess.run(
            ['powershell', '-NoProfile', '-Command', ps_command],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            cpu_name = result.stdout.strip()
            if cpu_name and len(cpu_name) > 0:
                # Simple approach: remove parentheses content, special chars, and clean up
                # Remove (R) and (TM) along with any other text in parentheses for now
                cpu_name = re.sub(r'\([^)]*\)', '', cpu_name)
                # Clean up double spaces
                cpu_name = re.sub(r'\s+', ' ', cpu_name).strip()
                return cpu_name
    except Exception as e:
        logger.debug(f"PowerShell CPU query failed: {e}")
    
    # Fallback: Try to clean up the default platform.processor() output
    cpu_str = raw_cpu_string.strip()
    
    # If it's already in a readable format, return it
    if 'Intel Core' in cpu_str or 'AMD Ryzen' in cpu_str or 'Pentium' in cpu_str or 'Atom' in cpu_str:
        return cpu_str
    
    # Try to extract brand and model from technical string
    if 'Intel' in cpu_str:
        return "Intel Processor"
    elif 'AMD' in cpu_str:
        return "AMD Processor"
    else:
        # Return original if we can't parse it
        return cpu_str if cpu_str else "Unknown Processor"

def get_cpu_core_info():
    """Get physical cores and logical cores count"""
    try:
        physical_cores = psutil.cpu_count(logical=False)
        logical_cores = psutil.cpu_count(logical=True)
        return physical_cores, logical_cores
    except Exception:
        return None, None

def get_system_info():
    """Get system info with caching (cached for 60 seconds)"""
    global _system_cache
    
    current_time = time.time()
    # Return cached data if still valid
    if _system_cache["data"] and (current_time - _system_cache["timestamp"]) < SYSTEM_CACHE_EXPIRY:
        logger.debug("Returning cached system info")
        return _system_cache["data"]
    
    logger.info("Collecting fresh system info")
    try:
        # Try to get GPU info using GPUtil first
        gpu_name = "Integrated Graphics"
        gpu_vram = 2
        if GPUtil:
            try:
                gpus = GPUtil.getGPUs()
                if gpus:
                    gpu_name = gpus[0].name
                    gpu_vram = gpus[0].memoryTotal / 1024  # Convert to GB
                else:
                    gpu_name = "Intel HD Graphics"  # Common integrated GPU
                    gpu_vram = 2  # Assume 2GB for integrated
            except Exception:
                gpu_name = "Intel HD Graphics"
                gpu_vram = 2
        else:
            # Fallback to wmic on Windows
            try:
                import subprocess
                result = subprocess.run(['wmic', 'path', 'win32_videocontroller', 'get', 'name'], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    if len(lines) > 1:
                        gpu_name = lines[1].strip()
                        # Assume VRAM based on name or default
                        if 'nvidia' in gpu_name.lower():
                            gpu_vram = 4  # Default for NVIDIA
                        elif 'amd' in gpu_name.lower() or 'radeon' in gpu_name.lower():
                            gpu_vram = 4  # Default for AMD
                        else:
                            gpu_vram = 2  # Integrated
                    else:
                        gpu_name = "Integrated Graphics"
                        gpu_vram = 2
                else:
                    gpu_name = "Integrated Graphics"
                    gpu_vram = 2
            except Exception:
                gpu_name = "Integrated Graphics"
                gpu_vram = 2
    except Exception:
        gpu_name = "Integrated Graphics"
        gpu_vram = 2  # Fallback

    if platform.system() == 'Windows':
        drive = os.getcwd().split(os.sep)[0] + os.sep
    else:
        drive = '/'
    try:
        storage_gb = round(psutil.disk_usage(drive).total / (1024**3), 2)
    except:
        storage_gb = 500  # Fallback

    info = {
        "OS": platform.system() + " " + platform.release(),
        "CPU": format_cpu_info(platform.processor()),
        "RAM (GB)": round(psutil.virtual_memory().total / (1024**3), 2),
        "GPU": gpu_name,
        "VRAM (GB)": round(gpu_vram, 2),
        "Storage (GB)": storage_gb
    }
    
    # Add CPU core information
    physical_cores, logical_cores = get_cpu_core_info()
    if physical_cores and logical_cores:
        info["CPU"] = f"{info['CPU']} ({physical_cores}C/{logical_cores}T)"
    
    logger.info(f"System info collected: {info}")
    
    # Cache the system info
    _system_cache["data"] = info
    _system_cache["timestamp"] = current_time
    
    return info

def parse_size(value):
    try:
        if not value:
            return 0
        # Handle both numbers and text with GB/MB suffixes
        value = str(value).lower().strip()
        value = value.replace("gb", "").replace("mb", "").strip()
        return float(value) if value else 0
    except:
        return 0

def compute_compatibility(game, system_info):
    """Return a compatibility percentage (0-100) and a colour string (hsl) based on system vs game requirements.

    Only RAM, VRAM and storage are compared numerically; other fields are ignored.
    If a requirement is missing or zero it is treated as satisfied.
    """
    try:
        ram_req = parse_size(game.get("ram_min", 0))
        vram_req = parse_size(game.get("vram_min", 0))
        storage_req = parse_size(game.get("storage_min", 0))

        sys_ram = system_info.get("RAM (GB)", 0)
        sys_vram = system_info.get("VRAM (GB)", 0)
        sys_storage = system_info.get("Storage (GB)", 0)

        # if there are no explicit requirements at all we treat the game as not
        # applicable rather than fully compatible.  this handles placeholder
        # search results and any weird empty rows.
        if ram_req <= 0 and vram_req <= 0 and storage_req <= 0:
            return 0, "hsl(0,80%,45%)"

        comps = []
        for req, sys in ((ram_req, sys_ram), (vram_req, sys_vram), (storage_req, sys_storage)):
            if req > 0:
                comps.append(min(sys / req, 1))
            else:
                comps.append(1)

        if comps:
            percent = int((sum(comps) / len(comps)) * 100)
        else:
            percent = 0

        # hue 0 = red, 120 = green; scale linearly
        hue = percent * 1.2
        color = f"hsl({hue:.0f}, 80%, 45%)"
        return percent, color
    except Exception as e:
        logger.debug(f"Compatibility computation failed: {e}")
        return 0, "hsl(0,80%,45%)"


def get_compatible_games(system_info):
    """Return every game with a non-zero compatibility score.

    Previously this helper filtered out anything that didn't meet all of the
    minimum requirements, which meant the UI only ever saw 100% entries.  For
    the new grading display we want to show the full range (10–100%).
    """
    logger.debug("Computing compatibility for all games")
    eligible = []

    for game in get_all_games():
        try:
            percent, color = compute_compatibility(game, system_info)
            if percent > 0:
                # don't mutate original cache inadvertently
                g = game.copy()
                g["compatibility_percent"] = percent
                g["compatibility_color"] = color
                eligible.append(g)
        except Exception as e:
            logger.debug(f"Skipping game during compatibility calc: {e}")

    # sort highest compatibility first so front end can slice(0,4) safely
    eligible.sort(key=lambda x: x.get("compatibility_percent", 0), reverse=True)
    return eligible

def fetch_game_details(game_name):
    try:
        url = f"https://api.rawg.io/api/games?key={RAWG_API_KEY}&search={game_name}"
        res = requests.get(url, timeout=10, verify=False)  # Increased timeout and disabled SSL verification for reliability
        if res.status_code == 200:
            data = res.json()
            if data.get("results"):
                game_data = data["results"][0]
                platforms = []
                stores = []
                
                # Safely extract platforms
                if game_data.get("platforms") and isinstance(game_data["platforms"], list):
                    platforms = [p["platform"]["name"] for p in game_data["platforms"] if p.get("platform")]
                
                # Safely extract stores  
                if game_data.get("stores") and isinstance(game_data["stores"], list):
                    stores = [s["store"]["name"] for s in game_data["stores"] if s.get("store")]
                    
                return {
                    "image": game_data.get("background_image", ""),
                    "platforms": platforms,
                    "stores": stores
                }
    except requests.exceptions.Timeout:
        logger.warning(f"RAWG API timeout for {game_name} - using defaults")
    except requests.exceptions.SSLError:
        logger.warning(f"RAWG SSL error for {game_name} - using defaults") 
    except requests.exceptions.ConnectionError:
        logger.warning(f"RAWG connection error for {game_name} - using defaults")
    except Exception as e:
        logger.warning(f"RAWG fetch error for {game_name}: {str(e)[:50]}...")
    return {"image": "", "platforms": [], "stores": []}

# Function to load cached game details from JSON files
def load_cached_game_details(game_name):
    details_path = os.path.join("static", "game_details", f"{game_name}.json")
    if os.path.exists(details_path):
        try:
            with open(details_path, "r", encoding="utf-8") as details_file:
                return json.load(details_file)
        except Exception as e:
            logger.error(f"Failed to load cached details for {game_name}: {e}")
    return {"platforms": [], "stores": []}

# Function to download and save game images and details locally
def download_game_images():
    """Download and cache game images and details, pre-load into memory"""
    global GAMES_CACHE_DETAILS
    
    logger.info("Downloading game images and details...")
    image_folder = os.path.join("static", "images")
    details_folder = os.path.join("static", "game_details")
    os.makedirs(image_folder, exist_ok=True)
    os.makedirs(details_folder, exist_ok=True)

    try:
        # Get all games
        all_games = get_all_games()
        
        for game in all_games:
            game_name = game["name"]
            image_path = os.path.join(image_folder, f"{game_name}.jpg")
            details_path = os.path.join(details_folder, f"{game_name}.json")

            # Check if both image and details already exist
            if os.path.exists(image_path) and os.path.exists(details_path):
                logger.debug(f"Data for {game_name} already exists, skipping download.")
                # Pre-load cached details into memory
                if game_name not in GAMES_CACHE_DETAILS:
                    try:
                        with open(details_path, "r", encoding="utf-8") as f:
                            GAMES_CACHE_DETAILS[game_name] = json.load(f)
                    except Exception as e:
                        logger.debug(f"Failed to load cached details for {game_name}: {e}")
                continue

            details = fetch_game_details(game_name)
            
            # Download image if it doesn't exist
            if not os.path.exists(image_path):
                image_url = details.get("image")
                if image_url:
                    try:
                        response = requests.get(image_url, stream=True, timeout=10)
                        if response.status_code == 200:
                            with open(image_path, "wb") as img_file:
                                shutil.copyfileobj(response.raw, img_file)
                            logger.info(f"Downloaded image for {game_name}")
                    except Exception as e:
                        logger.error(f"Failed to download image for {game_name}: {e}")
            
            # Save game details (platforms and stores) as JSON
            if not os.path.exists(details_path):
                try:
                    game_details = {
                        "platforms": details.get("platforms", []),
                        "stores": details.get("stores", [])
                    }
                    with open(details_path, "w", encoding="utf-8") as details_file:
                        json.dump(game_details, details_file, indent=2)
                    GAMES_CACHE_DETAILS[game_name] = game_details
                    logger.info(f"Downloaded details for {game_name}")
                except Exception as e:
                    logger.error(f"Failed to save details for {game_name}: {e}")
    except Exception as e:
        logger.error(f"Error downloading game images: {e}")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/system")
def system_specs():
    """Get system specs with 60-second browser cache"""
    response = jsonify(get_system_info())
    response.headers["Cache-Control"] = "public, max-age=60"
    return response

@app.route("/api/games")
def compatible_games():
    """Return games relevant to the current system.

    Without a query parameter this endpoint behaves exactly as before: it
    returns only games that meet the minimum RAM/VRAM/storage
    requirements.  When the `search` parameter is supplied the database is
    searched by name (case‑insensitive wildcard) and _all_ matching games are
    returned regardless of whether the machine actually fulfils the
    requirements; this allows the front end to offer a global search over the
    catalogue.  If a game is not present in the DB we still return a single
    entry with data from RAWG but compatibility will always be treated as
    0%.
    """
    logger.info("API /api/games called")
    specs = get_system_info()

    search_term = request.args.get("search", "").strip()
    games_list = []

    if search_term:
        logger.info(f"Searching for games matching '{search_term}'")
        conn = get_db_connection()
        cursor = conn.cursor()
        # case‑insensitive search
        cursor.execute("SELECT * FROM games WHERE name LIKE ? COLLATE NOCASE", (f"%{search_term}%",))
        rows = cursor.fetchall()
        if rows:
            games_list = [dict(r) for r in rows]
        else:
            # not in database; fall back to rawg for image/platforms but we can't
            # compute requirements so compatibility is 0
            logger.debug("No database entry found; returning placeholder entry")
            games_list = [{
                "name": search_term,
                "os_min": "",
                "os_rec": "",
                "cpu_min": "",
                "cpu_rec": "",
                "ram_min": "",
                "ram_rec": "",
                "gpu_min": "",
                "gpu_rec": "",
                "vram_min": "",
                "vram_rec": "",
                "storage_min": "",
                "storage_rec": "",
            }]
    else:
        # normal compatibility check
        games_list = get_compatible_games(specs)

    result = []
    for g in games_list:
        image_path = os.path.join("static", "images", f"{g['name']}.jpg")
        image_url = f"/{image_path}" if os.path.exists(image_path) else ""
        if not image_url:
            api_details = fetch_game_details(g['name'])
            image_url = api_details.get('image', '')
        if g['name'] in GAMES_CACHE_DETAILS:
            cached_details = GAMES_CACHE_DETAILS[g['name']]
        else:
            cached_details = load_cached_game_details(g["name"])

        percent, color = compute_compatibility(g, specs)

        result.append({
            "name": g["name"],
            "image": image_url,
            "platforms": cached_details.get("platforms", []),
            "stores": cached_details.get("stores", []),
            "os_min": g.get("os_min", ""),
            "os_rec": g.get("os_rec", ""),
            "cpu_min": g.get("cpu_min", ""),
            "cpu_rec": g.get("cpu_rec", ""),
            "ram_min": g.get("ram_min", ""),
            "ram_rec": g.get("ram_rec", ""),
            "gpu_min": g.get("gpu_min", ""),
            "gpu_rec": g.get("gpu_rec", ""),
            "vram_min": g.get("vram_min", ""),
            "vram_rec": g.get("vram_rec", ""),
            "storage_min": g.get("storage_min", ""),
            "storage_rec": g.get("storage_rec", ""),
            "compatibility_percent": percent,
            "compatibility_color": color,
        })

    response = jsonify({
        "system_info": specs,
        "games": result
    })
    # Browser cache for 5 minutes (300 seconds)
    response.headers["Cache-Control"] = "public, max-age=300"
    return response

@app.route("/api/game/<game_name>")
def game_details(game_name):
    """Fetch details for a specific game on-demand (API mode for online searches).

    This endpoint also returns compatibility percentage and colour so the
    modal can show a grade even when the card was populated via a search.
    """
    name = game_name.replace('_', ' ')
    details = fetch_game_details(name)

    # attempt to retrieve requirements from DB to compute compatibility
    specs = get_system_info()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM games WHERE name = ? COLLATE NOCASE", (name,))
    row = cursor.fetchone()
    if row:
        game_req = dict(row)
        percent, color = compute_compatibility(game_req, specs)
    else:
        percent, color = 0, "hsl(0,80%,45%)"

    details["compatibility_percent"] = percent
    details["compatibility_color"] = color

    response = jsonify(details)
    # Cache for 1 hour for online searches
    response.headers["Cache-Control"] = "public, max-age=3600"
    return response


@app.route('/api/add-game', methods=['POST'])
def api_add_game():
    """Receive JSON payload and add a new game to the database.

    Expects at least a `name` field.  Optional fields mirror the CSV columns
    (os_min, cpu_min, ram_min, gpu_min, vram_min, storage_min, etc.).
    """
    payload = request.get_json(force=True)
    if not payload or 'name' not in payload:
        return jsonify({'success': False, 'error': 'name is required'}), 400

    success = add_game_to_db(payload)
    if success:
        return jsonify({'success': True}), 201
    return jsonify({'success': False, 'error': 'insert failed'}), 500

# Call the database initialization and download function when the app starts
if __name__ == "__main__":
    # Initialize database
    init_database()
    logger.info("Database initialized")
    
    # Migrate data from CSV if needed
    migrate_csv_to_database()
    
    # Download game images and details in background to avoid blocking startup
    download_thread = threading.Thread(target=download_game_images)
    download_thread.daemon = True
    download_thread.start()
    logger.info("GameFit server starting on http://127.0.0.1:5000")
    print("GameFit server starting on http://127.0.0.1:5000")
    print("Opening browser automatically...")
    webbrowser.open('http://127.0.0.1:5000')
    time.sleep(0.5)  # Brief pause

    try:
        app.run(host='127.0.0.1', port=5000, debug=False)
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        print(f"Failed to start server: {e}")
