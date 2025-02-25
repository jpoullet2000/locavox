export interface Message {
    id: string;
    content: string;
    userId: string;
    timestamp: Date;
    metadata?: Record<string, any>;
}

export class Topic {
    private messages: Message[] = [];
    private name: string;
    private description: string;

    constructor(name: string, description: string) {
        this.name = name;
        this.description = description;
    }

    addMessage(message: Message): void {
        this.messages.push(message);
    }

    getMessages(): Message[] {
        return [...this.messages];
    }

    getName(): string {
        return this.name;
    }

    getDescription(): string {
        return this.description;
    }
}
