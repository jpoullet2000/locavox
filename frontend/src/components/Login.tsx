import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import {
    Box,
    Button,
    FormControl,
    FormLabel,
    Input,
    VStack,
    Heading,
    Text,
    useToast,
    FormErrorMessage,
    Alert,
    AlertIcon,
} from '@chakra-ui/react';
import { useAuth } from '../contexts/AuthContext';

function Login() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [formErrors, setFormErrors] = useState<{ email?: string, password?: string }>({});
    const { login, error, loading, clearError } = useAuth();
    const navigate = useNavigate();
    const toast = useToast();

    // Validate form
    const validateForm = () => {
        const errors: { email?: string, password?: string } = {};
        let isValid = true;

        if (!email) {
            errors.email = 'Email is required';
            isValid = false;
        } else if (!/\S+@\S+\.\S+/.test(email)) {
            errors.email = 'Email is invalid';
            isValid = false;
        }

        if (!password) {
            errors.password = 'Password is required';
            isValid = false;
        }

        setFormErrors(errors);
        return isValid;
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        clearError();

        if (!validateForm()) return;

        try {
            console.log(`Login form submitted with email: ${email}`);
            await login(email, password);

            toast({
                title: 'Login successful',
                status: 'success',
                duration: 3000,
                isClosable: true,
            });

            navigate('/dashboard');
        } catch (err) {
            // Error is handled by the login function and stored in the auth context
            console.error('Login error handled by auth context:', err);
        }
    };

    return (
        <Box maxW="md" mx="auto" mt="10" p="6" borderWidth="1px" borderRadius="lg" boxShadow="lg">
            <VStack spacing="6">
                <Heading as="h1" size="xl">Login</Heading>

                {error && (
                    <Alert status="error" borderRadius="md">
                        <AlertIcon />
                        {error}
                    </Alert>
                )}

                <form onSubmit={handleSubmit} style={{ width: '100%' }}>
                    <VStack spacing="4">
                        <FormControl isInvalid={!!formErrors.email} isRequired>
                            <FormLabel>Email</FormLabel>
                            <Input
                                type="email"
                                placeholder="your@email.com"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                            />
                            <FormErrorMessage>{formErrors.email}</FormErrorMessage>
                        </FormControl>

                        <FormControl isInvalid={!!formErrors.password} isRequired>
                            <FormLabel>Password</FormLabel>
                            <Input
                                type="password"
                                placeholder="********"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                            />
                            <FormErrorMessage>{formErrors.password}</FormErrorMessage>
                        </FormControl>

                        <Button
                            colorScheme="blue"
                            width="full"
                            type="submit"
                            isLoading={loading}
                            loadingText="Logging in..."
                        >
                            Login
                        </Button>
                    </VStack>
                </form>

                <Text>
                    Don't have an account? <Link to="/register" style={{ color: 'blue' }}>Register</Link>
                </Text>

                <Text>
                    <Link to="/forgot-password" style={{ color: 'blue' }}>Forgot password?</Link>
                </Text>
            </VStack>
        </Box>
    );
}

export default Login;
