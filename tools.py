import logging
from livekit.agents import function_tool, RunContext
import requests
from ddgs import DDGS
import os
import smtplib
from email.mime.multipart import MIMEMultipart  
from email.mime.text import MIMEText
from typing import Optional
import datetime
import webbrowser
import pyautogui
import psutil
import subprocess
import platform

@function_tool()
async def get_weather(
    context: RunContext,  # type: ignore
    city: str) -> str:
    """
    Get the current weather for a given city.
    """
    try:
        response = requests.get(
            f"https://wttr.in/{city}?format=3")
        if response.status_code == 200:
            logging.info(f"Weather for {city}: {response.text.strip()}")
            return response.text.strip()   
        else:
            logging.error(f"Failed to get weather for {city}: {response.status_code}")
            return f"Could not retrieve weather for {city}."
    except Exception as e:
        logging.error(f"Error retrieving weather for {city}: {e}")
        return f"An error occurred while retrieving weather for {city}." 

@function_tool()
async def search_web(
    context: RunContext,  # type: ignore
    query: str) -> str:
    """
    Search the web using DuckDuckGo.
    """
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=5))
            
            if not results:
                return f"No search results found for '{query}'."
            
            # Format the results into a readable string
            formatted_results = []
            for i, result in enumerate(results, 1):
                title = result.get('title', 'No title')
                body = result.get('body', 'No description')
                url = result.get('href', '')
                formatted_results.append(f"{i}. {title}\n   {body}\n   {url}")
            
            output = "\n\n".join(formatted_results)
            logging.info(f"Search results for '{query}': Found {len(results)} results")
            return output
    except Exception as e:
        logging.error(f"Error searching the web for '{query}': {e}")
        return f"An error occurred while searching the web for '{query}'."    

@function_tool()    
async def send_email(
    context: RunContext,  # type: ignore
    to_email: str,
    subject: str,
    message: str,
    cc_email: Optional[str] = None
) -> str:
    """
    Send an email through Gmail.
    
    Args:
        to_email: Recipient email address
        subject: Email subject line
        message: Email body content
        cc_email: Optional CC email address
    """
    try:
        # Gmail SMTP configuration
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        
        # Get credentials from environment variables
        gmail_user = os.getenv("GMAIL_USER")
        gmail_password = os.getenv("GMAIL_APP_PASSWORD")  # Use App Password, not regular password
        
        if not gmail_user or not gmail_password:
            logging.error("Gmail credentials not found in environment variables")
            return "Email sending failed: Gmail credentials not configured."
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = gmail_user
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # Add CC if provided
        recipients = [to_email]
        if cc_email:
            msg['Cc'] = cc_email
            recipients.append(cc_email)
        
        # Attach message body
        msg.attach(MIMEText(message, 'plain'))
        
        # Connect to Gmail SMTP server
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Enable TLS encryption
        server.login(gmail_user, gmail_password)
        
        # Send email
        text = msg.as_string()
        server.sendmail(gmail_user, recipients, text)
        server.quit()
        
        logging.info(f"Email sent successfully to {to_email}")
        return f"Email sent successfully to {to_email}"
        
    except smtplib.SMTPAuthenticationError:
        logging.error("Gmail authentication failed")
        return "Email sending failed: Authentication error. Please check your Gmail credentials."
    except smtplib.SMTPException as e:
        logging.error(f"SMTP error occurred: {e}")
        return f"Email sending failed: SMTP error - {str(e)}"
    except Exception as e:
        logging.error(f"Error sending email: {e}")
        return f"An error occurred while sending email: {str(e)}"


# ========================================
# DESKTOP AUTOMATION TOOLS (from Nevira)
# ========================================

