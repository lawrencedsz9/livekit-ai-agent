/**
 * Nevira Token Server
 * Securely mints LiveKit access tokens for React clients
 */
require('dotenv').config();
const express = require('express');
const cors = require('cors');
const { AccessToken } = require('livekit-server-sdk');

const app = express();

// Middleware
app.use(cors({
  origin: process.env.CORS_ORIGIN || 'http://localhost:5173',
  credentials: true
}));
app.use(express.json());

// Configuration
const LIVEKIT_API_KEY = process.env.LIVEKIT_API_KEY;
const LIVEKIT_API_SECRET = process.env.LIVEKIT_API_SECRET;
const PORT = process.env.PORT || 3001;

// Validate configuration
if (!LIVEKIT_API_KEY || !LIVEKIT_API_SECRET) {
  console.error('❌ ERROR: LIVEKIT_API_KEY and LIVEKIT_API_SECRET must be set in .env');
  process.exit(1);
}

/**
 * POST /token
 * Request body: { identity: string, roomName?: string }
 * Returns: { token: string }
 */
app.post('/token', async (req, res) => {
  try {
    const { identity, roomName } = req.body;

    if (!identity) {
      return res.status(400).json({ error: 'identity is required' });
    }

    const room = roomName || 'nevira-room';

    // Create access token
    const at = new AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET, {
      identity,
      // Token time-to-live (1 hour)
      ttl: '1h',
    });

    // Grant permissions for the room
    at.addGrant({
      room,
      roomJoin: true,
      canPublish: true,
      canSubscribe: true,
      canPublishData: true,
    });

    const token = await at.toJwt();

    console.log(`✅ Token generated for ${identity} in room ${room}`);

    res.json({ token, roomName: room });
  } catch (error) {
    console.error('Error generating token:', error);
    res.status(500).json({ error: 'Failed to generate token' });
  }
});

/**
 * GET /health
 * Health check endpoint
 */
app.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    timestamp: new Date().toISOString(),
    configured: !!(LIVEKIT_API_KEY && LIVEKIT_API_SECRET)
  });
});

// Start server
app.listen(PORT, () => {
  console.log('═══════════════════════════════════════════════');
  console.log('🚀 Nevira Token Server Started');
  console.log('═══════════════════════════════════════════════');
  console.log(`📡 Listening on: http://localhost:${PORT}`);
  console.log(`🔑 API Key configured: ${LIVEKIT_API_KEY ? '✅' : '❌'}`);
  console.log(`🔐 API Secret configured: ${LIVEKIT_API_SECRET ? '✅' : '❌'}`);
  console.log(`🌐 CORS origin: ${process.env.CORS_ORIGIN || 'http://localhost:5173'}`);
  console.log('═══════════════════════════════════════════════');
});
