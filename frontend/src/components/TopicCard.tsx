import React from 'react';
import {
    Box,
    Heading,
    Text,
    LinkBox,
    LinkOverlay,
    Image,
    Badge,
} from '@chakra-ui/react';
import { Link as RouterLink } from 'react-router-dom';

interface TopicCardProps {
    topic: {
        id: string;
        title: string;
        description: string;
        category?: string;
        imageUrl?: string;
    };
}

const TopicCard: React.FC<TopicCardProps> = ({ topic }) => {
    // Add safeguards for undefined properties
    const { id, title = '', description = '', category, imageUrl } = topic;

    return (
        <LinkBox as="article" borderWidth="1px" borderRadius="lg" overflow="hidden">
            {imageUrl && (
                <Image
                    src={imageUrl}
                    alt={title || 'Topic image'}
                    height="200px"
                    width="100%"
                    objectFit="cover"
                    fallbackSrc="https://via.placeholder.com/300x200?text=Topic"
                />
            )}
            <Box p={4}>
                <LinkOverlay as={RouterLink} to={`/topics/${id}`}>
                    <Heading size="md" mb={2}>{title || 'Untitled Topic'}</Heading>
                </LinkOverlay>
                {category && (
                    <Badge colorScheme="teal" mb={2}>
                        {category}
                    </Badge>
                )}
                <Text noOfLines={3}>{description || 'No description available'}</Text>
            </Box>
        </LinkBox>
    );
};

export default TopicCard;
