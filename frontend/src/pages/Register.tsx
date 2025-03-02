import React, { useState } from 'react';
import {
    Box,
    Button,
    FormControl,
    FormLabel,
    Heading,
    Input,
    Stack,
    Text,
    useColorModeValue,
    FormErrorMessage,
    Alert,
    AlertIcon,
    Link,
    InputGroup,
    InputRightElement,
    IconButton,
} from '@chakra-ui/react';
import { ViewIcon, ViewOffIcon } from '@chakra-ui/icons';
import { Link as RouterLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const Register: React.FC = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [displayName, setDisplayName] = useState('');
    const [showPassword, setShowPassword] = useState(false);
    const [passwordError, setPasswordError] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);

    const { register, error, clearError } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        // Validate password match
        if (password !== confirmPassword) {
            setPasswordError('Passwords do not match');
            return;
        }

        // Clear any previous error
        setPasswordError('');
        setIsSubmitting(true);

        try {
            await register(email, password, displayName);
            navigate('/dashboard');
        } catch (error) {
            // Error is handled by the auth context
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <Box
            minH={'100vh'}
            display="flex"
            alignItems="center"
            justifyContent="center"
            bg={useColorModeValue('gray.50', 'gray.800')}>
            <Stack spacing={8} mx={'auto'} maxW={'lg'} py={12} px={6}>
                <Stack align={'center'}>
                    <Heading fontSize={'4xl'} textAlign={'center'}>
                        Sign up for LocaVox
                    </Heading>
                    <Text fontSize={'lg'} color={'gray.600'}>
                        to connect with your local community ✌️
                    </Text>
                </Stack>
                <Box
                    rounded={'lg'}
                    bg={useColorModeValue('white', 'gray.700')}
                    boxShadow={'lg'}
                    p={8}>
                    {error && (
                        <Alert status="error" mb={4} borderRadius="md">
                            <AlertIcon />
                            {error}
                        </Alert>
                    )}
                    <form onSubmit={handleSubmit}>
                        <Stack spacing={4}>
                            <FormControl id="displayName" isRequired>
                                <FormLabel>Display Name</FormLabel>
                                <Input
                                    type="text"
                                    value={displayName}
                                    onChange={(e) => {
                                        setDisplayName(e.target.value);
                                        clearError();
                                    }}
                                />
                            </FormControl>
                            <FormControl id="email" isRequired>
                                <FormLabel>Email address</FormLabel>
                                <Input
                                    type="email"
                                    value={email}
                                    onChange={(e) => {
                                        setEmail(e.target.value);
                                        clearError();
                                    }}
                                />
                            </FormControl>
                            <FormControl id="password" isRequired isInvalid={!!passwordError}>
                                <FormLabel>Password</FormLabel>
                                <InputGroup>
                                    <Input
                                        type={showPassword ? 'text' : 'password'}
                                        value={password}
                                        onChange={(e) => {
                                            setPassword(e.target.value);
                                            setPasswordError('');
                                            clearError();
                                        }}
                                    />
                                    <InputRightElement h={'full'}>
                                        <IconButton
                                            aria-label={showPassword ? 'Hide password' : 'Show password'}
                                            variant={'ghost'}
                                            onClick={() => setShowPassword(!showPassword)}
                                            icon={showPassword ? <ViewOffIcon /> : <ViewIcon />}
                                        />
                                    </InputRightElement>
                                </InputGroup>
                            </FormControl>
                            <FormControl id="confirmPassword" isRequired isInvalid={!!passwordError}>
                                <FormLabel>Confirm Password</FormLabel>
                                <Input
                                    type={showPassword ? 'text' : 'password'}
                                    value={confirmPassword}
                                    onChange={(e) => {
                                        setConfirmPassword(e.target.value);
                                        setPasswordError('');
                                        clearError();
                                    }}
                                />
                                {passwordError && <FormErrorMessage>{passwordError}</FormErrorMessage>}
                            </FormControl>
                            <Stack spacing={10} pt={2}>
                                <Button
                                    type="submit"
                                    loadingText="Submitting"
                                    size="lg"
                                    bg={'blue.400'}
                                    color={'white'}
                                    _hover={{
                                        bg: 'blue.500',
                                    }}
                                    isLoading={isSubmitting}>
                                    Sign up
                                </Button>
                            </Stack>
                            <Stack pt={6}>
                                <Text align={'center'}>
                                    Already a user? {' '}
                                    <Link as={RouterLink} to="/login" color={'blue.400'}>
                                        Login
                                    </Link>
                                </Text>
                            </Stack>
                        </Stack>
                    </form>
                </Box>
            </Stack>
        </Box>
    );
};

export default Register;
