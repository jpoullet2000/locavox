import React from 'react';
import {
    Box,
    Flex,
    Text,
    Button,
    Stack,
    Link,
    useColorModeValue,
    useDisclosure,
    IconButton,
    HStack,
    Menu,
    MenuButton,
    MenuList,
    MenuItem,
    MenuDivider,
    useColorMode,
    Icon,
    Avatar,
} from '@chakra-ui/react';
import { HamburgerIcon, CloseIcon, MoonIcon, SunIcon, ChatIcon, AddIcon } from '@chakra-ui/icons';
import { Link as RouterLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

// Desktop Navigation Links - Define this outside the main component
const DesktopNav = ({ user }: { user: any }) => {
    const linkColor = useColorModeValue('gray.600', 'gray.200');
    const linkHoverColor = useColorModeValue('gray.800', 'white');

    return (
        <Stack direction={'row'} spacing={4}>
            <Link
                as={RouterLink}
                to="/"
                p={2}
                fontSize={'sm'}
                fontWeight={500}
                color={linkColor}
                _hover={{
                    textDecoration: 'none',
                    color: linkHoverColor,
                }}>
                Home
            </Link>
            {user && (
                <>
                    <Link
                        as={RouterLink}
                        to="/dashboard"
                        p={2}
                        fontSize={'sm'}
                        fontWeight={500}
                        color={linkColor}
                        _hover={{
                            textDecoration: 'none',
                            color: linkHoverColor,
                        }}>
                        Dashboard
                    </Link>
                    <Link
                        as={RouterLink}
                        to="/my-messages"
                        p={2}
                        fontSize={'sm'}
                        fontWeight={500}
                        color={linkColor}
                        _hover={{
                            textDecoration: 'none',
                            color: linkHoverColor,
                        }}>
                        My Messages
                    </Link>
                </>
            )}
            <Link
                as={RouterLink}
                to="/about"
                p={2}
                fontSize={'sm'}
                fontWeight={500}
                color={linkColor}
                _hover={{
                    textDecoration: 'none',
                    color: linkHoverColor,
                }}>
                About
            </Link>
        </Stack>
    );
};

// Mobile Navigation Item
const MobileNavItem = ({ label, to }: { label: string; to: string }) => {
    return (
        <Stack spacing={4}>
            <Link
                as={RouterLink}
                to={to}
                py={2}
                justify={'space-between'}
                align={'center'}
                _hover={{
                    textDecoration: 'none',
                }}>
                <Text
                    fontWeight={600}
                    color={useColorModeValue('gray.600', 'gray.200')}>
                    {label}
                </Text>
            </Link>
        </Stack>
    );
};

const Nav: React.FC = () => {
    const { isOpen, onToggle } = useDisclosure();
    const { colorMode, toggleColorMode } = useColorMode();
    const { user, logout } = useAuth();
    const navigate = useNavigate();

    // Function to handle logout
    const handleLogout = async () => {
        try {
            await logout();
            navigate('/');
        } catch (error) {
            console.error('Logout failed:', error);
        }
    };

    // Mobile Navigation
    const MobileNav = () => {
        return (
            <Stack
                bg={useColorModeValue('white', 'gray.800')}
                p={4}
                display={{ md: 'none' }}>
                <MobileNavItem label="Home" to="/" />
                {user && (
                    <>
                        <MobileNavItem label="Dashboard" to="/dashboard" />
                        <MobileNavItem label="My Messages" to="/my-messages" />
                    </>
                )}
                <MobileNavItem label="About" to="/about" />
            </Stack>
        );
    };

    // User Menu Component
    const UserMenu = () => {
        return (
            <Menu>
                <MenuButton
                    as={Button}
                    rounded={'full'}
                    variant={'link'}
                    cursor={'pointer'}
                    minW={0}>
                    <Avatar
                        size={'sm'}
                        name={user?.displayName || user?.email || 'User'}
                        src={user?.photoURL || ''}
                    />
                </MenuButton>
                <MenuList>
                    <MenuItem as={RouterLink} to="/dashboard">Dashboard</MenuItem>
                    <MenuItem as={RouterLink} to="/post-message" icon={<Icon as={AddIcon} />}>
                        Post Message
                    </MenuItem>
                    <MenuItem as={RouterLink} to="/my-messages" icon={<Icon as={ChatIcon} />}>
                        My Messages
                    </MenuItem>
                    <MenuDivider />
                    <MenuItem onClick={handleLogout}>Log out</MenuItem>
                </MenuList>
            </Menu>
        );
    };

    return (
        <Box>
            <Flex
                bg={useColorModeValue('white', 'gray.800')}
                color={useColorModeValue('gray.600', 'white')}
                minH={'60px'}
                py={{ base: 2 }}
                px={{ base: 4 }}
                borderBottom={1}
                borderStyle={'solid'}
                borderColor={useColorModeValue('gray.200', 'gray.900')}
                align={'center'}>
                <Flex
                    flex={{ base: 1, md: 'auto' }}
                    ml={{ base: -2 }}
                    display={{ base: 'flex', md: 'none' }}>
                    <IconButton
                        onClick={onToggle}
                        icon={
                            isOpen ? <CloseIcon w={3} h={3} /> : <HamburgerIcon w={5} h={5} />
                        }
                        variant={'ghost'}
                        aria-label={'Toggle Navigation'}
                    />
                </Flex>
                <Flex flex={{ base: 1 }} justify={{ base: 'center', md: 'start' }}>
                    <Text
                        as={RouterLink}
                        to="/"
                        textAlign={useColorModeValue('left', 'center')}
                        fontFamily={'heading'}
                        fontWeight={'bold'}
                        color={useColorModeValue('gray.800', 'white')}>
                        LocaVox
                    </Text>

                    <Flex display={{ base: 'none', md: 'flex' }} ml={10}>
                        {/* Pass the user prop to DesktopNav */}
                        <DesktopNav user={user} />
                    </Flex>
                </Flex>

                <Stack
                    flex={{ base: 1, md: 0 }}
                    justify={'flex-end'}
                    direction={'row'}
                    spacing={6}>
                    <Button onClick={toggleColorMode}>
                        {colorMode === 'light' ? <MoonIcon /> : <SunIcon />}
                    </Button>

                    {user ? (
                        <UserMenu />
                    ) : (
                        <>
                            <Button
                                as={RouterLink}
                                to="/login"
                                fontSize={'sm'}
                                fontWeight={400}
                                variant={'link'}>
                                Sign In
                            </Button>
                            <Button
                                as={RouterLink}
                                to="/register"
                                display={{ base: 'none', md: 'inline-flex' }}
                                fontSize={'sm'}
                                fontWeight={600}
                                color={'white'}
                                bg={'blue.400'}
                                _hover={{
                                    bg: 'blue.300',
                                }}>
                                Sign Up
                            </Button>
                        </>
                    )}
                </Stack>
            </Flex>

            <Flex
                display={{ base: isOpen ? 'block' : 'none', md: 'none' }}>
                <MobileNav />
            </Flex>
        </Box>
    );
};

export default Nav;
