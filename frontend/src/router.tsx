import {
    createBrowserRouter,
    createRoutesFromElements,
    Route,
    Outlet,
    RouterProvider as BaseRouterProvider,
    RouterProviderProps
} from 'react-router-dom';
import Home from './pages/Home';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import TopicView from './pages/TopicView';
import PostMessage from './pages/PostMessage';
import MyMessages from './pages/MyMessages';
import About from './pages/About';
import ProtectedRoute from './components/ProtectedRoute';
import Nav from './components/Nav';
import Footer from './components/Footer';
import ErrorBoundary from './components/ErrorBoundary';
import FutureCompatibleWrapper from './components/FutureCompatibleWrapper';
import { Box } from '@chakra-ui/react';
import React, { startTransition } from 'react';

// Root layout component that includes Nav and Footer
const RootLayout = () => {
    return (
        <Box display="flex" flexDirection="column" minHeight="100vh">
            <ErrorBoundary componentName="Nav">
                <Nav />
            </ErrorBoundary>

            <Box flexGrow={1} py={4} px={4}>
                <FutureCompatibleWrapper>
                    <Outlet />
                </FutureCompatibleWrapper>
            </Box>

            <ErrorBoundary componentName="Footer">
                <Footer />
            </ErrorBoundary>
        </Box>
    );
};

// Custom RouterProvider that ensures future flags are set consistently
const RouterProvider: React.FC<RouterProviderProps> = ({ router, ...rest }) => {
    // Updated future flags to include v7_relativeSplatPath
    const futureFlags = {
        v7_startTransition: true,
        v7_relativeSplatPath: true,
        // Add any other future flags here
    };

    // We need to explicitly define the future flags here
    const routerWithFutureFlags = {
        ...router,
        future: {
            ...router.future,
            ...futureFlags
        },
    };

    console.log('Creating RouterProvider with future flags:', routerWithFutureFlags.future);

    return (
        <BaseRouterProvider
            router={routerWithFutureFlags}
            future={futureFlags}
            {...rest}
        />
    );
};

// Create routes
const routes = (
    <Route element={<RootLayout />}>
        <Route
            path="/"
            element={
                <ErrorBoundary componentName="Home">
                    <Home />
                </ErrorBoundary>
            }
        />
        <Route
            path="/login"
            element={
                <ErrorBoundary componentName="Login">
                    <Login />
                </ErrorBoundary>
            }
        />
        <Route
            path="/register"
            element={
                <ErrorBoundary componentName="Register">
                    <Register />
                </ErrorBoundary>
            }
        />
        <Route
            path="/dashboard"
            element={
                <ProtectedRoute>
                    <ErrorBoundary componentName="Dashboard">
                        <Dashboard />
                    </ErrorBoundary>
                </ProtectedRoute>
            }
        />
        <Route
            path="/topics/:topicName"
            element={
                <ProtectedRoute>
                    <ErrorBoundary componentName="TopicView">
                        <TopicView />
                    </ErrorBoundary>
                </ProtectedRoute>
            }
        />
        <Route
            path="/post-message"
            element={
                <ProtectedRoute>
                    <ErrorBoundary componentName="PostMessage">
                        <PostMessage />
                    </ErrorBoundary>
                </ProtectedRoute>
            }
        />
        <Route
            path="/my-messages"
            element={
                <ProtectedRoute>
                    <ErrorBoundary componentName="MyMessages">
                        <MyMessages />
                    </ErrorBoundary>
                </ProtectedRoute>
            }
        />
        <Route
            path="/about"
            element={
                <ErrorBoundary componentName="About">
                    <About />
                </ErrorBoundary>
            }
        />
    </Route>
);

// Create router with future flags properly configured
export const router = createBrowserRouter(
    createRoutesFromElements(routes),
    {
        future: {
            v7_startTransition: true,
            v7_relativeSplatPath: true
        }
    }
);

// Export the enhanced RouterProvider
export { RouterProvider };
