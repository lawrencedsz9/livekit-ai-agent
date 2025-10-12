# 🎵 Nevira Enhanced Features Guide

## New Capabilities Added

### 1. 🎵 Music & Media Control
Play and control music from multiple platforms with voice commands.

### 2. 🚪 Smart Exit & Disconnect
Automatically close the assistant when you disconnect or say goodbye.

### 3. 💪 Enhanced Application Control
Better app closing with force termination support.

---

## 🎵 Music Features

### Play Music (Multiple Platforms)

**YouTube (Default)**
```
You: "Play some music"
You: "Play Bohemian Rhapsody"
You: "Play songs by Taylor Swift"
```

**Spotify**
```
You: "Play music on Spotify"
You: "Play Billie Eilish on Spotify"
You: "Open Spotify and play jazz"
```

**YouTube Music**
```
You: "Open YouTube Music"
You: "Play rock music on YouTube Music"
```

### Control Playback

**Play/Pause**
```
You: "Pause the music"
You: "Resume playing"
You: "Play"
```

**Skip Tracks**
```
You: "Next song"
You: "Skip this"
You: "Previous track"
You: "Go back"
```

**Stop**
```
You: "Stop the music"
```

---

## 🚪 Exit & Disconnect Features

### Voice-Controlled Exit

Say any of these to close Nevira:
```
You: "Goodbye"
You: "Bye"
You: "Exit"
You: "Close"
You: "Disconnect"
You: "Close the assistant"
```

Nevira will:
1. Say goodbye
2. Close the session
3. Terminate the program

### Auto-Disconnect (React UI)

When using the web interface:
- Click "Disconnect" button → closes cleanly
- Close browser tab → LiveKit handles cleanup
- Lost connection → automatic reconnection attempt

---

## 💪 Enhanced Application Control

### Close Applications

**Basic Close (Specific Apps)**
```
You: "Close Calculator"
You: "Close Notepad"
You: "Close Chrome"
```

**Force Close (Any App)**
```
You: "Force close Spotify"
You: "Force close all Chrome windows"
You: "Kill the Python process"
```

The `force_close_application` can close any running program by name!

---

## 🎯 Complete Command List

### Music Commands

| Command | Action |
|---------|--------|
| "Play [song/artist]" | Play on YouTube |
| "Play [song] on Spotify" | Play on Spotify |
| "Open YouTube Music" | Open YT Music app |
| "Open Spotify" | Open Spotify app |
| "Pause" / "Play" | Toggle playback |
| "Next" / "Skip" | Next track |
| "Previous" / "Back" | Previous track |
| "Stop" | Stop playback |

### Exit Commands

| Command | Action |
|---------|--------|
| "Goodbye" / "Bye" | Close assistant |
| "Exit" / "Close" | Close assistant |
| "Disconnect" | Close assistant |

### App Control

| Command | Action |
|---------|--------|
| "Close [app]" | Close specific app |
| "Force close [app]" | Force terminate app |
| "Open [app]" | Open application |

---

## 📋 Usage Examples

### Example 1: Music Session
```
You: "Hello Nevira"
Nevira: "Hello! How may I assist you today?"

You: "Play some chill music"
Nevira: "Opening YouTube to play 'chill music', Boss. Click on the song you want."
[Browser opens with search results]

You: "Pause the music"
Nevira: "Toggling play/pause, Boss."
[Music pauses]

You: "Next song"
Nevira: "Skipping to next track, Boss."
[Skips to next]

You: "That's enough, goodbye"
Nevira: "Goodbye, Boss. Closing assistant now."
[Assistant closes]
```

### Example 2: App Management
```
You: "Open Calculator"
Nevira: "Opening calculator now, Boss."
[Calculator opens]

You: "What's 2 plus 2?"
[Do your calculation]

You: "Close Calculator"
Nevira: "Closed calculator, Boss."
[Calculator closes]
```

### Example 3: Spotify Session
```
You: "Open Spotify"
Nevira: "Opening Spotify, Boss."
[Spotify app or web player opens]

You: "Play Imagine Dragons"
[Navigate to artist in Spotify]

You: "Turn up the volume"
Nevira: "Volume increased, Boss."

You: "Pause"
Nevira: "Toggling play/pause, Boss."
```

---

## 🔧 Technical Details

### Music Platforms

**YouTube**
- Opens YouTube search with query
- User clicks desired song
- Works with any music video

**Spotify**
- Tries desktop app first (if installed)
- Falls back to web player
- Opens search results automatically

