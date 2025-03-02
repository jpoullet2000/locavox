import React from 'react';
import {
    Box,
    Container,
    Heading,
    Text,
    Stack,
    Image,
    Divider,
    useColorModeValue,
    Link
} from '@chakra-ui/react';
import { ExternalLinkIcon } from '@chakra-ui/icons';

const About: React.FC = () => {
    return (
        <Container maxW="container.md" py={8}>
            <Stack spacing={8}>
                <Box textAlign="center">
                    <Heading as="h1" size="xl" mb={2}>
                        About LocaVox
                    </Heading>
                    <Text color={useColorModeValue('gray.600', 'gray.400')}>
                        Connecting communities, one message at a time
                    </Text>
                </Box>

                <Box
                    borderRadius="lg"
                    overflow="hidden"
                    bg={useColorModeValue('white', 'gray.700')}
                    boxShadow="md"
                    p={6}
                >
                    <Stack spacing={5}>
                        <Text>
                            LocaVox is a community-focused platform designed to bring neighbors together and foster meaningful local connections.
                            Our mission is to create spaces where people can share information, offer help, and build stronger communities.
                        </Text>

                        <Divider />

                        <Box>
                            <Heading as="h2" size="md" mb={4}>
                                Our Features
                            </Heading>
                            <Stack spacing={4}>
                                <Feature
                                    title="Community Message Boards"
                                    description="Share and discuss topics relevant to your neighborhood."
                                />
                                <Feature
                                    title="Local Task Marketplace"
                                    description="Offer or find help with tasks in your community."
                                />
                                <Feature
                                    title="Event Organization"
                                    description="Create and discover local events happening near you."
                                />
                            </Stack>
                        </Box>

                        <Divider />

                        <Box>
                            <Heading as="h2" size="md" mb={4}>
                                Our Team
                            </Heading>
                            <Text mb={4}>
                                We're a passionate group of developers and community advocates who believe technology can bring people closer together.
                            </Text>
                        </Box>

                        <Divider />

                        <Box>
                            <Heading as="h2" size="md" mb={4}>
                                Contact Us
                            </Heading>
                            <Text>
                                Have questions or suggestions? We'd love to hear from you.
                            </Text>
                            <Link href="mailto:contact@locavox.com" color="blue.500" isExternal>
                                contact@locavox.com <ExternalLinkIcon mx="2px" />
                            </Link>
                        </Box>
                    </Stack>
                </Box>
            </Stack>
        </Container>
    );
};

interface FeatureProps {
    title: string;
    description: string;
}

const Feature: React.FC<FeatureProps> = ({ title, description }) => {
    return (
        <Box>
            <Text fontWeight="bold">{title}</Text>
            <Text>{description}</Text>
        </Box>
    );
};

export default About;
