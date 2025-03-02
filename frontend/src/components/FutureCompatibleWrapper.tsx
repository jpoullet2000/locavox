import React, { useEffect } from 'react';

// This component logs a message to help identify if this file is being processed
console.log('Loading FutureCompatibleWrapper component');

interface FutureCompatibleWrapperProps {
    children: React.ReactNode;
}

/**
 * This component is a wrapper for any component that needs to be compatible with React Router's future flags.
 * It ensures that state updates are wrapped properly with startTransition when needed.
 */
const FutureCompatibleWrapper: React.FC<FutureCompatibleWrapperProps> = ({ children }) => {
    // Log that this component is being rendered
    useEffect(() => {
        console.log('FutureCompatibleWrapper mounted');
    }, []);

    // Simply render the children - the component exists just to provide a convenient break point
    // for adding potential logic in the future
    return <>{children}</>;
};

export default FutureCompatibleWrapper;
