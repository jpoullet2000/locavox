import React, { useState, useEffect } from 'react';
import {
    Box,
    Button,
    Container,
    FormControl,
    FormLabel,
    Heading,
    Input,
    Select,
    Textarea,
    VStack,
    useToast
} from '@chakra-ui/react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import { getTopics, postMessage } from '../api/messages';

const PostMessage: React.FC = () => {
    const [content, setContent] = useState('');
    const [selectedTopic, setSelectedTopic] = useState('');
    const [topics, setTopics] = useState<string[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const { user } = useAuth();
    const toast = useToast();
    const navigate = useNavigate();

    useEffect(() => {
        const fetchTopics = async () => {
            try {
                const topicsData = await getTopics();
                setTopics(topicsData);
                if (topicsData.length > 0) {
                    setSelectedTopic(topicsData[0]);
                }
            } catch (error) {
                toast({
                    title: 'Error',
                    description: 'Failed to fetch topics',
                    status: 'error',
                    duration: 3000,
                    isClosable: true,
                });
            }
        };

        fetchTopics();
    }, [toast]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

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

        setIsLoading(true);

        try {
            await postMessage({
                content,
                topicName: selectedTopic,
                userId: user?.id || 'anonymous',
                metadata: {
                    source: 'web',
                    timestamp: new Date().toISOString(),
                }
            });

            toast({
                title: 'Success',
                description: 'Message posted successfully',
                status: 'success',
                duration: 3000,
                isClosable: true,
            });

            setContent('');

            // Navigate to the user's messages page after successful post
            navigate('/my-messages');
        } catch (error) {
            toast({
                title: 'Error',
                description: 'Failed to post message',
                status: 'error',
                duration: 3000,
                isClosable: true,
            });
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <Container maxW="container.md" py={8}>
            <VStack spacing={6} align="stretch">
                <Heading as="h1" size="xl" textAlign="center">
                    Post a New Message
                </Heading>

                <Box as="form" onSubmit={handleSubmit} bg="white" p={6} borderRadius="md" boxShadow="md">
                    <VStack spacing={4} align="stretch">
                        <FormControl isRequired>
                            <FormLabel>Select Topic</FormLabel>
                            <Select
                                value={selectedTopic}
                                onChange={(e) => setSelectedTopic(e.target.value)}
                                placeholder="Select a topic"
                            >
                                {topics.map((topic) => (
                                    <option key={topic} value={topic}>
                                        {topic}
                                    </option>
                                ))}
                            </Select>
                        </FormControl>

                        <FormControl isRequired>
                            <FormLabel>Message</FormLabel>
                            <Textarea
                                value={content}
                                onChange={(e) => setContent(e.target.value)}
                                placeholder="Enter your message here..."
                                size="lg"
                                rows={6}
                            />
                        </FormControl>

                        <Button
                            type="submit"
                            colorScheme="blue"
                            size="lg"
                            isLoading={isLoading}
                            loadingText="Posting..."
                            width="full"
                            mt={4}
                        >
                            Post Message
                        </Button>
                    </VStack>
                </Box>
            </VStack>
        </Container>
    );
};

export default PostMessage;
