import React, { useEffect, useState } from 'react';
import {
    Box,
    Container,
    Heading,
    Text,
    VStack,
    HStack,
    Badge,
    Divider,
    Spinner,
    Button,
    Alert,
    AlertIcon,
    useColorModeValue,
    Flex,
    useToast,
    Tag,
    TagLabel,
} from '@chakra-ui/react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { getUserMessages } from '../api/messages';

interface MessageData {
    message: {
        id: string;
        content: string;
        userId: string;
        timestamp: string;
        metadata?: Record<string, any>;
    };
    topic: string;
}

interface UserMessagesResponse {
    user_id: string;
    total: number;
    messages: MessageData[];
}

const MyMessages: React.FC = () => {
    const [messages, setMessages] = useState<MessageData[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [totalMessages, setTotalMessages] = useState(0);
    const { user } = useAuth();
    const toast = useToast();

    const bgColor = useColorModeValue('white', 'gray.700');
    const borderColor = useColorModeValue('gray.200', 'gray.600');

    useEffect(() => {
        const fetchMessages = async () => {
            if (!user?.id) {
                setError('Please log in to view your messages');
                setIsLoading(false);
                return;
            }

            try {
                setIsLoading(true);
                const response = await getUserMessages(user.id);
                setMessages(response.messages);
                setTotalMessages(response.total);
                setIsLoading(false);
            } catch (error) {
                console.error('Error fetching messages:', error);
                setError('Failed to fetch messages. Please try again later.');
                setIsLoading(false);
            }
        };

        fetchMessages();
    }, [user]);

    const formatDate = (dateString: string) => {
        const date = new Date(dateString);
        return date.toLocaleString();
    };

    if (isLoading) {
        return (
            <Container centerContent py={10}>
                <Spinner size="xl" />
                <Text mt={4}>Loading your messages...</Text>
            </Container>
        );
    }

    if (error) {
        return (
            <Container maxW="container.md" py={8}>
                <Alert status="error" borderRadius="md">
                    <AlertIcon />
                    {error}
                </Alert>
                <Button as={Link} to="/post-message" colorScheme="blue" mt={4}>
                    Post a New Message
                </Button>
            </Container>
        );
    }

    return (
        <Container maxW="container.lg" py={8}>
            <VStack spacing={6} align="stretch">
                <Flex justify="space-between" align="center">
                    <Heading as="h1" size="xl">
                        My Messages
                    </Heading>
                    <Button as={Link} to="/post-message" colorScheme="blue">
                        Post New Message
                    </Button>
                </Flex>

                {totalMessages > 0 ? (
                    <Text fontSize="md">
                        Showing {messages.length} of {totalMessages} total messages
                    </Text>
                ) : (
                    <Alert status="info" borderRadius="md">
                        <AlertIcon />
                        You haven't posted any messages yet. Click "Post New Message" to get started.
                    </Alert>
                )}

                <VStack spacing={4} align="stretch">
                    {messages.map((messageData) => (
                        <Box
                            key={messageData.message.id}
                            p={5}
                            borderWidth="1px"
                            borderRadius="lg"
                            borderColor={borderColor}
                            bg={bgColor}
                            boxShadow="sm"
                        >
                            <VStack align="stretch" spacing={3}>
                                <HStack justify="space-between">
                                    <Tag size="md" colorScheme="blue" borderRadius="full">
                                        <TagLabel>{messageData.topic}</TagLabel>
                                    </Tag>
                                    <Text fontSize="sm" color="gray.500">
                                        {formatDate(messageData.message.timestamp)}
                                    </Text>
                                </HStack>

                                <Text fontSize="md" whiteSpace="pre-wrap">
                                    {messageData.message.content}
                                </Text>

                                {messageData.message.metadata && Object.keys(messageData.message.metadata).length > 0 && (
                                    <>
                                        <Divider />
                                        <Box>
                                            <Text fontSize="sm" fontWeight="bold" mb={1}>
                                                Metadata:
                                            </Text>
                                            <HStack flexWrap="wrap" spacing={2}>
                                                {Object.entries(messageData.message.metadata).map(([key, value]) => (
                                                    <Badge key={key} colorScheme="gray">
                                                        {key}: {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                                                    </Badge>
                                                ))}
                                            </HStack>
                                        </Box>
                                    </>
                                )}
                            </VStack>
                        </Box>
                    ))}
                </VStack>

                {messages.length === 0 && !isLoading && !error && (
                    <Box textAlign="center" py={10}>
                        <Heading as="h3" size="md" mb={4}>
                            No messages found
                        </Heading>
                        <Text mb={6}>You haven't posted any messages yet.</Text>
                        <Button as={Link} to="/post-message" colorScheme="blue">
                            Post Your First Message
                        </Button>
                    </Box>
                )}
            </VStack>
        </Container>
    );
};

export default MyMessages;
