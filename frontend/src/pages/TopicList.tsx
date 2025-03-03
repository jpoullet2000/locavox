import React, { useState, useEffect, useMemo } from 'react';
import {
    Box,
    Container,
    Heading,
    SimpleGrid,
    Input,
    InputGroup,
    InputLeftElement,
    Spinner,
    Text,
    Center,
    Select,
    Flex,
    Button,
    useToast,
} from '@chakra-ui/react';
import { SearchIcon } from '@chakra-ui/icons';
import TopicCard from '../components/TopicCard';
import { fetchTopics } from '../services/topicService';

interface Topic {
    id: string;
    title: string;
    description: string;
    category?: string; // Make this optional since it might be missing in some topics
    imageUrl?: string;
}

const TopicList: React.FC = () => {
    // Add console logging to track component rendering
    console.log('TopicList component rendering');

    // 1. First, declare all useState hooks
    const [topics, setTopics] = useState<Topic[]>([]);
    const [filteredTopics, setFilteredTopics] = useState<Topic[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [searchQuery, setSearchQuery] = useState('');
    const [categoryFilter, setCategoryFilter] = useState('');

    // 2. Then, declare all other hooks, including useToast
    const toast = useToast();

    // 3. Use useMemo for derived state
    const categories = useMemo(() => {
        const uniqueCategories = new Set<string>();
        topics.forEach(topic => {
            if (topic.category && topic.category.trim() !== '') {
                uniqueCategories.add(topic.category);
            }
        });
        return Array.from(uniqueCategories).sort();
    }, [topics]);

    // 4. useEffect for data fetching
    useEffect(() => {
        console.log('TopicList useEffect running - fetching topics');

        const getTopics = async () => {
            try {
                setLoading(true);
                const topicsData = await fetchTopics();
                console.log('Topics fetched successfully:', topicsData);
                setTopics(topicsData);
                setFilteredTopics(topicsData);
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

    // 5. useEffect for filtering
    useEffect(() => {
        console.log('Filtering topics with searchQuery:', searchQuery, 'and categoryFilter:', categoryFilter);

        // Add safe filtering logic with null checks
        let filtered = [...topics];

        // Filter by category if selected
        if (categoryFilter) {
            filtered = filtered.filter(topic =>
                topic.category && topic.category === categoryFilter
            );
        }

        // Filter by search query if provided
        if (searchQuery.trim() !== '') {
            const query = searchQuery.toLowerCase();
            filtered = filtered.filter(topic => {
                // Add null checks before calling toLowerCase()
                const titleMatch = topic.title ? topic.title.toLowerCase().includes(query) : false;
                const descMatch = topic.description ? topic.description.toLowerCase().includes(query) : false;
                const categoryMatch = topic.category ? topic.category.toLowerCase().includes(query) : false;
                return titleMatch || descMatch || categoryMatch;
            });
        }

        setFilteredTopics(filtered);
    }, [topics, searchQuery, categoryFilter]);

    // 6. Event handlers
    const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setSearchQuery(e.target.value);
    };

    const handleCategoryChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
        setCategoryFilter(e.target.value);
    };

    const handleClearFilters = () => {
        setSearchQuery('');
        setCategoryFilter('');
        setFilteredTopics(topics);
    };

    // 7. Render
    return (
        <Container maxW="container.xl" py={8}>
            <Heading as="h1" mb={6}>Browse Topics</Heading>

            <Flex direction={{ base: "column", md: "row" }} mb={6} gap={4}>
                <InputGroup flex="2">
                    <InputLeftElement pointerEvents="none">
                        <SearchIcon color="gray.300" />
                    </InputLeftElement>
                    <Input
                        placeholder="Search topics..."
                        value={searchQuery}
                        onChange={handleSearchChange}
                        data-testid="topic-search-input"
                    />
                </InputGroup>

                <Select
                    placeholder="Filter by category"
                    value={categoryFilter}
                    onChange={handleCategoryChange}
                    flex="1"
                    data-testid="category-filter"
                >
                    {categories.map(category => (
                        <option key={category} value={category}>
                            {category}
                        </option>
                    ))}
                </Select>

                <Button
                    onClick={handleClearFilters}
                    variant="outline"
                    isDisabled={!searchQuery && !categoryFilter}
                >
                    Clear Filters
                </Button>
            </Flex>

            {loading ? (
                <Center py={10}>
                    <Spinner size="xl" />
                </Center>
            ) : error ? (
                <Center py={10}>
                    <Text color="red.500">{error}</Text>
                </Center>
            ) : filteredTopics.length === 0 ? (
                <Center py={10} flexDirection="column" gap={4}>
                    <Text>No topics found matching your criteria.</Text>
                    {(searchQuery || categoryFilter) && (
                        <Button onClick={handleClearFilters} colorScheme="blue">
                            Clear Filters
                        </Button>
                    )}
                </Center>
            ) : (
                <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={6}>
                    {filteredTopics.map((topic) => (
                        <TopicCard key={topic.id} topic={topic} />
                    ))}
                </SimpleGrid>
            )}
        </Container>
    );
};

export default TopicList;
