import React, { useState, useEffect } from 'react';
import {
    Box,
    Container,
    Heading,
    Text,
    Stack,
    Button,
    useColorModeValue,
    Spinner,
    Alert,
    AlertIcon,
    Flex,
    Avatar,
    Card,
    CardHeader,
    CardBody,
    Badge,
    Divider,
} from '@chakra-ui/react';
import { useParams, Link as RouterLink } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { getTopicMessages } from '../api/messages';

interface Message {
    id: string;
    content: string;
    userId: string;
    timestamp: string;
    metadata?: Record<string, any>;
}

const TopicView: React.FC = () => {
    const { topicName } = useParams<{ topicName: string }>();
    const [messages, setMessages] = useState<Message[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const { user } = useAuth();

    const bgColor = useColorModeValue('white', 'gray.700');
    const borderColor = useColorModeValue('gray.200', 'gray.600');

    useEffect(() => {
        const fetchTopicMessages = async () => {
            if (!topicName) {
                setError('Invalid topic name');
                setIsLoading(false);
                return;
            }

            try {
                const messagesData = await getTopicMessages(topicName);
                setMessages(messagesData);
            } catch (err) {
                console.error('Error fetching topic messages:', err);
                setError(`Failed to load messages for topic "${topicName}". Please try again later.`);
            } finally {
                setIsLoading(false);
            }
        };

        fetchTopicMessages();
    }, [topicName]);

    const formatDate = (dateString: string) => {
        const date = new Date(dateString);
        return date.toLocaleString();
    };

    if (isLoading) {
        return (
            <Container centerContent py={10}>
                <Spinner size="xl" />
                <Text mt={4}>Loading messages...</Text>
            </Container>
        );
    }

    return (
        <Container maxW="container.lg" py={8}>
            <Stack spacing={6}>
                <Box>
                    <Heading as="h1" size="xl" mb={2}>
                        {topicName}
                    </Heading>
                    <Text fontSize="lg" color="gray.600">
                        Community discussions about {topicName?.toLowerCase().replace('_', ' ')}
                    </Text>
                </Box>

                <Flex justify="space-between">
                    <Button
                        as={RouterLink}
                        to={`/post-message`}
                        state={{ defaultTopic: topicName }}
                        colorScheme="blue"
                    >
                        Post New Message
                    </Button>
                    <Button as={RouterLink} to="/dashboard" variant="outline">
                        Back to Dashboard
                    </Button>
                </Flex>

                {error ? (
                    <Alert status="error" borderRadius="md">
                        <AlertIcon />
                        {error}
                    </Alert>
                ) : messages.length === 0 ? (
                    <Box textAlign="center" py={10}>
                        <Alert status="info" borderRadius="md">
                            <AlertIcon />
                            No messages in this topic yet. Be the first to post!
                        </Alert>
                    </Box>
                ) : (
                    <Stack spacing={4} mt={4}>
                        {messages.map((message) => (
                            <Card
                                key={message.id}
                                bg={bgColor}
                                borderWidth="1px"
                                borderRadius="lg"
                                borderColor={borderColor}
                                boxShadow="sm"
                            >
                                <CardHeader>
                                    <Flex justify="space-between" align="center">
                                        <Flex align="center">
                                            <Avatar size="sm" name={message.userId} mr={2} />
                                            <Text fontWeight="bold">{message.userId}</Text>
                                        </Flex>
                                        <Text fontSize="sm" color="gray.500">
                                            {formatDate(message.timestamp)}
                                        </Text>
                                    </Flex>
                                </CardHeader>

                                <CardBody pt={0}>
                                    <Text whiteSpace="pre-wrap" mb={4}>
                                        {message.content}
                                    </Text>

                                    {message.metadata && Object.keys(message.metadata).length > 0 && (
                                        <>
                                            <Divider my={2} />
                                            <Box>
                                                <Text fontSize="sm" fontWeight="bold" mb={1}>
                                                    Metadata:
                                                </Text>
                                                <Flex wrap="wrap" gap={2}>
                                                    {Object.entries(message.metadata).map(([key, value]) => (
                                                        <Badge key={key} colorScheme="blue">
                                                            {key}: {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                                                        </Badge>
                                                    ))}
                                                </Flex>
                                            </Box>
                                        </>
                                    )}
                                </CardBody>
                            </Card>
                        ))}
                    </Stack>
                )}
            </Stack>
        </Container>
    );
};

export default TopicView;
