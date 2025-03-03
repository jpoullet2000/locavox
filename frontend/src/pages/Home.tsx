import React from 'react';
import { Box, Button, Container, Heading, Text, VStack, Flex, useColorModeValue } from '@chakra-ui/react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const Home: React.FC = () => {
    const { isAuthenticated, user } = useAuth();
    const bgColor = useColorModeValue('blue.50', 'blue.900');
    const cardBg = useColorModeValue('white', 'gray.700');

    return (
        <Container maxW="container.xl" py={10}>
            <VStack spacing={8} align="stretch">
                <Box
                    bg={bgColor}
                    p={8}
                    borderRadius="lg"
                    textAlign="center"
                >
                    <Heading as="h1" size="2xl" mb={4}>
                        Welcome to LocaVox
                    </Heading>
                    <Text fontSize="xl" mb={6}>
                        Connect with your local community through meaningful conversations
                    </Text>

                    {isAuthenticated ? (
                        <Button as={Link} to="/dashboard" size="lg" colorScheme="blue">
                            Go to Dashboard
                        </Button>
                    ) : (
                        <Flex gap={4} justifyContent="center">
                            <Button as={Link} to="/login" size="lg" colorScheme="blue">
                                Sign In
                            </Button>
                            <Button as={Link} to="/register" size="lg" variant="outline" colorScheme="blue">
                                Register
                            </Button>
                        </Flex>
                    )}
                </Box>

                <Heading as="h2" size="lg" textAlign="center" mt={8}>
                    How LocaVox Works
                </Heading>

                <Flex
                    direction={{ base: 'column', md: 'row' }}
                    gap={6}
                >
                    {[
                        {
                            title: 'Post Messages',
                            description: 'Share your thoughts, questions, or offers with your local community',
                            link: '/post-message'
                        },
                        {
                            title: 'Browse Topics',
                            description: 'Explore different community topics and join the conversation',
                            link: '/topics'
                        },
                        {
                            title: 'Connect',
                            description: 'Meet neighbors and build meaningful connections',
                            link: '/dashboard'
                        },
                    ].map((feature, index) => (
                        <Box
                            key={index}
                            bg={cardBg}
                            p={6}
                            borderRadius="md"
                            flex="1"
                            boxShadow="md"
                        >
                            <Heading as="h3" size="md" mb={2}>
                                {feature.title}
                            </Heading>
                            <Text mb={4}>{feature.description}</Text>
                            <Button
                                as={Link}
                                to={isAuthenticated ? feature.link : '/login'}
                                colorScheme="blue"
                                variant="outline"
                                size="sm"
                            >
                                {isAuthenticated ? 'Get Started' : 'Sign In to Continue'}
                            </Button>
                        </Box>
                    ))}
                </Flex>
            </VStack>
        </Container>
    );
};

export default Home;
