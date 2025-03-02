/**
 * Global application configuration
 */

// Get environment variables with fallbacks
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080';

// Auth endpoints
export const AUTH_ENDPOINTS = {
    LOGIN: '/login',           // Simple login path (no /auth prefix)
    REGISTER: '/register',     // Simple register path (no /auth prefix)
    LOGOUT: '/logout',         // Simple logout path (no /auth prefix)
    ME: '/me',                 // Simple me path (no /auth prefix)
    // Also provide the full paths as alternatives
    AUTH_LOGIN: '/auth/login',      // Full login path
    AUTH_REGISTER: '/auth/register', // Full register path
    AUTH_LOGOUT: '/auth/logout',     // Full logout path
    AUTH_ME: '/auth/me',            // Full me path
};

// Other API endpoints
export const API_ENDPOINTS = {
    TOPICS: '/topics',
    MESSAGES: '/messages',
    USERS: '/users',
};

// Feature flags from environment
export const FEATURES = {
    NOTIFICATIONS: import.meta.env.VITE_ENABLE_NOTIFICATIONS === 'true',
    GEOLOCATION: import.meta.env.VITE_ENABLE_GEOLOCATION === 'true',
};

// Log level
export const LOG_LEVEL = import.meta.env.VITE_LOG_LEVEL || 'info';

export default {
    API_BASE_URL,
    AUTH_ENDPOINTS,
    API_ENDPOINTS,
    FEATURES,
    LOG_LEVEL,
};
