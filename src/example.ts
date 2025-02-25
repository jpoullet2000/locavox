import { TopicManager } from './core/TopicManager';
import { CommunityTaskMarketplace } from './apps/CommunityTaskMarketplace';
import { NeighborhoodHubChat } from './apps/NeighborhoodHubChat';

async function main() {
    // Initialize the framework
    const topicManager = new TopicManager();

    // Create and register applications
    const marketplace = new CommunityTaskMarketplace();
    const neighborhoodChat = new NeighborhoodHubChat();

    topicManager.registerTopic(marketplace);
    topicManager.registerTopic(neighborhoodChat);

    // Add some sample messages
    marketplace.addTaskOffer(
        'user1',
        'ladder',
        'Available to borrow this weekend'
    );

    neighborhoodChat.postMessage(
        'user2',
        'Beautiful weather today!'
    );

    // Example query
    const query = 'could you tell me whether someone is lending his ladder';
    const result = await topicManager.findRelevantTopicAndMessages(query);

    if (result) {
        console.log(`Found in topic: ${result.topic.getName()}`);
        console.log('Relevant messages:', result.messages);
        console.log('Would you like to send a private message to the lender?');
    } else {
        console.log('No relevant messages found.');
    }
}

main().catch(console.error);
