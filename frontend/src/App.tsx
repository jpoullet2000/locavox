import React, { useState, useEffect } from 'react';
import { ChakraProvider, Box, Text, Spinner, VStack, useToast, Button } from '@chakra-ui/react';
import { Routes, Route } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import HomePage from './pages/HomePage';
import TopicsPage from './pages/TopicsPage';
import RootLayout from './layouts/RootLayout';
import ErrorPage from './pages/ErrorPage';
import theme from './theme';
import ErrorBoundary from './components/ErrorBoundary';

const App: React.FC = () => {
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const toast = useToast();

    // Add a simple initialization check with timeout
    useEffect(() => {
        let timer: NodeJS.Timeout;

        const initApp = async () => {
            try {
                // Simulate any initialization logic here, like checking auth status
                // Replace with actual initialization logic as needed
                console.log('App is initializing...');

                // For demo, we'll just wait a short amount of time
                await new Promise(resolve => setTimeout(resolve, 500));

                setLoading(false);
            } catch (err) {
                console.error('App initialization error:', err);
                setError('Failed to load application. Please refresh the page or check your connection.');
                setLoading(false);

                toast({
                    title: 'Application Error',
                    description: 'There was a problem loading the application.',
                    status: 'error',
                    duration: 5000,
                    isClosable: true,
                });
            }
        };

        // Start initialization
        initApp();

        // Set a timeout to prevent indefinite loading
        timer = setTimeout(() => {
            if (loading) {
                console.warn('App initialization timeout exceeded');
                setLoading(false);
                setError('Application took too long to load. Please check your network connection.');

                toast({
                    title: 'Loading Timeout',
                    description: 'Application took too long to load. This might indicate a network issue.',
                    status: 'warning',
                    duration: 5000,
                    isClosable: true,
                });
            }
        }, 10000); // 10 second timeout

        return () => {
            clearTimeout(timer);
        };
    }, []);

    if (loading) {
        return (
            <ChakraProvider theme={theme}>
                <Box height="100vh" display="flex" alignItems="center" justifyContent="center">
                    <VStack spacing={4}>
                        <Spinner size="xl" color="blue.500" thickness="4px" speed="0.65s" />
                        <Text fontSize="xl">Loading LocaVox...</Text>
                        <Text fontSize="sm" color="gray.500">Please wait while we set things up</Text>
                    </VStack>
                </Box>
            </ChakraProvider>
        );
    }

    if (error) {
        return (
            <ChakraProvider theme={theme}>
                <Box height="100vh" display="flex" alignItems="center" justifyContent="center" p={4}>
                    <VStack spacing={4} textAlign="center" maxW="500px">
                        <Text fontSize="xl" color="red.500">Application Error</Text>
                        <Text>{error}</Text>
                        <Text fontSize="sm" color="gray.500">
                            Try refreshing the page. If the problem persists, please contact support.
                        </Text>
                        <Button colorScheme="blue" onClick={() => window.location.reload()}>
                            Refresh Page
                        </Button>
                    </VStack>
                </Box>
            </ChakraProvider>
        );
    }

    return (
        <ChakraProvider theme={theme}>
            <ErrorBoundary>
                <AuthProvider>
                    <Routes>
                        <Route element={<RootLayout />}>
                            <Route path="/" element={<HomePage />} />
                            <Route path="/topics" element={<TopicsPage />} />
                            <Route path="*" element={<ErrorPage />} />
                        </Route>
                    </Routes>
                </AuthProvider>
            </ErrorBoundary>
        </ChakraProvider>
    );
};

export default App;
