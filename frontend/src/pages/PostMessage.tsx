import React, { useState, useEffect } from 'react';
import {
    Box,
    Button,
    Container,
    FormControl,
    FormLabel,
    FormErrorMessage,
    Heading,
    Input,
    Select,
    Textarea,
    VStack,
    useColorModeValue,
    useToast,
    Text,
    Flex,
    Spinner,
} from '@chakra-ui/react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { getTopics, postMessage } from '../api/messages';

interface Topic {
    id: string;
    name: string;
    description: string;
}

const PostMessage: React.FC = () => {
    const [content, setContent] = useState('');
    const [selectedTopic, setSelectedTopic] = useState('');
    const [topics, setTopics] = useState<Topic[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const { user } = useAuth();
    const toast = useToast();
    const navigate = useNavigate();

    const bgColor = useColorModeValue('white', 'gray.700');

    // Fetch available topics
    useEffect(() => {
        const fetchTopics = async () => {
            try {
                setIsLoading(true);
                const response = await getTopics();

                if (response && Array.isArray(response.topics)) {
                    setTopics(response.topics);
                    // Select the first topic by default if available
                    if (response.topics.length > 0) {
                        setSelectedTopic(response.topics[0].name);
                    }
                } else {
                    // Fallback topics
                    const fallbackTopics = [
                        { id: '1', name: 'General', description: 'General discussions' },
                        { id: '2', name: 'Events', description: 'Local events' },
                        { id: '3', name: 'Help', description: 'Requests for help' },
                    ];
                    setTopics(fallbackTopics);
                    setSelectedTopic('General');
                }
            } catch (err) {
                console.error('Failed to fetch topics:', err);
                setError('Failed to load topics. Please try again later.');

                // Set fallback topics
                const fallbackTopics = [
                    { id: '1', name: 'General', description: 'General discussions' },
                    { id: '2', name: 'Events', description: 'Local events' },
                    { id: '3', name: 'Help', description: 'Requests for help' },
                ];
                setTopics(fallbackTopics);
                setSelectedTopic('General');
            } finally {
                setIsLoading(false);
            }
        };

        fetchTopics();
    }, []);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        // Validation
        if (!content.trim()) {
            toast({
                title: 'Error',
                description: 'Message content cannot be empty',
                status: 'error',
                duration: 3000,
                isClosable: true,
            });
            return;
        }

        if (!selectedTopic) {
            toast({
                title: 'Error',
                description: 'Please select a topic',
                status: 'error',
                duration: 3000,
                isClosable: true,
            });
            return;
        }

        // Submit the message
        setIsSubmitting(true);

        try {
            const response = await postMessage({
                content,
                topicName: selectedTopic,
                userId: user?.id || 'anonymous',
                metadata: { source: 'web' }
            });

            toast({
                title: 'Message posted',
                description: 'Your message has been posted successfully',
                status: 'success',
                duration: 5000,
                isClosable: true,
            });

            // Redirect to the topic or my messages page
            navigate('/my-messages');
        } catch (err) {
            console.error('Failed to post message:', err);
            toast({
                title: 'Error',
                description: 'Failed to post message. Please try again later.',
                status: 'error',
                duration: 5000,
                isClosable: true,
            });
        } finally {
            setIsSubmitting(false);
        }
    };

    if (isLoading) {
        return (
            <Container centerContent py={10}>
                <Spinner size="xl" />
                <Text mt={4}>Loading...</Text>
            </Container>
        );
    }

    return (
        <Container maxW="container.md" py={8}>
            <Box bg={bgColor} p={8} borderRadius="lg" boxShadow="md">
                <VStack spacing={6} align="stretch">
                    <Heading as="h1" size="xl" textAlign="center">
                        Post a New Message
                    </Heading>

                    {error && (
                        <Text color="red.500" textAlign="center">
                            {error}
                        </Text>
                    )}

                    <form onSubmit={handleSubmit}>
                        <VStack spacing={4} align="stretch">
                            <FormControl isRequired>
                                <FormLabel>Topic</FormLabel>
                                <Select
                                    value={selectedTopic}
                                    onChange={(e) => setSelectedTopic(e.target.value)}
                                    placeholder="Select a topic"
                                >
                                    {topics.map((topic) => (
                                        <option key={topic.id} value={topic.name}>
                                            {topic.name} - {topic.description}
                                        </option>
                                    ))}
                                </Select>
                            </FormControl>

                            <FormControl isRequired>
                                <FormLabel>Message</FormLabel>
                                <Textarea
                                    value={content}
                                    onChange={(e) => setContent(e.target.value)}
                                    placeholder="What would you like to share with your community?"
                                    size="lg"
                                    minH="200px"
                                    resize="vertical"
                                />
                                <FormErrorMessage>Message cannot be empty</FormErrorMessage>
                            </FormControl>

                            <Flex justifyContent="space-between" mt={6}>
                                <Button
                                    variant="outline"
                                    onClick={() => navigate(-1)}
                                >
                                    Cancel
                                </Button>
                                <Button
                                    type="submit"
                                    colorScheme="blue"
                                    isLoading={isSubmitting}
                                    loadingText="Posting..."
                                >
                                    Post Message
                                </Button>
                            </Flex>
                        </VStack>
                    </form>
                </VStack>
            </Box>
        </Container>
    );
};

export default PostMessage;
