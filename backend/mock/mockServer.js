// ...existing code...

// Ensure mockData is properly imported
const mockData = require('./mockData');

// ...existing code...

// Add topics endpoint - make sure this is not inside any conditional blocks
app.get('/topics', (req, res) => {
    console.log('GET /topics - Sending:', mockData.topics);
    res.json(mockData.topics);
});

// Add message posting endpoint
app.post('/topics/:topicName/messages', (req, res) => {
    const { topicName } = req.params;
    const { content, userId, metadata } = req.body;

    console.log(`POST /topics/${topicName}/messages - Received:`, { content, userId, metadata });

    // Create a new message with a generated ID
    const newMessage = {
        id: Date.now().toString(),
        content,
        userId,
        timestamp: new Date().toISOString(),
        metadata: metadata || {}
    };

    // Add the message to our mock database if needed
    // For this example, we're just returning the created message

    res.status(201).json(newMessage);
});

// Add endpoint to retrieve messages from a topic
app.get('/topics/:topicName/messages', (req, res) => {
    const { topicName } = req.params;
    console.log(`GET /topics/${topicName}/messages`);

    // Return empty array or mock data
    res.json([]);
});

// Add endpoint to retrieve messages for a user
app.get('/users/:userId/messages', (req, res) => {
    const { userId } = req.params;
    console.log(`GET /users/${userId}/messages`);

    res.json({
        user_id: userId,
        total: 0,
        messages: []
    });
});

// Add endpoint to delete a specific message
app.delete('/topics/:topicName/messages/:messageId', (req, res) => {
    const { topicName, messageId } = req.params;
    console.log(`DELETE /topics/${topicName}/messages/${messageId}`);

    // In a real implementation, you'd check user permissions here
    // and remove the message from your database

    // For the mock server, we'll just return a success response
    res.status(204).send();
});

// ...existing code...
