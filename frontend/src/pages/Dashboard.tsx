import React, { useState, useEffect } from 'react';
import {
    Box,
    Heading,
    Text,
    SimpleGrid,
    Container,
    Button,
    Stack,
    Icon,
    Card,
    CardHeader,
    CardBody,
    CardFooter,
    Avatar,
    Flex,
    Spinner,
    Center,
    useColorModeValue,
} from '@chakra-ui/react';
import { Link as RouterLink } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { getTopics } from '../api/messages';
import { AddIcon, ChatIcon } from '@chakra-ui/icons';

interface Topic {
    name: string;
    description: string;
}

const Dashboard: React.FC = () => {
    const [topics, setTopics] = useState<Topic[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const { user } = useAuth();

    const bgColor = useColorModeValue('white', 'gray.700');
    const borderColor = useColorModeValue('gray.200', 'gray.600');

    useEffect(() => {
        const fetchTopics = async () => {
            try {
                const topicNames = await getTopics();
                // Convert simple topic names to Topic objects with descriptions
                const formattedTopics = topicNames.map(name => ({
                    name,
                    description: `Discussion about ${name.toLowerCase().replace('_', ' ')}`
                }));
                setTopics(formattedTopics);
                setError(null);
            } catch (err) {
                console.error('Error fetching topics:', err);
                setError('Failed to load topics. Please try again later.');
            } finally {
                setIsLoading(false);
            }
        };

        fetchTopics();
    }, []);

    if (isLoading) {
        return (
            <Center h="50vh">
                <Spinner size="xl" />
            </Center>
        );
    }

    return (
        <Container maxW="container.xl" py={8}>
            <Box textAlign="center" mb={10}>
                <Heading as="h1" size="xl" mb={2}>
                    Welcome, {user?.displayName || 'Neighbor'}!
                </Heading>
                <Text fontSize="lg" color="gray.600">
                    Stay connected with your local community
                </Text>
            </Box>

            <SimpleGrid columns={{ base: 1, md: 2 }} spacing={6} mb={8}>
                <Card bg={bgColor} borderWidth="1px" borderColor={borderColor} boxShadow="sm">
                    <CardHeader>
                        <Heading size="md">Post a Message</Heading>
                    </CardHeader>
                    <CardBody>
                        <Text>Share news, ask questions, or start discussions with your community.</Text>
                    </CardBody>
                    <CardFooter>
                        <Button as={RouterLink} to="/post-message" colorScheme="blue" leftIcon={<Icon as={ChatIcon} />}>
                            Create Post
                        </Button>
                    </CardFooter>
                </Card>

                <Card bg={bgColor} borderWidth="1px" borderColor={borderColor} boxShadow="sm">
                    <CardHeader>
                        <Heading size="md">Your Messages</Heading>
                    </CardHeader>
                    <CardBody>
                        <Text>View all messages you've posted across different topics.</Text>
                    </CardBody>
                    <CardFooter>
                        <Button as={RouterLink} to="/my-messages" colorScheme="green" leftIcon={<Icon as={AddIcon} />}>
                            View Your Messages
                        </Button>
                    </CardFooter>
                </Card>
            </SimpleGrid>

            <Box mb={8}>
                <Heading as="h2" size="lg" mb={4}>
                    Community Topics
                </Heading>
                {error ? (
                    <Text color="red.500">{error}</Text>
                ) : (
                    <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={6}>
                        {topics.map((topic) => (
                            <Card
                                key={topic.name}
                                bg={bgColor}
                                borderWidth="1px"
                                borderColor={borderColor}
                                boxShadow="sm"
                                transition="all 0.3s"
                                _hover={{ transform: 'translateY(-5px)', boxShadow: 'md' }}
                            >
                                <CardHeader>
                                    <Heading size="md">{topic.name}</Heading>
                                </CardHeader>
                                <CardBody>
                                    <Text>{topic.description}</Text>
                                </CardBody>
                                <CardFooter>
                                    <Button
                                        as={RouterLink}
                                        to={`/topics/${topic.name}`}
                                        variant="outline"
                                        colorScheme="blue"
                                    >
                                        View Topic
                                    </Button>
                                </CardFooter>
                            </Card>
                        ))}
                    </SimpleGrid>
                )}
            </Box>
        </Container>
    );
};

export default Dashboard;
