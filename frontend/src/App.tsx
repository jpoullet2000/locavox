import React from 'react';
import { ChakraProvider, theme } from '@chakra-ui/react';
import { AuthProvider } from './contexts/AuthContext';
import ErrorBoundary from './components/ErrorBoundary';
import { router, RouterProvider } from './router';

const App: React.FC = () => {
    console.log("App component rendering");

    // Future flags for React Router v7 compatibility
    const routerFutureFlags = {
        v7_startTransition: true,
        v7_relativeSplatPath: true
    };

    return (
        <ChakraProvider theme={theme}>
            <ErrorBoundary componentName="App">
                <AuthProvider>
                    <RouterProvider router={router} />
                </AuthProvider>
            </ErrorBoundary>
        </ChakraProvider>
    );
};

export default App;
