import React, { useState } from 'react';
import { sendMessage } from '../services/api';
import './TextInput.css';

export const TextInput: React.FC = () => {
    const [text, setText] = useState('');
    const [response, setResponse] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        try {
            const backendResponse = await sendMessage(text);
            setResponse(backendResponse);
        } catch (error) {
            console.error('Error:', error);
            setResponse('Error communicating with the server');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="text-input-container">
            <form onSubmit={handleSubmit} className="text-input-form">
                <label htmlFor="messageInput" className="input-label">
                    Your Message:
                </label>
                <textarea
                    id="messageInput"
                    value={text}
                    onChange={(e) => setText(e.target.value)}
                    placeholder="Type your message here..."
                    rows={6}
                    className="text-area"
                    disabled={isLoading}
                />
                <button type="submit" className="submit-button" disabled={isLoading}>
                    {isLoading ? 'Processing...' : 'Submit'}
                </button>
            </form>
            {response && (
                <div className="response-container">
                    <h3>AI Response:</h3>
                    <p>{response}</p>
                </div>
            )}
        </div>
    );
};
