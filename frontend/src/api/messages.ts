import axios from 'axios';
import { API_ENDPOINTS } from '../config';
import { callApiWithFallback, getAuthHeaders } from './apiUtils';

// Define types for message data
interface MessagePayload {
    content: string;
    topicName: string;
    userId: string;
    metadata?: Record<string, any>;
}

interface MessageResponse {
    id: string;
    content: string;
    userId: string;
    timestamp: string;
    metadata?: Record<string, any>;
}

interface UserMessagesResponse {
    user_id: string;
    total: number;
    messages: Array<{
        message: MessageResponse;
        topic: string | { name: string; description: string };
    }>;
}

/**
 * Get all available topics
 * @returns Array of topics
 */
export async function getTopics() {
    return callApiWithFallback('/topics', 'get');
}

/**
 * Post a new message to a topic
 * @param payload Message data to post
 * @returns The created message
 */
export const postMessage = async (payload: MessagePayload): Promise<MessageResponse> => {
    return callApiWithFallback(
        `/topics/${payload.topicName}/messages`,
        'post',
        {
            headers: {
                ...getAuthHeaders(),
                'Content-Type': 'application/json'
            }
        },
        {
            content: payload.content,
            userId: payload.userId,
            metadata: payload.metadata || {}
        }
    );
};

/**
 * Delete a message from a topic
 * @param topicName The topic containing the message
 * @param messageId The ID of the message to delete
 */
export const deleteMessage = async (topicName: string, messageId: string): Promise<void> => {
    await callApiWithFallback(
        `/topics/${topicName}/messages/${messageId}`,
        'delete',
        {
            headers: getAuthHeaders()
        }
    );
};

/**
 * Get all messages for a specific user
 * @param userId The user ID to get messages for
 * @returns Object containing user messages
 */
export const getUserMessages = async (userId: string): Promise<UserMessagesResponse> => {
    return callApiWithFallback(
        `/users/${userId}/messages`,
        'get',
        {
            headers: getAuthHeaders()
        }
    );
};

/**
 * Get all messages in a specific topic
 * @param topicName The topic to get messages from
 * @returns Array of messages
 */
export const getTopicMessages = async (topicName: string): Promise<MessageResponse[]> => {
    return callApiWithFallback(
        `/topics/${topicName}/messages`,
        'get',
        {
            headers: getAuthHeaders()
        }
    );
};
