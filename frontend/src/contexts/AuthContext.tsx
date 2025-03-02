import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { authAPI } from '../api/client';

// Define user type
export interface User {
    id: string;
    email: string;
    displayName: string;
    photoURL?: string;
}

// Define auth context type
interface AuthContextType {
    user: User | null;
    loading: boolean;
    error: string | null;
    login: (email: string, password: string) => Promise<void>;
    register: (email: string, password: string, displayName?: string) => Promise<void>;
    logout: () => Promise<void>;
    clearError: () => void;
}

// Create the context with a default value
const AuthContext = createContext<AuthContextType>({
    user: null,
    loading: false,
    error: null,
    login: async () => { },
    register: async () => { },
    logout: async () => { },
    clearError: () => { },
});

// Provider component
export function AuthProvider({ children }: { children: ReactNode }) {
    const [user, setUser] = useState<User | null>(null);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);

    // Check if user is already logged in
    useEffect(() => {
        const checkAuthStatus = async () => {
            try {
                const token = localStorage.getItem('token');
                if (token) {
                    try {
                        const userData = await authAPI.getCurrentUser();
                        setUser(userData);
                    } catch (error) {
                        // Invalid token or session expired
                        localStorage.removeItem('token');
                    }
                }
            } finally {
                setLoading(false);
            }
        };

        checkAuthStatus();
    }, []);

    const login = async (email: string, password: string) => {
        setLoading(true);
        setError(null);

        try {
            console.log(`Attempting to log in with email: ${email}`);
            const response = await authAPI.login(email, password);

            // Check if the response contains what we expect
            if (!response || !response.token || !response.user) {
                throw new Error('Invalid response from server');
            }

            // Store the token
            localStorage.setItem('token', response.token);

            // Set the user
            setUser(response.user);

            console.log('Login successful!', response.user);
        } catch (error: any) {
            console.error('Login failed:', error);

            // Create a user-friendly error message
            let errorMessage = 'Login failed: ';

            if (error.response) {
                // The request was made and the server responded with a status code
                errorMessage += error.response.data?.message || error.response.statusText || 'Server error';
            } else if (error.request) {
                // The request was made but no response was received
                errorMessage += 'No response from server';
            } else {
                // Something happened in setting up the request
                errorMessage += error.message || 'Unknown error';
            }

            setError(errorMessage);
        } finally {
            setLoading(false);
        }
    };

    const register = async (email: string, password: string, displayName?: string) => {
        setLoading(true);
        setError(null);

        try {
            const response = await authAPI.register(email, password, displayName);

            // Check response
            if (!response || !response.token || !response.user) {
                throw new Error('Invalid response from server');
            }

            // Store token and user
            localStorage.setItem('token', response.token);
            setUser(response.user);
        } catch (error: any) {
            console.error('Registration failed:', error);

            let errorMessage = 'Registration failed: ';

            if (error.response) {
                errorMessage += error.response.data?.message || error.response.statusText || 'Server error';
            } else if (error.request) {
                errorMessage += 'No response from server';
            } else {
                errorMessage += error.message || 'Unknown error';
            }

            setError(errorMessage);
        } finally {
            setLoading(false);
        }
    };

    const logout = async () => {
        setLoading(true);
        setError(null);

        try {
            await authAPI.logout();
        } catch (error) {
            console.error('Logout error:', error);
            // Even if server logout fails, we proceed with local logout
        } finally {
            localStorage.removeItem('token');
            setUser(null);
            setLoading(false);
        }
    };

    const clearError = () => {
        setError(null);
    };

    return (
        <AuthContext.Provider value={{ user, loading, error, login, register, logout, clearError }}>
            {children}
        </AuthContext.Provider>
    );
}

// Custom hook to use the auth context
export function useAuth() {
    return useContext(AuthContext);
}