@function_tool()
async def control_volume(
    context: RunContext,  # type: ignore
    action: str
) -> str:
    """
    Control system volume on Windows.
    
    Args:
        action: Must be one of: "up", "down", "mute", "unmute"
    """
    try:
        action = action.lower().strip()
        
        if action in ["up", "increase", "raise"]:
            pyautogui.press("volumeup")
            logging.info("Volume increased")
            return "Volume increased, Boss."
        elif action in ["down", "decrease", "lower"]:
            pyautogui.press("volumedown")
            logging.info("Volume decreased")
            return "Volume decreased, Boss."
        elif action in ["mute", "silence"]:
            pyautogui.press("volumemute")
            logging.info("Volume muted")
            return "Volume muted, Boss."
        elif action in ["unmute"]:
            pyautogui.press("volumemute")  # Toggle mute
            logging.info("Volume unmuted")
            return "Volume unmuted, Boss."
        else:
            return f"Invalid action '{action}'. Use: up, down, mute, or unmute."
            
    except Exception as e:
        logging.error(f"Error controlling volume: {e}")
        return f"Could not control volume: {str(e)}"


@function_tool()
async def open_application(
    context: RunContext,  # type: ignore
    app_name: str
) -> str:
    """
    Open Windows applications like Calculator, Notepad, Paint, etc.
    
    Args:
        app_name: Name of the application (calculator, notepad, paint, cmd, explorer)
    """
    try:
        app_name = app_name.lower().strip()
        
        apps = {
            "calculator": "calc.exe",
            "notepad": "notepad.exe",
            "paint": "mspaint.exe",
            "cmd": "cmd.exe",
            "command prompt": "cmd.exe",
            "explorer": "explorer.exe",
            "file explorer": "explorer.exe",
            "task manager": "taskmgr.exe",
            "settings": "ms-settings:",
        }
        
        if app_name in apps:
            if apps[app_name].startswith("ms-"):
                # For Windows 10/11 URI schemes
                webbrowser.open(apps[app_name])
            else:
                os.startfile(apps[app_name])
            logging.info(f"Opened {app_name}")
            return f"Opening {app_name} now, Boss."
        else:
            available = ", ".join(apps.keys())
            return f"I don't know how to open '{app_name}'. Available apps: {available}"
            
    except Exception as e:
        logging.error(f"Error opening application '{app_name}': {e}")
        return f"Could not open {app_name}: {str(e)}"


@function_tool()
async def close_application(
    context: RunContext,  # type: ignore
    app_name: str
) -> str:
    """
    Close Windows applications.
    
    Args:
        app_name: Name of the application to close (calculator, notepad, paint)
    """
    try:
        app_name = app_name.lower().strip()
        
        # Map app names to their process names
        app_processes = {
            "calculator": ["Calculator.exe", "ApplicationFrameHost.exe"],
            "notepad": ["notepad.exe"],
            "paint": ["mspaint.exe"],
            "chrome": ["chrome.exe"],
            "edge": ["msedge.exe"],
        }
        
        if app_name not in app_processes:
            available = ", ".join(app_processes.keys())
            return f"I don't know how to close '{app_name}'. Available: {available}"
        
        # Kill the processes
        for process_name in app_processes[app_name]:
            if platform.system() == "Windows":
                os.system(f'taskkill /f /im {process_name} 2>nul')
        
        logging.info(f"Closed {app_name}")
        return f"Closed {app_name}, Boss."
        
    except Exception as e:
        logging.error(f"Error closing application '{app_name}': {e}")
        return f"Could not close {app_name}: {str(e)}"


