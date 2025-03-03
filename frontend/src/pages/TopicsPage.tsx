import React, { useEffect, useState } from 'react';
import {
    Box,
    Heading,
    SimpleGrid,
    Spinner,
    Center,
    Text,
    Container,
    useToast
} from '@chakra-ui/react';
import TopicCard from '../components/TopicCard';
import { fetchTopics } from '../services/topicService';

interface Topic {
    id: string;
    title: string;
    description: string;
    imageUrl?: string;
    // Add other properties as needed
}

const TopicsPage: React.FC = () => {
    // Add console log to confirm this component is being rendered
    console.log('TopicsPage component rendering');

    const [topics, setTopics] = useState<Topic[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const toast = useToast();

    useEffect(() => {
        console.log('TopicsPage useEffect running');

        const getTopics = async () => {
            try {
                setLoading(true);
                console.log('Fetching topics...');
                const topicsData = await fetchTopics();
                console.log('Topics fetched successfully:', topicsData);
                setTopics(topicsData);
                setError(null);
            } catch (err) {
                console.error('Error fetching topics:', err);
                setError('Failed to load topics. Please try again later.');
                toast({
                    title: 'Error',
                    description: 'Failed to load topics. Please try again later.',
                    status: 'error',
                    duration: 5000,
                    isClosable: true,
                });
            } finally {
                setLoading(false);
            }
        };

        getTopics();
    }, [toast]);

    return (
        <Container maxW="container.xl" py={8}>
            <div id="topics-page-marker">TopicsPage rendered</div>
            <Heading as="h1" mb={6}>Browse Topics</Heading>

            {loading ? (
                <Center py={10}>
                    <Spinner size="xl" />
                </Center>
            ) : error ? (
                <Center py={10}>
                    <Text color="red.500">{error}</Text>
                </Center>
            ) : topics.length === 0 ? (
                <Center py={10}>
                    <Text>No topics found. Check back later!</Text>
                </Center>
            ) : (
                <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={6}>
                    {topics.map((topic) => (
                        <TopicCard key={topic.id} topic={topic} />
                    ))}
                </SimpleGrid>
            )}
        </Container>
    );
};

export default TopicsPage;
