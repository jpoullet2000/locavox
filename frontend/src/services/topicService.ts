import { API_BASE_URL, TOPIC_ENDPOINTS } from '../config';

// Ensure we're using the correct imports and environment variables
console.log('API Base URL in topicService:', API_BASE_URL);

interface Topic {
    id: string;
    title: string;
    description: string;
    imageUrl?: string;
    // Add other properties as needed
}

export const fetchTopics = async (): Promise<Topic[]> => {
    try {
        const response = await fetch(`${API_BASE_URL}${TOPIC_ENDPOINTS.GET_ALL}`);

        if (!response.ok) {
            throw new Error(`Error: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error('Error fetching topics:', error);
        // Log the URL we're trying to access
        console.log(`Attempted to fetch from: ${API_BASE_URL}${TOPIC_ENDPOINTS.GET_ALL}`);
        // If API is not ready yet, return mock data for development
        return mockTopics;
    }
};

export const fetchTopicById = async (id: string): Promise<Topic> => {
    try {
        const response = await fetch(`${API_BASE_URL}${TOPIC_ENDPOINTS.GET_BY_ID(id)}`);

        if (!response.ok) {
            throw new Error(`Error: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error(`Error fetching topic ${id}:`, error);
        // Log the URL we're trying to access
        console.log(`Attempted to fetch from: ${API_BASE_URL}${TOPIC_ENDPOINTS.GET_BY_ID(id)}`);
        // Return a mock topic for development
        return mockTopics.find(topic => topic.id === id) || mockTopics[0];
    }
};

// Mock data for development
const mockTopics: Topic[] = [
    {
        id: '1',
        title: 'Local Events',
        description: 'Discover upcoming events in your community.',
        imageUrl: 'https://via.placeholder.com/300x200?text=Events'
    },
    {
        id: '2',
        title: 'Community Projects',
        description: 'Learn about and get involved with local community projects.',
        imageUrl: 'https://via.placeholder.com/300x200?text=Projects'
    },
    {
        id: '3',
        title: 'Local Businesses',
        description: 'Support local businesses and discover new favorites.',
        imageUrl: 'https://via.placeholder.com/300x200?text=Businesses'
    },
    {
        id: '4',
        title: 'Neighborhood News',
        description: 'Stay updated on what\'s happening in your neighborhood.',
        imageUrl: 'https://via.placeholder.com/300x200?text=News'
    }
];
