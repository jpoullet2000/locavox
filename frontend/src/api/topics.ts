import { Message, TopicResponse } from '../types/Topic';

const API_BASE = 'http://localhost:8000';

export async function queryTopics(query: string): Promise<TopicResponse | null> {
    const response = await fetch(`${API_BASE}/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query })
    });
    return response.ok ? response.json() : null;
}

export async function postMessage(
    topicName: string,
    userId: string,
    content: string,
    metadata?: Record<string, any>
): Promise<Message | null> {
    const response = await fetch(`${API_BASE}/topics/${topicName}/messages`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ userId, content, metadata })
    });
    return response.ok ? response.json() : null;
}
