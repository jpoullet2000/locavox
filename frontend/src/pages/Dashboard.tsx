import React, { useState, useEffect } from 'react';
import {
    Box,
    Container,
    Heading,
    SimpleGrid,
    Text,
    VStack,
    HStack,
    Stat,
    StatLabel,
    StatNumber,
    StatHelpText,
    Button,
    useColorModeValue,
    Spinner,
} from '@chakra-ui/react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const Dashboard: React.FC = () => {
    const { user } = useAuth();
    const [loading, setLoading] = useState(true);
    const [stats, setStats] = useState({
        totalMessages: 0,
        activeTopics: 0,
        latestActivity: null
    });

    const cardBg = useColorModeValue('white', 'gray.700');
    const borderColor = useColorModeValue('gray.200', 'gray.600');

    useEffect(() => {
        // Simulating data loading
        const loadDashboardData = async () => {
            try {
                // In a real app, you'd fetch this data from your API
                await new Promise(resolve => setTimeout(resolve, 800));

                setStats({
                    totalMessages: 42,
                    activeTopics: 5,
                    latestActivity: new Date().toISOString()
                });
            } catch (error) {
                console.error('Failed to load dashboard data:', error);
            } finally {
                setLoading(false);
            }
        };

        loadDashboardData();
    }, []);

    if (loading) {
        return (
            <Container centerContent py={10}>
                <Spinner size="xl" />
                <Text mt={4}>Loading dashboard data...</Text>
            </Container>
        );
    }

    return (
        <Container maxW="container.lg" py={8}>
            <VStack spacing={8} align="stretch">
                <Box textAlign="center" mb={4}>
                    <Heading as="h1" size="xl">Welcome, {user?.username || 'User'}!</Heading>
                    <Text mt={2} color="gray.500">Here's what's happening in your community</Text>
                </Box>

                {/* Stats Cards */}
                <SimpleGrid columns={{ base: 1, md: 3 }} spacing={6}>
                    <Box p={5} shadow="md" borderWidth="1px" borderRadius="lg" bg={cardBg}>
                        <Stat>
                            <StatLabel fontSize="lg">Your Messages</StatLabel>
                            <StatNumber>{stats.totalMessages}</StatNumber>
                            <StatHelpText>Across all topics</StatHelpText>
                            <Button
                                as={Link}
                                to="/my-messages"
                                colorScheme="blue"
                                variant="outline"
                                size="sm"
                                mt={2}
                            >
                                View All
                            </Button>
                        </Stat>
                    </Box>

                    <Box p={5} shadow="md" borderWidth="1px" borderRadius="lg" bg={cardBg}>
                        <Stat>
                            <StatLabel fontSize="lg">Active Topics</StatLabel>
                            <StatNumber>{stats.activeTopics}</StatNumber>
                            <StatHelpText>Join the conversation</StatHelpText>
                            <Button
                                as={Link}
                                to="/topics"
                                colorScheme="blue"
                                variant="outline"
                                size="sm"
                                mt={2}
                            >
                                Browse Topics
                            </Button>
                        </Stat>
                    </Box>

                    <Box p={5} shadow="md" borderWidth="1px" borderRadius="lg" bg={cardBg}>
                        <Stat>
                            <StatLabel fontSize="lg">Share Something</StatLabel>
                            <StatNumber>New Post</StatNumber>
                            <StatHelpText>Create a new message</StatHelpText>
                            <Button
                                as={Link}
                                to="/post-message"
                                colorScheme="blue"
                                size="sm"
                                mt={2}
                            >
                                Post Now
                            </Button>
                        </Stat>
                    </Box>
                </SimpleGrid>

                {/* Quick Actions */}
                <Box
                    p={5}
                    mt={6}
                    shadow="md"
                    borderWidth="1px"
                    borderRadius="lg"
                    bg={cardBg}
                >
                    <Heading size="md" mb={4}>Quick Actions</Heading>
                    <SimpleGrid columns={{ base: 1, sm: 2, md: 4 }} spacing={4}>
                        <Button as={Link} to="/post-message" colorScheme="blue" variant="solid">
                            Create Post
                        </Button>
                        <Button as={Link} to="/topics" colorScheme="green" variant="solid">
                            Browse Topics
                        </Button>
                        <Button as={Link} to="/my-messages" colorScheme="purple" variant="solid">
                            My Messages
                        </Button>
                        <Button as={Link} to="/profile" colorScheme="orange" variant="solid">
                            Edit Profile
                        </Button>
                    </SimpleGrid>
                </Box>
            </VStack>
        </Container>
    );
};

export default Dashboard;
