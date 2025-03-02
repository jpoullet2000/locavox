import React from 'react';
import { Box } from '@chakra-ui/react';
import Nav from './Nav';
import Footer from './Footer';
import ErrorBoundary from './ErrorBoundary';
import { Outlet } from 'react-router-dom';

const Layout: React.FC = () => {
    return (
        <Box display="flex" flexDirection="column" minHeight="100vh">
            <ErrorBoundary componentName="Nav">
                <Nav />
            </ErrorBoundary>

            <Box flexGrow={1} py={4} px={4}>
                <Outlet />
            </Box>

            <ErrorBoundary componentName="Footer">
                <Footer />
            </ErrorBoundary>
        </Box>
    );
};

export default Layout;
