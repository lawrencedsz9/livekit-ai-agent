import React, { useState, useEffect, useRef } from 'react';
import { Room, RoomEvent, Track } from 'livekit-client';
import './App.css';

const TOKEN_SERVER = 'http://localhost:3001/token';
const LIVEKIT_URL = 'wss://deskto-ai-zog435cw.livekit.cloud';
const ROOM_NAME = 'nevira-room';

function App() {
  const [room, setRoom] = useState(null);
  const [connected, setConnected] = useState(false);
  const [connecting, setConnecting] = useState(false);
  const [muted, setMuted] = useState(false);
  const [speaking, setSpeaking] = useState(false);
  const [participants, setParticipants] = useState([]);
  const [agentSpeaking, setAgentSpeaking] = useState(false);
  const [error, setError] = useState(null);
  
  const localAudioRef = useRef(null);
  const remoteAudioRef = useRef(null);

  // Get access token from server
  const getToken = async (identity) => {
    try {
      const response = await fetch(TOKEN_SERVER, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ identity, roomName: ROOM_NAME }),
      });
      
      if (!response.ok) {
        throw new Error(`Token request failed: ${response.statusText}`);
      }
      
      const data = await response.json();
      return data.token;
    } catch (err) {
      console.error('Error getting token:', err);
      throw err;
    }
  };

  // Connect to LiveKit room
  const connectToRoom = async () => {
    setConnecting(true);
    setError(null);

    try {
      // Generate unique identity
      const identity = `user_${Math.floor(Math.random() * 10000)}`;
      
      // Get token from server
      const token = await getToken(identity);
      
      // Create room instance
      const newRoom = new Room({
        adaptiveStream: true,
        dynacast: true,
      });

      // Set up event listeners
      setupRoomListeners(newRoom);

      // Connect to room
      await newRoom.connect(LIVEKIT_URL, token);
      
      // Enable microphone
      await newRoom.localParticipant.setMicrophoneEnabled(true);
      
      setRoom(newRoom);
      setConnected(true);
      console.log('✅ Connected to room:', ROOM_NAME);
      
    } catch (err) {
      console.error('Connection error:', err);
      setError(err.message);
    } finally {
      setConnecting(false);
    }
  };

  // Set up room event listeners
  const setupRoomListeners = (room) => {
    // Track subscribed (remote audio from agent)
    room.on(RoomEvent.TrackSubscribed, (track, publication, participant) => {
      console.log('Track subscribed:', track.kind, 'from', participant.identity);
      
      if (track.kind === Track.Kind.Audio) {
        const audioElement = track.attach();
        if (remoteAudioRef.current) {
          remoteAudioRef.current.innerHTML = '';
          remoteAudioRef.current.appendChild(audioElement);
        }
        
        // Detect agent speaking
        if (participant.identity.includes('agent') || participant.identity.includes('nevira')) {
          setAgentSpeaking(true);
          setTimeout(() => setAgentSpeaking(false), 3000);
        }
      }
    });

    // Participant connected
    room.on(RoomEvent.ParticipantConnected, (participant) => {
      console.log('Participant connected:', participant.identity);
      updateParticipants(room);
    });

    // Participant disconnected
    room.on(RoomEvent.ParticipantDisconnected, (participant) => {
      console.log('Participant disconnected:', participant.identity);
      updateParticipants(room);
    });

    // Speaking changed
    room.on(RoomEvent.ActiveSpeakersChanged, (speakers) => {
      const isLocalSpeaking = speakers.some(s => s.isLocal);
      setSpeaking(isLocalSpeaking);
    });

    // Disconnected
    room.on(RoomEvent.Disconnected, () => {
      console.log('Disconnected from room');
      setConnected(false);
      setRoom(null);
    });

    // Connection quality changed
    room.on(RoomEvent.ConnectionQualityChanged, (quality, participant) => {
      console.log('Connection quality:', quality, participant.identity);
    });
  };

  // Update participants list
  const updateParticipants = (room) => {
    const allParticipants = Array.from(room.remoteParticipants.values()).map(p => ({
      identity: p.identity,
      isAgent: p.identity.includes('agent') || p.identity.includes('nevira'),
    }));
    setParticipants(allParticipants);
  };

  // Disconnect from room
  const disconnectFromRoom = async () => {
    if (room) {
      await room.disconnect();
      setRoom(null);
      setConnected(false);
      setParticipants([]);
    }
  };

  // Toggle mute
  const toggleMute = async () => {
    if (room) {
      const newMuted = !muted;
      await room.localParticipant.setMicrophoneEnabled(!newMuted);
      setMuted(newMuted);
    }
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (room) {
        room.disconnect();
      }
    };
  }, [room]);

  return (
    <div className="app">
      <div className="container">
        <header className="header">
          <div className="logo">
            <span className="logo-icon">🎙️</span>
            <h1>Nevira</h1>
          </div>
          <p className="subtitle">AI Voice Assistant</p>
        </header>

        <div className="card">
          {error && (
            <div className="error">
              <span>⚠️</span> {error}
            </div>
          )}

          {!connected ? (
            <div className="connect-section">
              <div className="status-badge offline">Offline</div>
              <p className="description">
                Connect to start talking with Nevira, your AI assistant powered by Google Gemini.
              </p>
              <button 
                className="btn btn-primary btn-large"
                onClick={connectToRoom}
                disabled={connecting}
              >
                {connecting ? (
                  <>
                    <span className="spinner"></span>
                    Connecting...
                  </>
                ) : (
                  <>
                    <span>🔗</span>
                    Connect to Nevira
                  </>
                )}
              </button>
            </div>
          ) : (
            <div className="connected-section">
              <div className="status-badge online">
                <span className="pulse"></span>
                Connected
              </div>

              <div className="voice-indicator">
                {speaking && (
                  <div className="speaking-animation">
                    <div className="wave"></div>
                    <div className="wave"></div>
                    <div className="wave"></div>
                  </div>
                )}
                {agentSpeaking && (
                  <div className="agent-speaking">
                    <span>🤖</span> Nevira is speaking...
                  </div>
                )}
                {!speaking && !agentSpeaking && (
                  <p className="idle-text">Listening... speak to Nevira</p>
                )}
              </div>

              <div className="controls">
                <button 
                  className={`btn ${muted ? 'btn-danger' : 'btn-secondary'}`}
                  onClick={toggleMute}
                >
                  <span>{muted ? '🔇' : '🎤'}</span>
                  {muted ? 'Unmute' : 'Mute'}
                </button>
                
                <button 
                  className="btn btn-danger"
                  onClick={disconnectFromRoom}
                >
                  <span>📞</span>
                  Disconnect
                </button>
              </div>

              {participants.length > 0 && (
                <div className="participants">
                  <h3>Participants</h3>
                  <div className="participant-list">
                    {participants.map((p, i) => (
                      <div key={i} className="participant">
                        <span>{p.isAgent ? '🤖' : '👤'}</span>
                        <span>{p.identity}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        <footer className="footer">
          <p>💡 Make sure the Python agent is running: <code>python agent.py dev</code></p>
          <p>🔧 Token server: <code>{TOKEN_SERVER}</code></p>
        </footer>

        {/* Hidden audio elements for playback */}
        <div style={{ display: 'none' }}>
          <div ref={localAudioRef} id="local-audio"></div>
          <div ref={remoteAudioRef} id="remote-audio"></div>
        </div>
      </div>
    </div>
  );
}

export default App;
