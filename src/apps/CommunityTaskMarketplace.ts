import { Topic, Message } from '../core/Topic';

export class CommunityTaskMarketplace extends Topic {
    constructor() {
        super(
            'Community Task Marketplace',
            'A place to share and request community resources and help'
        );
    }

    addTaskOffer(userId: string, item: string, details: string): void {
        this.addMessage({
            id: crypto.randomUUID(),
            userId,
            content: `Offering: ${item} - ${details}`,
            timestamp: new Date(),
            metadata: {
                type: 'offer',
                item
            }
        });
    }

    addTaskRequest(userId: string, item: string, details: string): void {
        this.addMessage({
            id: crypto.randomUUID(),
            userId,
            content: `Looking for: ${item} - ${details}`,
            timestamp: new Date(),
            metadata: {
                type: 'request',
                item
            }
        });
    }
}
