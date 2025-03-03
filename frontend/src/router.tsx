import { createBrowserRouter, Navigate } from 'react-router-dom';
import RootLayout from './layouts/RootLayout';
import Home from './pages/Home';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import NotFound from './pages/NotFound';
import MyMessages from './pages/MyMessages';
import PostMessage from './pages/PostMessage';
import TopicList from './pages/TopicList';
import ProtectedRoute from './components/ProtectedRoute';
import ErrorBoundary from './components/ErrorBoundary';
// Import the debug component
import TopicRouteDebug from './components/TopicRouteDebug';

// Add console logging for route navigation
const logRouteChange = (path: string) => {
    console.log(`Navigating to path: ${path}`);
    return null;
};

export const router = createBrowserRouter([
    {
        path: '/',
        element: <RootLayout />,
        errorElement: <ErrorBoundary />,
        children: [
            {
                index: true,
                element: <Home />,
                loader: () => logRouteChange('/'),
            },
            {
                path: 'login',
                element: <Login />,
            },
            {
                path: 'register',
                element: <Register />,
            },
            {
                path: 'dashboard',
                element: <ProtectedRoute><Dashboard /></ProtectedRoute>,
            },
            {
                path: 'post-message',
                element: <ProtectedRoute><PostMessage /></ProtectedRoute>,
            },
            {
                path: 'my-messages',
                element: <ProtectedRoute><MyMessages /></ProtectedRoute>,
            },
            {
                path: 'topics',
                // Add the debug component and use TopicList (not protected for now to rule out auth issues)
                element: <>
                    <TopicRouteDebug />
                    <TopicList />
                </>,
                loader: () => logRouteChange('/topics'),
            },
            {
                path: '*',
                element: <NotFound />,
            },
        ],
    },
]);
