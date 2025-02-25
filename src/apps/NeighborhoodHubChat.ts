import { Topic, Message } from '../core/Topic';

export class NeighborhoodHubChat extends Topic {
    constructor() {
        super(
            'Neighborhood Hub Chat',
            'General neighborhood discussion and casual conversations'
        );
    }

    postMessage(userId: string, content: string): void {
        this.addMessage({
            id: crypto.randomUUID(),
            userId,
            content,
            timestamp: new Date(),
            metadata: {
                type: 'chat'
            }
        });
    }
}
