/**
 * Global application configuration
 */

// Base URLs for API endpoints
export const REAL_API_BASE_URL = 'http://localhost:8000';
export const MOCK_API_BASE_URL = 'http://localhost:8080';

// Default API base URL - updated to use Vite's environment variables
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || REAL_API_BASE_URL;

// Backend API URLs
export const API_ENDPOINTS = {
    REAL_BACKEND: 'http://localhost:8000',
    MOCK_BACKEND: 'http://localhost:8080',
};

// Helper function to attempt API calls with fallback
export async function apiCallWithFallback<T>(
    realApiCall: () => Promise<T>,
    mockApiCall: () => Promise<T>
): Promise<T> {
    try {
        return await realApiCall();
    } catch (primaryError) {
        console.error('Error calling real API:', primaryError);
        try {
            console.log('Falling back to mock API...');
            return await mockApiCall();
        } catch (fallbackError) {
            console.error('Error calling mock API:', fallbackError);
            throw primaryError;
        }
    }
}

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

// Topic API endpoints
export const TOPIC_ENDPOINTS = {
    GET_ALL: '/topics',
    GET_BY_ID: (id: string) => `/topics/${id}`,
    CREATE: '/topics',
    UPDATE: (id: string) => `/topics/${id}`,
    DELETE: (id: string) => `/topics/${id}`,
};

// Other API endpoints - renamed to avoid duplicate declaration
export const OTHER_API_ENDPOINTS = {
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

// Log all environment variables in development mode for debugging
if (import.meta.env.DEV) {
    console.log('Environment variables:', {
        NODE_ENV: import.meta.env.MODE,
        BASE_URL: import.meta.env.BASE_URL,
        API_BASE_URL,
        FEATURES,
        LOG_LEVEL,
    });
}

export default {
    API_BASE_URL,
    REAL_API_BASE_URL,
    MOCK_API_BASE_URL,
    AUTH_ENDPOINTS,
    TOPIC_ENDPOINTS,
    OTHER_API_ENDPOINTS,
    FEATURES,
    LOG_LEVEL,
};
