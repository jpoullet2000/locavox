import React from 'react';
import {
    Box,
    Container,
    Stack,
    Text,
    Link,
    useColorModeValue,
    Flex,
} from '@chakra-ui/react';
import { Link as RouterLink } from 'react-router-dom';

const Footer: React.FC = () => {
    return (
        <Box
            bg={useColorModeValue('gray.50', 'gray.900')}
            color={useColorModeValue('gray.700', 'gray.200')}
            mt="auto"
            borderTopWidth={1}
            borderStyle="solid"
            borderColor={useColorModeValue('gray.200', 'gray.700')}>
            <Container
                as={Stack}
                maxW="container.lg"
                py={4}
                direction={{ base: 'column', md: 'row' }}
                spacing={4}
                justify={{ base: 'center', md: 'space-between' }}
                align={{ base: 'center', md: 'center' }}>
                <Text>© 2025 LocaVox. All rights reserved</Text>
                <Stack direction="row" spacing={6}>
                    <Link as={RouterLink} to="/">Home</Link>
                    <Link as={RouterLink} to="/about">About</Link>
                    <Link as={RouterLink} to="/contact">Contact</Link>
                    <Link as={RouterLink} to="/terms">Terms</Link>
                    <Link as={RouterLink} to="/privacy">Privacy</Link>
                </Stack>
            </Container>
        </Box>
    );
};

export default Footer;
