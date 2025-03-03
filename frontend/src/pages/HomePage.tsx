import React from 'react';
import { Link as RouterLink } from 'react-router-dom';
// ...other imports...

const HomePage: React.FC = () => {
    // Add logging to track when this component renders
    console.log('HomePage rendering');

    return (
        <Container maxW="container.xl">
            {/* ...existing code... */}

            {/* Update the Get Started button to ensure it works */}
            <Button
                as={RouterLink}
                to="/topics"
                colorScheme="teal"
                size="lg"
                mt={6}
                onClick={() => console.log('Get Started button clicked, navigating to /topics')}
            >
                Browse Topics
            </Button>

            {/* Alternative button using navigate for testing */}
            <Button
                colorScheme="blue"
                size="lg"
                mt={6}
                ml={4}
                onClick={() => {
                    console.log('Direct navigate button clicked');
                    window.location.href = '/topics';
                }}
            >
                Topics (Direct)
            </Button>

            {/* ...existing code... */}
        </Container>
    );
};

export default HomePage;
