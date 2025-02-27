const API_BASE_URL = 'http://localhost:8000';

export async function sendMessage(text: string): Promise<string> {
    try {
        const defaultTopic = 'chat'; // Using 'chat' as the default topic
        const response = await fetch(`${API_BASE_URL}/topics/${defaultTopic}/messages`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                userId: 'anonymous', // You might want to make this configurable
                content: text,
                metadata: {} // Optional metadata
            }),
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const data = await response.json();
        return data.content; // The backend returns the complete message object
    } catch (error) {
        console.error('Error calling backend:', error);
        throw error;
    }
}
