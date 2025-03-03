import axios, { AxiosRequestConfig } from 'axios';

// API endpoint configurations
export const API_ENDPOINTS = {
    REAL_BACKEND: 'http://localhost:8000',
    MOCK_BACKEND: 'http://localhost:8080',
};

/**
 * Makes an API call to the real backend first, then falls back to the mock backend if needed
 * 
 * @param path - The API path (without the base URL)
 * @param method - The HTTP method (get, post, delete, etc.)
 * @param config - Optional axios config
 * @param data - Optional request body data
 * @returns Promise with the response data
 */
export async function callApiWithFallback<T = any>(
    path: string,
    method: 'get' | 'post' | 'put' | 'delete' | 'patch',
    config?: AxiosRequestConfig,
    data?: any
): Promise<T> {
    try {
        // Try the real backend first
        console.log(`Calling real backend: ${method.toUpperCase()} ${API_ENDPOINTS.REAL_BACKEND}${path}`);
        const realResponse = await axios({
            method,
            url: `${API_ENDPOINTS.REAL_BACKEND}${path}`,
            data,
            ...config
        });
        return realResponse.data;
    } catch (primaryError) {
        console.error(`Error calling real backend (${method.toUpperCase()} ${path}):`, primaryError);

        try {
            // Fall back to mock API if real backend fails
            console.log(`Falling back to mock API: ${method.toUpperCase()} ${API_ENDPOINTS.MOCK_BACKEND}${path}`);
            const mockResponse = await axios({
                method,
                url: `${API_ENDPOINTS.MOCK_BACKEND}${path}`,
                data,
                ...config
            });
            return mockResponse.data;
        } catch (fallbackError) {
            console.error(`Error calling mock API (${method.toUpperCase()} ${path}):`, fallbackError);
            // If both fail, throw the original error
            throw primaryError;
        }
    }
}

/**
 * Helper function to get auth headers for authenticated requests
 */
export function getAuthHeaders() {
    const token = localStorage.getItem('token');
    return token ? { Authorization: `Bearer ${token}` } : {};
}

/**
 * Handle API errors in a consistent way
 * 
 * @param error - The error from axios
 * @param fallbackMessage - Default message to show if error doesn't have a message
 * @returns A user-friendly error message
 */
export function getErrorMessage(error: any, fallbackMessage = 'An error occurred'): string {
    if (error.response) {
        // The request was made and the server responded with a status code outside of 2xx
        const serverMessage = error.response.data?.detail || error.response.data?.message;
        if (serverMessage) return serverMessage;

        // Standard messages for common status codes
        switch (error.response.status) {
            case 400: return 'Invalid request';
            case 401: return 'You need to log in';
            case 403: return 'You do not have permission to perform this action';
            case 404: return 'The requested resource was not found';
            case 429: return 'Too many requests. Please try again later';
            case 500: return 'Server error. Please try again later';
            default: return `Error ${error.response.status}: ${error.response.statusText}`;
        }
    } else if (error.request) {
        // The request was made but no response was received
        return 'No response from server. Please check your connection';
    } else {
        // Something happened in setting up the request
        return error.message || fallbackMessage;
    }
}

/**
 * Format a date for display
 */
export function formatDate(dateString: string): string {
    try {
        return new Date(dateString).toLocaleString();
    } catch (e) {
        return dateString;
    }
}

/**
 * Truncate text if it's longer than the specified length
 */
export function truncateText(text: string, maxLength: number = 100): string {
    if (text.length <= maxLength) return text;
    return `${text.substring(0, maxLength - 3)}...`;
}