@function_tool()
async def open_website(
    context: RunContext,  # type: ignore
    site_name: str
) -> str:
    """
    Open popular websites or social media platforms.
    
    Args:
        site_name: Name of the site (youtube, facebook, instagram, whatsapp, discord, twitter, github, google)
    """
    try:
        site_name = site_name.lower().strip()
        
        sites = {
            'youtube': 'https://youtube.com',
            'facebook': 'https://facebook.com',
            'instagram': 'https://instagram.com',
            'whatsapp': 'https://web.whatsapp.com',
            'discord': 'https://discord.com',
            'twitter': 'https://twitter.com',
            'x': 'https://x.com',
            'github': 'https://github.com',
            'google': 'https://google.com',
            'gmail': 'https://gmail.com',
            'reddit': 'https://reddit.com',
            'linkedin': 'https://linkedin.com',
        }
        
        if site_name in sites:
            webbrowser.open(sites[site_name])
            logging.info(f"Opened {site_name}")
            return f"Opening {site_name}, Boss."
        else:
            # Try to open as URL if it contains a domain
            if '.' in site_name or site_name.startswith('http'):
                url = site_name if site_name.startswith('http') else f'https://{site_name}'
                webbrowser.open(url)
                return f"Opening {url}, Boss."
            else:
                available = ", ".join(sites.keys())
                return f"Unknown site '{site_name}'. Popular sites: {available}"
            
    except Exception as e:
        logging.error(f"Error opening website '{site_name}': {e}")
        return f"Could not open website: {str(e)}"


@function_tool()
async def search_google(
    context: RunContext,  # type: ignore
    query: str
) -> str:
    """
    Open Google search with a specific query in the default browser.
    
    Args:
        query: The search query
    """
    try:
        search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        webbrowser.open(search_url)
        logging.info(f"Searching Google for: {query}")
        return f"Searching Google for '{query}', Boss."
        
    except Exception as e:
        logging.error(f"Error searching Google: {e}")
        return f"Could not perform Google search: {str(e)}"


@function_tool()
async def get_system_status(
    context: RunContext  # type: ignore
) -> str:
    """
    Get current system information including CPU usage, battery status, and memory.
    """
    try:
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Memory info
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        
        # Battery info
        battery = psutil.sensors_battery()
        if battery:
            battery_percent = battery.percent
            plugged = "plugged in" if battery.power_plugged else "on battery"
            battery_info = f"Battery: {battery_percent}% ({plugged})"
        else:
            battery_info = "Battery: Not available (desktop system)"
        
        # Disk usage
        disk = psutil.disk_usage('/')
        disk_percent = disk.percent
        
        status = f"System Status:\n"
        status += f"- CPU Usage: {cpu_percent}%\n"
        status += f"- Memory Usage: {memory_percent}%\n"
        status += f"- Disk Usage: {disk_percent}%\n"
        status += f"- {battery_info}"
        
        logging.info(f"System status retrieved: CPU {cpu_percent}%, Memory {memory_percent}%")
        return status
        
    except Exception as e:
        logging.error(f"Error getting system status: {e}")
        return f"Could not retrieve system status: {str(e)}"


@function_tool()
async def get_schedule(
    context: RunContext,  # type: ignore
    day: Optional[str] = None
) -> str:
    """
    Get the user's schedule for a specific day. If no day is provided, returns today's schedule.
    
    Args:
        day: Day of the week (monday, tuesday, etc.) or "today"
    """
    try:
        # Determine which day to show
        if not day or day.lower() == "today":
            current_day = datetime.datetime.today().weekday()
            day_names = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
            day = day_names[current_day]
        else:
            day = day.lower().strip()
        
        # Schedule data (customize this for the user)
        schedule = {
            "monday": "From 9:00 AM to 9:50 AM you have Algorithm class, from 10:00 AM to 11:50 AM you have DSA class.",
            "tuesday": "From 9:00 AM to 9:50 AM you have Database Management class, from 10:00 AM to 11:50 AM you have Computer Networks class, from 2:00 PM to 4:50 PM you have DSA Lab.",
            "wednesday": "From 9:00 AM to 9:50 AM you have Operating Systems class, from 10:00 AM to 11:50 AM you have Software Engineering class, from 2:00 PM to 4:50 PM you have CN Lab.",
            "thursday": "From 9:00 AM to 9:50 AM you have Database Management class, from 10:00 AM to 11:50 AM you have Algorithm class, from 2:00 PM to 4:50 PM you have DBMS Lab.",
            "friday": "From 9:00 AM to 9:50 AM you have Operating Systems class, from 10:00 AM to 11:50 AM you have Computer Networks class.",
            "saturday": "From 9:00 AM to 9:50 AM you have Software Engineering class, from 10:00 AM to 11:50 AM you have Open Elective or Extra class.",
            "sunday": "You are free today, Boss. Time to relax or revise!"
        }
        
        if day in schedule:
            logging.info(f"Retrieved schedule for {day}")
            return f"Your schedule for {day.title()}: {schedule[day]}"
        else:
            return f"I don't have schedule information for '{day}'."
            
    except Exception as e:
        logging.error(f"Error getting schedule: {e}")
        return f"Could not retrieve schedule: {str(e)}"


