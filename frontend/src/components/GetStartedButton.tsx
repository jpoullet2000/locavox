import React from 'react';
import { Button, ButtonProps } from '@chakra-ui/react';
import { Link as RouterLink, useNavigate } from 'react-router-dom';

interface GetStartedButtonProps extends ButtonProps {
    useNavigate?: boolean;
}

const GetStartedButton: React.FC<GetStartedButtonProps> = ({
    useNavigateHook = false,
    children = "Get Started",
    ...rest
}) => {
    const navigate = useNavigate();

    const handleClick = () => {
        console.log('GetStartedButton clicked, navigating to /topics');
        navigate('/topics');
    };

    if (useNavigateHook) {
        return (
            <Button
                colorScheme="primary"
                size="lg"
                onClick={handleClick}
                {...rest}
            >
                {children}
            </Button>
        );
    }

    return (
        <Button
            as={RouterLink}
            to="/topics"
            colorScheme="primary"
            size="lg"
            onClick={() => console.log('GetStartedButton clicked (RouterLink), navigating to /topics')}
            {...rest}
        >
            {children}
        </Button>
    );
};

export default GetStartedButton;
