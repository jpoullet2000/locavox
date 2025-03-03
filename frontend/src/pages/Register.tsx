import React, { useState } from 'react';
import {
    Box,
    Button,
    FormControl,
    FormLabel,
    FormErrorMessage,
    Input,
    Stack,
    Heading,
    Text,
    useColorModeValue,
    Container,
    useToast,
    InputGroup,
    InputRightElement,
    Link as ChakraLink,
} from '@chakra-ui/react';
import { ViewIcon, ViewOffIcon } from '@chakra-ui/icons';
import { Link, useNavigate } from 'react-router-dom';

const Register: React.FC = () => {
    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [showPassword, setShowPassword] = useState(false);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [errors, setErrors] = useState<Record<string, string>>({});

    const navigate = useNavigate();
    const toast = useToast();

    const validateForm = () => {
        const newErrors: Record<string, string> = {};

        if (!username) {
            newErrors.username = 'Username is required';
        } else if (username.length < 3) {
            newErrors.username = 'Username must be at least 3 characters';
        }

        if (!email) {
            newErrors.email = 'Email is required';
        } else if (!/\S+@\S+\.\S+/.test(email)) {
            newErrors.email = 'Email is invalid';
        }

        if (!password) {
            newErrors.password = 'Password is required';
        } else if (password.length < 6) {
            newErrors.password = 'Password must be at least 6 characters';
        }

        if (password !== confirmPassword) {
            newErrors.confirmPassword = 'Passwords do not match';
        }

        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        if (!validateForm()) {
            return;
        }

        setIsSubmitting(true);

        try {
            // In a real app, you would call your register API here
            await new Promise(resolve => setTimeout(resolve, 1000));

            toast({
                title: 'Account created.',
                description: "We've created your account for you.",
                status: 'success',
                duration: 5000,
                isClosable: true,
            });

            navigate('/login');
        } catch (error) {
            toast({
                title: 'An error occurred.',
                description: 'Unable to create your account.',
                status: 'error',
                duration: 5000,
                isClosable: true,
            });
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <Container maxW="lg" py={12}>
            <Stack spacing={8}>
                <Stack align="center">
                    <Heading fontSize="2xl">Create your account</Heading>
                    <Text fontSize="md" color="gray.600">
                        to enjoy all of our community features ✌️
                    </Text>
                </Stack>

                <Box
                    rounded="lg"
                    bg={useColorModeValue('white', 'gray.700')}
                    boxShadow="lg"
                    p={8}
                >
                    <form onSubmit={handleSubmit}>
                        <Stack spacing={4}>
                            <FormControl id="username" isRequired isInvalid={!!errors.username}>
                                <FormLabel>Username</FormLabel>
                                <Input
                                    type="text"
                                    value={username}
                                    onChange={(e) => setUsername(e.target.value)}
                                />
                                <FormErrorMessage>{errors.username}</FormErrorMessage>
                            </FormControl>

                            <FormControl id="email" isRequired isInvalid={!!errors.email}>
                                <FormLabel>Email address</FormLabel>
                                <Input
                                    type="email"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                />
                                <FormErrorMessage>{errors.email}</FormErrorMessage>
                            </FormControl>

                            <FormControl id="password" isRequired isInvalid={!!errors.password}>
                                <FormLabel>Password</FormLabel>
                                <InputGroup>
                                    <Input
                                        type={showPassword ? 'text' : 'password'}
                                        value={password}
                                        onChange={(e) => setPassword(e.target.value)}
                                    />
                                    <InputRightElement h="full">
                                        <Button
                                            variant="ghost"
                                            onClick={() => setShowPassword(!showPassword)}
                                        >
                                            {showPassword ? <ViewOffIcon /> : <ViewIcon />}
                                        </Button>
                                    </InputRightElement>
                                </InputGroup>
                                <FormErrorMessage>{errors.password}</FormErrorMessage>
                            </FormControl>

                            <FormControl id="confirmPassword" isRequired isInvalid={!!errors.confirmPassword}>
                                <FormLabel>Confirm Password</FormLabel>
                                <InputGroup>
                                    <Input
                                        type={showPassword ? 'text' : 'password'}
                                        value={confirmPassword}
                                        onChange={(e) => setConfirmPassword(e.target.value)}
                                    />
                                    <InputRightElement h="full">
                                        <Button
                                            variant="ghost"
                                            onClick={() => setShowPassword(!showPassword)}
                                        >
                                            {showPassword ? <ViewOffIcon /> : <ViewIcon />}
                                        </Button>
                                    </InputRightElement>
                                </InputGroup>
                                <FormErrorMessage>{errors.confirmPassword}</FormErrorMessage>
                            </FormControl>

                            <Stack spacing={10} pt={2}>
                                <Button
                                    type="submit"
                                    loadingText="Creating account..."
                                    size="lg"
                                    bg="blue.400"
                                    color="white"
                                    _hover={{
                                        bg: 'blue.500',
                                    }}
                                    isLoading={isSubmitting}
                                >
                                    Sign up
                                </Button>
                            </Stack>

                            <Stack pt={6}>
                                <Text align="center">
                                    Already a user? <ChakraLink as={Link} to="/login" color="blue.400">Login</ChakraLink>
                                </Text>
                            </Stack>
                        </Stack>
                    </form>
                </Box>
            </Stack>
        </Container>
    );
};

export default Register;
