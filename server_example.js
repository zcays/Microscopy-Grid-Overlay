// Simple Node.js Express server to handle connections from Roblox Studio
const express = require('express');
const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.json());

// Middleware for simple API Key authentication
const API_KEY = process.env.API_KEY || "YOUR_SECRET_API_KEY";
function authenticate(req, res, next) {
  const authHeader = req.headers['authorization'];
  if (authHeader === `Bearer ${API_KEY}`) {
    next();
  } else {
    res.status(401).json({ error: "Unauthorized" });
  }
}

// Endpoint to test connection from Roblox Studio
app.get('/api/health', (req, res) => {
  res.json({ status: "online", time: new Date().toISOString() });
});

// Endpoint to receive data/events from Roblox Studio
app.post('/api/server-status', authenticate, (req, res) => {
  console.log("Received data from Roblox Studio:", req.body);
  res.json({ success: true, message: "Data received successfully" });
});

app.listen(PORT, () => {
  console.log(`Roblox API Server listening on port ${PORT}`);
});
