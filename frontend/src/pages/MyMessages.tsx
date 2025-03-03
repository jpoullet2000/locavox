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
    IconButton,
    AlertDialog,
    AlertDialogBody,
    AlertDialogContent,
    AlertDialogFooter,
    AlertDialogHeader,
    AlertDialogOverlay,
    useDisclosure,
} from '@chakra-ui/react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { getUserMessages, deleteMessage } from '../api/messages';
import { DeleteIcon } from '@chakra-ui/icons';
import { formatDate } from '../api/apiUtils';

interface MessageData {
    message: {
        id: string;
        content: string;
        userId: string;
        timestamp: string;
        metadata?: Record<string, any>;
    };
    topic: string | { name: string; description: string }; // Handle both string and object formats
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
    const [isDeleting, setIsDeleting] = useState(false);
    const [messageToDelete, setMessageToDelete] = useState<{ id: string; topicName: string } | null>(null);
    const { isOpen, onOpen, onClose } = useDisclosure();
    const cancelRef = React.useRef<HTMLButtonElement>(null);
    const { user } = useAuth();
    const toast = useToast();

    const bgColor = useColorModeValue('white', 'gray.700');
    const borderColor = useColorModeValue('gray.200', 'gray.600');

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

    useEffect(() => {
        fetchMessages();
    }, [user]);

    // Helper function to extract topic name regardless of format
    const getTopicName = (topic: string | { name: string; description: string }): string => {
        if (typeof topic === 'string') {
            return topic;
        }
        return topic.name;
    };

    const handleDeleteClick = (messageId: string, topicName: string | { name: string; description: string }) => {
        const topicNameStr = getTopicName(topicName);
        setMessageToDelete({ id: messageId, topicName: topicNameStr });
        onOpen();
    };

    const confirmDelete = async () => {
        if (!messageToDelete) return;

        setIsDeleting(true);
        try {
            await deleteMessage(messageToDelete.topicName, messageToDelete.id);
            // Remove the message from the local state
            setMessages(messages.filter(msg => msg.message.id !== messageToDelete.id));
            setTotalMessages(prev => Math.max(0, prev - 1));

            toast({
                title: 'Message deleted',
                description: 'Your message has been successfully deleted',
                status: 'success',
                duration: 3000,
                isClosable: true,
            });
        } catch (error) {
            console.error('Failed to delete message:', error);
            toast({
                title: 'Error',
                description: 'Failed to delete message. Please try again.',
                status: 'error',
                duration: 3000,
                isClosable: true,
            });
        } finally {
            setIsDeleting(false);
            onClose();
            setMessageToDelete(null);
        }
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
                                        <TagLabel>{getTopicName(messageData.topic)}</TagLabel>
                                    </Tag>
                                    <Flex align="center">
                                        <Text fontSize="sm" color="gray.500" mr={3}>
                                            {formatDate(messageData.message.timestamp)}
                                        </Text>
                                        {messageData.message.userId === user?.id && (
                                            <IconButton
                                                aria-label="Delete message"
                                                icon={<DeleteIcon />}
                                                size="sm"
                                                colorScheme="red"
                                                variant="ghost"
                                                onClick={() => handleDeleteClick(messageData.message.id, messageData.topic)}
                                            />
                                        )}
                                    </Flex>
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

            {/* Delete Confirmation Dialog */}
            <AlertDialog
                isOpen={isOpen}
                leastDestructiveRef={cancelRef}
                onClose={onClose}
            >
                <AlertDialogOverlay>
                    <AlertDialogContent>
                        <AlertDialogHeader fontSize="lg" fontWeight="bold">
                            Delete Message
                        </AlertDialogHeader>

                        <AlertDialogBody>
                            Are you sure? You can't undo this action afterwards.
                        </AlertDialogBody>

                        <AlertDialogFooter>
                            <Button ref={cancelRef} onClick={onClose} disabled={isDeleting}>
                                Cancel
                            </Button>
                            <Button
                                colorScheme="red"
                                onClick={confirmDelete}
                                ml={3}
                                isLoading={isDeleting}
                                loadingText="Deleting"
                            >
                                Delete
                            </Button>
                        </AlertDialogFooter>
                    </AlertDialogContent>
                </AlertDialogOverlay>
            </AlertDialog>
        </Container>
    );
};

export default MyMessages;
