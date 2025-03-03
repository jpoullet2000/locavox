import React from 'react';
import {
    Box,
    Flex,
    HStack,
    IconButton,
    Button,
    Menu,
    MenuButton,
    MenuList,
    MenuItem,
    MenuDivider,
    useDisclosure,
    useColorModeValue,
    Stack,
    Text,
} from '@chakra-ui/react';
import { HamburgerIcon, CloseIcon } from '@chakra-ui/icons';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

interface NavLinkProps {
    children: React.ReactNode;
    href: string;
}

const NavLink = ({ children, href }: NavLinkProps) => (
    <Box
        as={Link}
        px={2}
        py={1}
        rounded={'md'}
        _hover={{
            textDecoration: 'none',
            bg: useColorModeValue('gray.200', 'gray.700'),
        }}
        to={href}
    >
        {children}
    </Box>
);

export default function Navbar() {
    const { isOpen, onOpen, onClose } = useDisclosure();
    const { isAuthenticated, user, logout } = useAuth();
    const navigate = useNavigate();

    const handleLogout = () => {
        logout();
        navigate('/');
    };

    return (
        <Box bg={useColorModeValue('white', 'gray.800')} px={4} boxShadow={'sm'}>
            <Flex h={16} alignItems={'center'} justifyContent={'space-between'}>
                <IconButton
                    size={'md'}
                    icon={isOpen ? <CloseIcon /> : <HamburgerIcon />}
                    aria-label={'Open Menu'}
                    display={{ md: 'none' }}
                    onClick={isOpen ? onClose : onOpen}
                />
                <HStack spacing={8} alignItems={'center'}>
                    <Box fontWeight="bold" fontSize="xl">
                        <Link to="/">LocaVox</Link>
                    </Box>
                    <HStack as={'nav'} spacing={4} display={{ base: 'none', md: 'flex' }}>
                        <NavLink href="/">Home</NavLink>
                        {isAuthenticated ? (
                            <>
                                <NavLink href="/dashboard">Dashboard</NavLink>
                                <NavLink href="/topics">Topics</NavLink>
                                <NavLink href="/post-message">Post Message</NavLink>
                            </>
                        ) : (
                            <NavLink href="/login">Login</NavLink>
                        )}
                    </HStack>
                </HStack>
                <Flex alignItems={'center'}>
                    {isAuthenticated ? (
                        <Menu>
                            <MenuButton
                                as={Button}
                                rounded={'full'}
                                variant={'link'}
                                cursor={'pointer'}
                                minW={0}
                            >
                                {user?.username || 'User'}
                            </MenuButton>
                            <MenuList>
                                <MenuItem as={Link} to="/my-messages">My Messages</MenuItem>
                                <MenuItem as={Link} to="/profile">Profile</MenuItem>
                                <MenuDivider />
                                <MenuItem onClick={handleLogout}>Sign Out</MenuItem>
                            </MenuList>
                        </Menu>
                    ) : (
                        <Button as={Link} to="/login" colorScheme="blue" size="sm">
                            Sign In
                        </Button>
                    )}
                </Flex>
            </Flex>

            {isOpen ? (
                <Box pb={4} display={{ md: 'none' }}>
                    <Stack as={'nav'} spacing={4}>
                        <NavLink href="/">Home</NavLink>
                        {isAuthenticated ? (
                            <>
                                <NavLink href="/dashboard">Dashboard</NavLink>
                                <NavLink href="/topics">Topics</NavLink>
                                <NavLink href="/post-message">Post Message</NavLink>
                                <NavLink href="/my-messages">My Messages</NavLink>
                            </>
                        ) : (
                            <>
                                <NavLink href="/login">Login</NavLink>
                                <NavLink href="/register">Register</NavLink>
                            </>
                        )}
                    </Stack>
                </Box>
            ) : null}
        </Box>
    );
}
