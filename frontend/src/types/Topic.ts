export interface Message {
    id: string;
    content: string;
    userId: string;
    timestamp: string;
    metadata?: Record<string, any>;
}

export interface Topic {
    name: string;
    description: string;
    messages: Message[];
}

export interface TopicResponse {
    topic: Topic;
    messages: Message[];
}
