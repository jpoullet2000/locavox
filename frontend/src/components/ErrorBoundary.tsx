import React, { Component, ErrorInfo, ReactNode } from 'react';
import {
    Box,
    Heading,
    Text,
    Button,
    Code,
    useColorModeValue,
    Container,
    Stack
} from '@chakra-ui/react';
import { WarningTwoIcon } from '@chakra-ui/icons';

interface Props {
    children: ReactNode;
    fallback?: ReactNode;
    componentName?: string;
}

interface State {
    hasError: boolean;
    error: Error | null;
    errorInfo: ErrorInfo | null;
}

class ErrorBoundary extends Component<Props, State> {
    constructor(props: Props) {
        super(props);
        this.state = {
            hasError: false,
            error: null,
            errorInfo: null
        };
    }

    static getDerivedStateFromError(error: Error): State {
        // Update state so the next render will show the fallback UI.
        return { hasError: true, error, errorInfo: null };
    }

    componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
        // You can also log the error to an error reporting service
        console.error("ErrorBoundary caught an error", error, errorInfo);
        this.setState({
            error: error,
            errorInfo: errorInfo
        });
    }

    render(): ReactNode {
        const { hasError, error, errorInfo } = this.state;
        const { children, fallback, componentName } = this.props;

        if (hasError) {
            if (fallback) {
                return fallback;
            }

            // You can render any custom fallback UI
            return (
                <ErrorFallback
                    error={error}
                    errorInfo={errorInfo}
                    componentName={componentName}
                    resetError={() => this.setState({ hasError: false, error: null, errorInfo: null })}
                />
            );
        }

        return children;
    }
}

// Separate fallback component for cleaner code
interface ErrorFallbackProps {
    error: Error | null;
    errorInfo: ErrorInfo | null;
    componentName?: string;
    resetError: () => void;
}

const ErrorFallback: React.FC<ErrorFallbackProps> = ({
    error,
    errorInfo,
    componentName,
    resetError
}) => {
    const bgColor = useColorModeValue('white', 'gray.800');
    const borderColor = useColorModeValue('red.500', 'red.300');

    return (
        <Container maxW="container.md" py={8}>
            <Box
                p={6}
                bg={bgColor}
                borderWidth="1px"
                borderColor={borderColor}
                borderRadius="md"
                boxShadow="md"
            >
                <Stack spacing={4} align="flex-start">
                    <Box display="flex" alignItems="center">
                        <WarningTwoIcon color="red.500" boxSize={6} mr={2} />
                        <Heading size="md" color="red.500">
                            Something went wrong {componentName ? `in ${componentName}` : ''}
                        </Heading>
                    </Box>

                    <Text>
                        We've encountered an error. Please try refreshing the page or contact support if the problem persists.
                    </Text>

                    {error && (
                        <Box bg="gray.50" p={3} borderRadius="md" width="100%" overflowX="auto">
                            <Text color="red.600" fontWeight="bold">Error:</Text>
                            <Code display="block" whiteSpace="pre-wrap" p={2}>
                                {error.toString()}
                            </Code>

                            {errorInfo && (
                                <>
                                    <Text color="red.600" fontWeight="bold" mt={2}>Component Stack:</Text>
                                    <Code display="block" whiteSpace="pre-wrap" p={2} fontSize="xs">
                                        {errorInfo.componentStack}
                                    </Code>
                                </>
                            )}
                        </Box>
                    )}

                    <Stack direction="row" spacing={4}>
                        <Button
                            onClick={() => window.location.reload()}
                            colorScheme="blue"
                        >
                            Refresh Page
                        </Button>
                        <Button
                            onClick={resetError}
                            variant="outline"
                        >
                            Try Again
                        </Button>
                    </Stack>
                </Stack>
            </Box>
        </Container>
    );
};

export default ErrorBoundary;
