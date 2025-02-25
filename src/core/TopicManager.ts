import { Topic, Message } from './Topic';

export class TopicManager {
    private topics: Topic[] = [];

    registerTopic(topic: Topic): void {
        this.topics.push(topic);
    }

    async findRelevantTopicAndMessages(query: string): Promise<{
        topic: Topic;
        messages: Message[];
    } | null> {
        // In a real implementation, this would use an LLM to:
        // 1. Analyze the query
        // 2. Find the most relevant topic
        // 3. Search for matching messages
        // For now, we'll use a simple keyword match
        const keywords = query.toLowerCase().split(' ');

        for (const topic of this.topics) {
            const messages = topic.getMessages().filter(msg =>
                keywords.some(keyword =>
                    msg.content.toLowerCase().includes(keyword)
                )
            );

            if (messages.length > 0) {
                return { topic, messages };
            }
        }

        return null;
    }
}