**YouTube Music**
- Opens YouTube Music web player
- Searches for requested content
- Premium features available with subscription

### Media Controls

Uses Windows media keys:
- `playpause` - Play/Pause toggle
- `nexttrack` - Skip forward
- `prevtrack` - Skip backward
- `stop` - Stop playback

Works with:
- Spotify
- YouTube (when focused)
- Windows Media Player
- VLC
- Most media players

### Close Mechanisms

**close_assistant()**
- Sets `close_requested` flag
- Agent sees flag and terminates
- Clean exit with goodbye message

**force_close_application()**
- Searches all running processes
- Matches by name (partial match)
- Terminates all matching processes
- More powerful than `close_application()`

---

## 🎨 Customization

### Add Local Music Player

Edit `tools.py`:

```python
@function_tool()
async def play_local_music(
    context: RunContext,
    query: str
) -> str:
    """Play music from local library using VLC or Windows Media Player"""
    try:
        # Open your preferred player
        music_folder = os.path.join(os.path.expanduser("~"), "Music")
        os.startfile(music_folder)
        return f"Opening local music library, Boss."
    except Exception as e:
        return f"Could not open music library: {str(e)}"
```

### Add Custom Streaming Service

```python
@function_tool()
async def open_apple_music(
    context: RunContext,
    query: Optional[str] = None
) -> str:
    """Open Apple Music"""
    try:
        if query:
            url = f"https://music.apple.com/search?term={query.replace(' ', '+')}"
        else:
            url = "https://music.apple.com/"
        webbrowser.open(url)
        return f"Opening Apple Music, Boss."
    except Exception as e:
        return f"Could not open Apple Music: {str(e)}"
```

---

## 🐛 Troubleshooting

### Music won't play

**Problem:** YouTube/Spotify opens but no music plays

**Solution:**
- The tool opens the platform and searches
- You need to click the first result to play
- Or ask: "Play [exact song name]" for better results

### Media controls don't work

**Problem:** Play/pause doesn't affect music

**Solution:**
- Make sure the music player has focus (is the active window)
- Try clicking on the player window first
- Some web players need to be the active tab

### Can't close assistant

**Problem:** Saying "goodbye" doesn't close it

**Solution:**
- Make sure you say exact keywords: "goodbye", "bye", "exit", "close"
- Check agent logs for errors
- Use Ctrl+C in terminal as backup

### Force close doesn't work

**Problem:** App still running after force close

**Solution:**
- Check exact app name with Task Manager
- Try more specific name: "chrome" not "google chrome"
- Some system apps may be protected
- Use full process name if needed

---

## 💡 Tips & Best Practices

### Music

1. **Be Specific**: "Play Bohemian Rhapsody by Queen" works better than "play music"
2. **Choose Platform**: Specify "on Spotify" or "on YouTube" for better results
3. **Use Controls**: Use "pause", "next", "back" for quick control without touching keyboard

### Exit

1. **Clean Exit**: Always say "goodbye" rather than force-killing terminal
2. **Save Work**: Close important apps before exiting assistant
3. **React UI**: Use "Disconnect" button for web interface

### App Control

1. **Specific Names**: Use exact app names: "calculator", "notepad"
2. **Force Close**: Use for stubborn apps that won't close normally
3. **Check First**: Ask "what apps are running" before closing

---

## 🆕 What's New

### Version 2.0 (Oct 12, 2025)

**Music & Media**
✅ Multi-platform music playback (YouTube, Spotify, YouTube Music)
✅ Full media controls (play/pause/next/previous/stop)
✅ Platform-specific search and playback
✅ Automatic fallback to web players

**Assistant Control**
✅ Voice-controlled exit ("goodbye", "close", etc.)
✅ Clean shutdown with goodbye message
✅ Auto-disconnect handling
✅ Session cleanup on exit

**Enhanced App Control**
✅ Force close any application by name
✅ Partial name matching for processes
✅ Multiple instance termination
✅ Better error handling

---

## 📚 Related Documentation

- `README.md` - Main project documentation
- `tools.py` - All function implementations
- `prompts.py` - Agent instructions and personality
- `agent.py` - Core agent logic

---

## 🎉 Quick Start

1. **Start Nevira**
   ```powershell
   python agent.py console
   ```

2. **Try Music**
   ```
   You: "Play some music"
   ```

3. **Control Playback**
   ```
   You: "Pause"
   You: "Next"
   ```

4. **Exit**
   ```
   You: "Goodbye"
   ```

---

**Enjoy your enhanced Nevira assistant! 🎵🤖**
