/**
 * API client for making requests to the backend
 */
import axios from 'axios';

// Get the API base URL from environment variable or use the default
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080';

// Create an Axios instance with default config
const apiClient = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request interceptor to add auth token to requests
apiClient.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

// Response interceptor to handle common errors
apiClient.interceptors.response.use(
    (response) => response,
    (error) => {
        console.error('API Error:', error.response?.data || error.message);

        // Add specific error handling for auth-related errors
        if (error.response?.status === 401) {
            // Unauthorized - could clear token or redirect to login
            console.log('Authentication error - you may need to log in again');
            // localStorage.removeItem('token'); // Uncomment to auto-logout on auth errors
        }

        return Promise.reject(error);
    }
);

// Auth API functions
export const authAPI = {
    login: async (email: string, password: string) => {
        try {
            console.log(`Attempting login with ${email} to ${API_BASE_URL}/login`);
            const response = await apiClient.post('/login', { email, password });
            return response.data;
        } catch (error) {
            console.error('Login error:', error);
            throw error;
        }
    },

    register: async (email: string, password: string, displayName?: string) => {
        try {
            const response = await apiClient.post('/register', {
                email,
                password,
                displayName
            });
            return response.data;
        } catch (error) {
            console.error('Registration error:', error);
            throw error;
        }
    },

    logout: async () => {
        try {
            const response = await apiClient.post('/logout');
            return response.data;
        } catch (error) {
            console.error('Logout error:', error);
            // Even if logout fails on the server, we can still clear local state
            localStorage.removeItem('token');
            throw error;
        }
    },

    getCurrentUser: async () => {
        try {
            const response = await apiClient.get('/me');
            return response.data;
        } catch (error) {
            console.error('Get current user error:', error);
            throw error;
        }
    }
};

// Export the base client for other API needs
export default apiClient;
