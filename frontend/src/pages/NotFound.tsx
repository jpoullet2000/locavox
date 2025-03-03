import React from 'react';
import { Box, Heading, Text, Button, VStack, Container, useColorModeValue } from '@chakra-ui/react';
import { Link } from 'react-router-dom';

const NotFound: React.FC = () => {
    const bg = useColorModeValue('gray.50', 'gray.900');
    const color = useColorModeValue('gray.800', 'white');

    return (
        <Container maxW="container.md" centerContent py={20}>
            <Box
                bg={useColorModeValue('white', 'gray.700')}
                p={10}
                borderRadius="lg"
                boxShadow="md"
                textAlign="center"
            >
                <VStack spacing={6}>
                    <Heading
                        as="h1"
                        size="4xl"
                        color={useColorModeValue('blue.500', 'blue.300')}
                    >
                        404
                    </Heading>

                    <Heading as="h2" size="xl">Page Not Found</Heading>

                    <Text fontSize="lg" color={useColorModeValue('gray.600', 'gray.400')}>
                        The page you're looking for doesn't exist or has been moved.
                    </Text>

                    <Button
                        as={Link}
                        to="/"
                        colorScheme="blue"
                        size="lg"
                        mt={4}
                    >
                        Return Home
                    </Button>
                </VStack>
            </Box>
        </Container>
    );
};

export default NotFound;