@function_tool()
async def get_time_and_date(
    context: RunContext  # type: ignore
) -> str:
    """
    Get the current time, date, and day of the week.
    """
    try:
        now = datetime.datetime.now()
        
        day_name = now.strftime("%A")
        date_str = now.strftime("%B %d, %Y")
        time_str = now.strftime("%I:%M %p")
        
        result = f"Today is {day_name}, {date_str}. The current time is {time_str}."
        logging.info(f"Time and date retrieved: {result}")
        return result
        
    except Exception as e:
        logging.error(f"Error getting time and date: {e}")
        return f"Could not retrieve time and date: {str(e)}"


@function_tool()
async def take_screenshot(
    context: RunContext,  # type: ignore
    filename: Optional[str] = None
) -> str:
    """
    Take a screenshot and save it to the Pictures folder.
    
    Args:
        filename: Optional custom filename (without extension)
    """
    try:
        # Create screenshots directory
        pictures_dir = os.path.join(os.path.expanduser("~"), "Pictures", "Screenshots")
        os.makedirs(pictures_dir, exist_ok=True)
        
        # Generate filename
        if not filename:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}"
        
        filepath = os.path.join(pictures_dir, f"{filename}.png")
        
        # Take screenshot
        screenshot = pyautogui.screenshot()
        screenshot.save(filepath)
        
        logging.info(f"Screenshot saved to {filepath}")
        return f"Screenshot saved to {filepath}, Boss."
        
    except Exception as e:
        logging.error(f"Error taking screenshot: {e}")
        return f"Could not take screenshot: {str(e)}"


# ========================================
# MUSIC & MEDIA CONTROL TOOLS
# ========================================

@function_tool()
async def play_music(
    context: RunContext,  # type: ignore
    query: str,
    platform: str = "youtube"
) -> str:
    """
    Play music from YouTube, Spotify, or search query.
    
    Args:
        query: Song name, artist, or search term
        platform: "youtube", "spotify", or "search" (default: youtube)
    """
    try:
        platform = platform.lower().strip()
        
        if platform == "spotify":
            # Open Spotify with search
            spotify_search = f"spotify:search:{query.replace(' ', '%20')}"
            webbrowser.open(spotify_search)
            logging.info(f"Opening Spotify to play: {query}")
            return f"Opening Spotify to play '{query}', Boss."
            
        elif platform == "youtube":
            # Open YouTube search for music
            youtube_search = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
            webbrowser.open(youtube_search)
            logging.info(f"Opening YouTube to play: {query}")
            return f"Opening YouTube to play '{query}', Boss. Click on the song you want."
            
        else:
            # Default to YouTube
            youtube_search = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}+music"
            webbrowser.open(youtube_search)
            logging.info(f"Searching YouTube for: {query}")
            return f"Searching for '{query}' on YouTube, Boss."
            
    except Exception as e:
        logging.error(f"Error playing music: {e}")
        return f"Could not play music: {str(e)}"


