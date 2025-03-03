import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { getErrorMessage } from '../api/apiUtils';

// Define the user type
interface User {
    id: string;
    username: string;
    email?: string;
    // Add other user properties as needed
}

// Define the context type
interface AuthContextType {
    user: User | null;
    loading: boolean;
    error: string | null;
    login: (username: string, password: string) => Promise<void>;
    logout: () => void;
    isAuthenticated: boolean;
}

// Create the context with a default value
const AuthContext = createContext<AuthContextType>({
    user: null,
    loading: true,
    error: null,
    login: async () => { },
    logout: () => { },
    isAuthenticated: false,
});

// Custom hook to use the auth context
export const useAuth = () => useContext(AuthContext);

interface AuthProviderProps {
    children: ReactNode;
}

// AuthProvider component
export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
    const [user, setUser] = useState<User | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    // Check if the user is already authenticated on mount
    useEffect(() => {
        const checkAuth = async () => {
            try {
                // Check for stored user data in localStorage
                const storedUser = localStorage.getItem('user');
                const storedToken = localStorage.getItem('token');

                if (storedUser && storedToken) {
                    setUser(JSON.parse(storedUser));
                    console.log('User restored from local storage');
                }
            } catch (err) {
                console.error('Auth initialization error:', err);
                setError('Failed to restore authentication state');
            } finally {
                // Always set loading to false when done
                setLoading(false);
            }
        };

        // Set a timeout to ensure we don't block indefinitely
        const timeoutId = setTimeout(() => {
            if (loading) {
                console.warn('Auth initialization timeout exceeded');
                setLoading(false);
                setError('Authentication check timed out');
            }
        }, 3000);

        checkAuth();

        return () => clearTimeout(timeoutId);
    }, []);

    // Login function
    const login = async (username: string, password: string) => {
        setLoading(true);
        setError(null);

        try {
            // For demo, we'll just simulate a login
            // In a real app, you would call your login API
            await new Promise(resolve => setTimeout(resolve, 500));

            // Create a mock user
            const newUser = {
                id: `user-${username}`,
                username,
                email: `${username}@example.com`,
            };

            // Store the user in state and localStorage
            setUser(newUser);
            localStorage.setItem('user', JSON.stringify(newUser));
            localStorage.setItem('token', 'mock-jwt-token');

            console.log('User logged in:', newUser);
        } catch (err) {
            console.error('Login error:', err);
            const errorMsg = getErrorMessage(err, 'Login failed. Please try again.');
            setError(errorMsg);
            throw new Error(errorMsg);
        } finally {
            setLoading(false);
        }
    };

    // Logout function
    const logout = () => {
        setUser(null);
        localStorage.removeItem('user');
        localStorage.removeItem('token');
        console.log('User logged out');
    };

    // Provide the auth context
    return (
        <AuthContext.Provider
            value={{
                user,
                loading,
                error,
                login,
                logout,
                isAuthenticated: !!user,
            }}
        >
            {children}
        </AuthContext.Provider>
    );
};
