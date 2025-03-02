import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Center, Spinner, Text, VStack } from '@chakra-ui/react';

interface ProtectedRouteProps {
    children: React.ReactNode;
    redirectTo?: string;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
    children,
    redirectTo = '/login'
}) => {
    const { user, isLoading } = useAuth();
    const location = useLocation();

    // Show loading spinner while checking authentication
    if (isLoading) {
        return (
            <Center h="100vh">
                <VStack spacing={4}>
                    <Spinner size="xl" />
                    <Text>Checking authentication...</Text>
                </VStack>
            </Center>
        );
    }

    // Redirect to login if not authenticated
    if (!user) {
        return <Navigate to={redirectTo} state={{ from: location }} replace />;
    }

    // Render children if authenticated
    return <>{children}</>;
};

export default ProtectedRoute;
