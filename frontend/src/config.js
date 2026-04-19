// Centralized API Configuration
// Automatically detects the current host or uses the Cloudflare tunnel
const isLocalhost = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
const API_BASE_URL = isLocalhost ? 'http://localhost:8000' : `${window.location.protocol}//${window.location.host}`;

export default API_BASE_URL;
