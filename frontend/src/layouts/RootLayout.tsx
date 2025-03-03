import React from 'react';
import { Box, Flex, useColorModeValue } from '@chakra-ui/react';
import { Outlet } from 'react-router-dom';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import { useAuth } from '../contexts/AuthContext';

const RootLayout: React.FC = () => {
    const { loading } = useAuth();
    const bgColor = useColorModeValue('gray.50', 'gray.900');

    // Add logging to debug when RootLayout renders and when Outlet is rendered
    console.log('RootLayout rendering');

    return (
        <Flex
            direction="column"
            minHeight="100vh"
            bg={bgColor}
        >
            <Navbar />

            <Box
                flex="1"
                as="main"
                py={4}
                onLoad={() => console.log('Main content area loaded')}
            >
                {/* This debug div will help identify if the layout renders but the outlet doesn't */}
                <div style={{ display: 'none' }} id="root-layout-debug">
                    RootLayout rendered successfully
                </div>
                {loading ? (
                    <Box textAlign="center" py={10}>
                        Loading content...
                    </Box>
                ) : (
                    <Outlet />
                )}
            </Box>

            <Footer />
        </Flex>
    );
};

export default RootLayout;
