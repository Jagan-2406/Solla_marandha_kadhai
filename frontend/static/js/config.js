// frontend/static/js/config.js

// Determine the API base URL depending on the environment
const API_BASE_URL = (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')
    ? 'http://127.0.0.1:5000'
    : 'https://solla-marandha-kadhai.onrender.com';
