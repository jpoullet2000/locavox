import React, { useEffect } from 'react';
import { useLocation } from 'react-router-dom';

/**
 * A component to help debug routing issues with the Topics page
 */
const TopicRouteDebug: React.FC = () => {
    const location = useLocation();

    useEffect(() => {
        console.log('TopicRouteDebug: Current location', {
            pathname: location.pathname,
            search: location.search,
            hash: location.hash,
            state: location.state,
        });

        // Log React Router DOM version
        try {
            // @ts-ignore - This is for debugging only
            const version = window.ReactRouterVersion || 'unknown';
            console.log('React Router DOM version:', version);
        } catch (e) {
            console.log('Could not determine React Router version');
        }
    }, [location]);

    return null; // This component doesn't render anything
};

export default TopicRouteDebug;
