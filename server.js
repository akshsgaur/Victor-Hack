const express = require('express');
const path = require('path');
const app = express();
app.use(express.static('public'));

// Log all requests to see what's happening
app.use((req, res, next) => {
  console.log(`Request for: ${req.url}`);
  next();
});

// Serve static files from the templates directory
app.use(express.static(path.join(__dirname, 'templates')));

// Serve index.html for the root path
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'templates', 'index.html'));
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
  console.log(`Serving files from: ${path.join(__dirname, 'templates')}`);
});