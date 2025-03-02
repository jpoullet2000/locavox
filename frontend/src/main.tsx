import React, { startTransition } from 'react';
import ReactDOM from 'react-dom/client';
import { ChakraProvider, theme } from '@chakra-ui/react';
import { RouterProvider } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import ErrorBoundary from './components/ErrorBoundary';
import { router } from './router';
import './index.css';

// For troubleshooting: Add a console log to verify main.tsx is executing
console.log('LocaVox app starting...');

// Get the root element
const rootElement = document.getElementById('root');

// Only attempt to render if the root element exists
if (rootElement) {
    // Remove the loading indicator once React takes over
    const loadingIndicator = document.getElementById('loading-indicator');
    if (loadingIndicator) {
        loadingIndicator.style.display = 'none';
    }

    // Create root and render the app
    const root = ReactDOM.createRoot(rootElement);

    // Use startTransition for initial render to be compatible with React Router v7
    startTransition(() => {
        root.render(
            <React.StrictMode>
                <ChakraProvider theme={theme}>
                    <ErrorBoundary componentName="App">
                        <AuthProvider>
                            <RouterProvider
                                router={router}
                                future={{
                                    v7_startTransition: true
                                }}
                            />
                        </AuthProvider>
                    </ErrorBoundary>
                </ChakraProvider>
            </React.StrictMode>
        );
    });

    // Add a success message in console
    console.log('LocaVox app rendered successfully!');
} else {
    // Log error if root element is missing
    console.error('Could not find root element to mount React app!');
}