@function_tool()
async def control_media(
    context: RunContext,  # type: ignore
    action: str
) -> str:
    """
    Control media playback (play/pause, next, previous, stop).
    Works with Spotify, YouTube, Windows Media Player, etc.
    
    Args:
        action: "play", "pause", "next", "previous", or "stop"
    """
    try:
        action = action.lower().strip()
        
        if action in ["play", "pause", "playpause"]:
            pyautogui.press("playpause")
            logging.info("Toggled play/pause")
            return "Toggling play/pause, Boss."
            
        elif action in ["next", "skip"]:
            pyautogui.press("nexttrack")
            logging.info("Skipped to next track")
            return "Skipping to next track, Boss."
            
        elif action in ["previous", "back", "prev"]:
            pyautogui.press("prevtrack")
            logging.info("Going to previous track")
            return "Going back to previous track, Boss."
            
        elif action == "stop":
            pyautogui.press("stop")
            logging.info("Stopped media playback")
            return "Stopped playback, Boss."
            
        else:
            return f"Invalid action '{action}'. Use: play, pause, next, previous, or stop."
            
    except Exception as e:
        logging.error(f"Error controlling media: {e}")
        return f"Could not control media: {str(e)}"


@function_tool()
async def close_assistant(
    context: RunContext  # type: ignore
) -> str:
    """
    Close the Nevira assistant and terminate the session.
    Use this when user says goodbye, exit, close, or disconnect.
    """
    try:
        logging.info("User requested to close assistant - initiating shutdown")
        
        # Set flag for graceful shutdown
        context.agent.close_requested = True  # type: ignore
        
        # Schedule immediate termination after response is sent
        import asyncio
        import sys
        
        async def delayed_shutdown():
            await asyncio.sleep(2)  # Give time for response to be sent
            logging.info("Terminating Nevira assistant process...")
            sys.exit(0)
        
        # Start shutdown task
        asyncio.create_task(delayed_shutdown())
        
        return "Goodbye, Boss. Closing assistant now."
        
    except Exception as e:
        logging.error(f"Error closing assistant: {e}")
        # Force exit as backup
        import sys
        sys.exit(0)


@function_tool()
async def force_close_application(
    context: RunContext,  # type: ignore
    app_name: str
) -> str:
    """
    Force close any running application by name.
    More powerful than close_application - works with any app.
    
    Args:
        app_name: Name or partial name of the application process
    """
    try:
        app_name = app_name.lower().strip()
        closed_count = 0
        
        # Find and terminate matching processes
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                process_name = proc.info['name'].lower()
                if app_name in process_name:
                    proc.terminate()
                    closed_count += 1
                    logging.info(f"Terminated process: {proc.info['name']}")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        if closed_count > 0:
            return f"Closed {closed_count} instance(s) of {app_name}, Boss."
        else:
            return f"No running application found matching '{app_name}', Boss."
            
    except Exception as e:
        logging.error(f"Error force closing application: {e}")
        return f"Could not close {app_name}: {str(e)}"


@function_tool()
async def open_youtube_music(
    context: RunContext,  # type: ignore
    query: Optional[str] = None
) -> str:
    """
    Open YouTube Music and optionally search for a song.
    
    Args:
        query: Optional song name or artist to search for
    """
    try:
        if query:
            # Search on YouTube Music
            yt_music_search = f"https://music.youtube.com/search?q={query.replace(' ', '+')}"
            webbrowser.open(yt_music_search)
            logging.info(f"Opening YouTube Music with search: {query}")
            return f"Opening YouTube Music to search for '{query}', Boss."
        else:
            # Just open YouTube Music homepage
            webbrowser.open("https://music.youtube.com/")
            logging.info("Opening YouTube Music")
            return "Opening YouTube Music, Boss."
            
    except Exception as e:
        logging.error(f"Error opening YouTube Music: {e}")
        return f"Could not open YouTube Music: {str(e)}"


