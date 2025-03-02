import axios from 'axios';
import { API_BASE_URL } from '../config';

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
        topic: string;
    }>;
}

// Get topics available for posting
export const getTopics = async (): Promise<string[]> => {
    const response = await axios.get(`${API_BASE_URL}/topics`);
    return response.data.map((topic: any) => topic.name);
};

// Post a new message
export const postMessage = async (payload: MessagePayload): Promise<MessageResponse> => {
    const response = await axios.post(`${API_BASE_URL}/topics/${payload.topicName}/messages`, {
        content: payload.content,
        userId: payload.userId,
        metadata: payload.metadata || {},
    });
    return response.data;
};

// Get messages for a specific user
export const getUserMessages = async (userId: string): Promise<UserMessagesResponse> => {
    const response = await axios.get(`${API_BASE_URL}/users/${userId}/messages`);
    return response.data;
};

// Get messages from a specific topic
export const getTopicMessages = async (topicName: string): Promise<MessageResponse[]> => {
    const response = await axios.get(`${API_BASE_URL}/topics/${topicName}/messages`);
    return response.data;
};