@function_tool()
async def open_spotify(
    context: RunContext,  # type: ignore
    query: Optional[str] = None
) -> str:
    """
    Open Spotify desktop app or web player and optionally search for a song.
    
    Args:
        query: Optional song name or artist to search for
    """
    try:
        # Try to open Spotify desktop app first
        if platform.system() == "Windows":
            try:
                # Check if Spotify is installed
                spotify_path = os.path.join(os.environ.get('APPDATA', ''), 
                                          'Spotify', 'Spotify.exe')
                if os.path.exists(spotify_path):
                    if query:
                        # Open Spotify with search
                        search_uri = f"spotify:search:{query.replace(' ', '%20')}"
                        webbrowser.open(search_uri)
                    else:
                        subprocess.Popen([spotify_path])
                    logging.info("Opened Spotify desktop app")
                    return f"Opening Spotify{' to search for ' + query if query else ''}, Boss."
                else:
                    raise FileNotFoundError("Spotify not found")
            except:
                # Fallback to web player
                if query:
                    spotify_url = f"https://open.spotify.com/search/{query.replace(' ', '%20')}"
                else:
                    spotify_url = "https://open.spotify.com/"
                webbrowser.open(spotify_url)
                logging.info("Opened Spotify web player")
                return f"Opening Spotify web player{' to search for ' + query if query else ''}, Boss."
        else:
            # Non-Windows: use web player
            if query:
                spotify_url = f"https://open.spotify.com/search/{query.replace(' ', '%20')}"
            else:
                spotify_url = "https://open.spotify.com/"
            webbrowser.open(spotify_url)
            return f"Opening Spotify{' to search for ' + query if query else ''}, Boss."
            
    except Exception as e:
        logging.error(f"Error opening Spotify: {e}")
        return f"Could not open Spotify: {str(e)}"


@function_tool()
async def close_browser(
    context: RunContext,  # type: ignore
    browser: Optional[str] = None
) -> str:
    """
    Close browser windows (Chrome, Edge, Firefox) or specific YouTube/music tabs.
    
    Args:
        browser: Optional browser name ("chrome", "edge", "firefox") or "all" for all browsers
    """
    try:
        browser_processes = {
            "chrome": ["chrome.exe"],
            "edge": ["msedge.exe"],
            "firefox": ["firefox.exe"],
        }
        
        if browser and browser.lower() in browser_processes:
            # Close specific browser
            for proc_name in browser_processes[browser.lower()]:
                os.system(f'taskkill /f /im {proc_name} 2>nul')
            logging.info(f"Closed {browser}")
            return f"Closed {browser}, Boss."
        else:
            # Close all browsers
            for browser_name, processes in browser_processes.items():
                for proc_name in processes:
                    os.system(f'taskkill /f /im {proc_name} 2>nul')
            logging.info("Closed all browsers")
            return "Closed all browsers, Boss."
            
    except Exception as e:
        logging.error(f"Error closing browser: {e}")
        return f"Could not close browser: {str(e)}"


@function_tool()
async def close_youtube(
    context: RunContext  # type: ignore
) -> str:
    """
    Close the browser (which closes YouTube tabs).
    Since YouTube runs in browser, this closes the active browser window.
    """
    try:
        # Try to close the most common browsers
        closed_any = False
        
        # Try Chrome first (most common)
        result = os.system('taskkill /fi "WINDOWTITLE eq *YouTube*" /im chrome.exe /f 2>nul')
        if result == 0:
            closed_any = True
        else:
            # If specific YouTube window not found, close Chrome entirely
            result = os.system('taskkill /im chrome.exe /f 2>nul')
            if result == 0:
                closed_any = True
        
        # Try Edge
        result = os.system('taskkill /fi "WINDOWTITLE eq *YouTube*" /im msedge.exe /f 2>nul')
        if result == 0:
            closed_any = True
        else:
            result = os.system('taskkill /im msedge.exe /f 2>nul')
            if result == 0:
                closed_any = True
        
        # Try Firefox
        result = os.system('taskkill /fi "WINDOWTITLE eq *YouTube*" /im firefox.exe /f 2>nul')
        if result == 0:
            closed_any = True
        else:
            result = os.system('taskkill /im firefox.exe /f 2>nul')
            if result == 0:
                closed_any = True
        
        if closed_any:
            logging.info("Closed YouTube/browser")
            return "Closed YouTube, Boss."
        else:
            return "No browser windows found to close, Boss."
            
    except Exception as e:
        logging.error(f"Error closing YouTube: {e}")
        return f"Could not close YouTube: {str(e)}"