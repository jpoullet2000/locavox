import os
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
import asyncio
import json
from . import config
from .logger import setup_logger
from .base_models import Message  # Add this import to fix the NameError

# Set up logger for this module
logger = setup_logger(__name__)

# Don't initialize clients immediately - will be created on-demand if API key is available
client = None
async_client = None


def get_openai_client():
    """Get or create the OpenAI client if API key is available"""
    global client
    if client is None:
        if not config.OPENAI_API_KEY:
            logger.warning("OpenAI API key not set. LLM features will be disabled.")
            return None
        try:
            from openai import OpenAI

            client = OpenAI(api_key=config.OPENAI_API_KEY)
        except ImportError:
            logger.error("OpenAI package not installed. LLM features will be disabled.")
            return None
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            return None
    return client


def get_async_openai_client():
    """Get or create the Async OpenAI client if API key is available"""
    global async_client
    if async_client is None:
        if not config.OPENAI_API_KEY:
            logger.warning("OpenAI API key not set. LLM features will be disabled.")
            return None
        try:
            from openai import AsyncOpenAI

            async_client = AsyncOpenAI(api_key=config.OPENAI_API_KEY)
        except ImportError:
            logger.error("OpenAI package not installed. LLM features will be disabled.")
            return None
        except Exception as e:
            logger.error(f"Failed to initialize AsyncOpenAI client: {e}")
            return None
    return async_client


class SmartSearch:
    """Advanced search functionality with LLM-powered capabilities"""

    @staticmethod
    async def rank_results_with_llm(
        query: str, messages: List[Message], limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Use LLM to rank and explain search results"""
        if not messages:
            return []

        # Get the async client only when needed
        client = get_async_openai_client()
        if client is None:
            # Fallback to basic ranking if LLM is not available
            return [
                {"message": msg, "relevance": 1.0, "explanation": ""}
                for msg in messages[:limit]
            ]

        # Format messages for the LLM
        formatted_messages = []
        for i, msg in enumerate(
            messages[:10]
        ):  # Limit to 10 messages for API context window
            formatted_messages.append(
                f"Message {i + 1}:\n"
                f"Content: {msg.content}\n"
                f"User: {msg.userId}\n"
                f"Metadata: {json.dumps(msg.metadata)}\n"
            )

        messages_text = "\n".join(formatted_messages)

        try:
            completion = await client.chat.completions.create(
                model="gpt-3.5-turbo",
                temperature=0.3,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an intelligent search assistant. Analyze messages and rank them based on relevance to the query. Provide a brief explanation for each message's relevance.",
                    },
                    {
                        "role": "user",
                        "content": f'Query: "{query}"\n\nMessages to analyze:\n{messages_text}\n\nRank the top {min(limit, len(messages))} messages by relevance to the query. For each message, provide the message number and a brief explanation of its relevance.',
                    },
                ],
            )

            ranking_explanation = completion.choices[0].message.content

            # Extract ranked message indices from the explanation
            # This is a simplified implementation - for production, use regex or more robust parsing
            ranked_indices = []
            for i in range(1, len(messages) + 1):
                if f"Message {i}" in ranking_explanation:
                    ranked_indices.append(i - 1)  # Adjust for 0-indexing
                    if len(ranked_indices) >= limit:
                        break

            # Add any remaining messages if we didn't get enough from the parsing
            remaining = [i for i in range(len(messages)) if i not in ranked_indices]
            ranked_indices.extend(remaining[: limit - len(ranked_indices)])

            # Create ranked results with explanations
            ranked_results = []
            for idx in ranked_indices[:limit]:
                explanation = ""
                msg_marker = f"Message {idx + 1}:"
                if msg_marker in ranking_explanation:
                    parts = ranking_explanation.split(msg_marker)[1].split("Message")[0]
                    explanation = parts.strip()

                ranked_results.append(
                    {
                        "message": messages[idx],
                        "relevance": 1.0
                        - (ranked_indices.index(idx) / len(ranked_indices))
                        if ranked_indices
                        else 0,
                        "explanation": explanation,
                    }
                )

            return ranked_results

        except Exception as e:
            logger.error(f"LLM ranking failed: {e}")
            # Fall back to simple ranking if LLM fails
            return [
                {"message": msg, "relevance": 1.0, "explanation": ""}
                for msg in messages[:limit]
            ]

    @staticmethod
    async def classify_topic_fit(
        query: str, topic_name: str, topic_description: str
    ) -> Tuple[float, str]:
        """Determine how well a query fits a given topic"""
        # Get the client only when needed
        client = get_async_openai_client()
        if client is None:
            # Return neutral score if LLM is not available
            return (0.5, "LLM unavailable for topic classification")

        try:
            completion = await client.chat.completions.create(
                model="gpt-3.5-turbo",
                temperature=0.2,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at classifying queries into appropriate topics.",
                    },
                    {
                        "role": "user",
                        "content": f'Topic: {topic_name}\nDescription: {topic_description}\n\nQuery: "{query}"\n\nOn a scale of 0-10, how relevant is this query to the topic? Provide a brief explanation.',
                    },
                ],
            )

            response = completion.choices[0].message.content

            # Extract score - basic implementation, could be more robust
            score = 5.0  # Default middle score
            try:
                for line in response.split("\n"):
                    if any(
                        x in line.lower()
                        for x in ["score", "scale", "rating", "relevance"]
                    ):
                        # Find the first number in the line
                        import re

                        numbers = re.findall(r"\d+(?:\.\d+)?", line)
                        if numbers:
                            score = float(numbers[0])
                            if score > 10:  # Handle cases like "8/10"
                                score = score / 10
                            break
            except (ValueError, IndexError) as e:
                logger.warning(f"Failed to parse score from LLM response: {e}")
                # Keep default score on parsing error

            # Normalize score to 0-1
            normalized_score = min(max(score / 10, 0), 1)

            # Extract explanation
            explanation = response.strip()

            return (normalized_score, explanation)

        except Exception as e:
            logger.error(f"Topic classification failed: {e}")
            return (0.5, "")  # Return neutral score on error

    @staticmethod
    async def get_query_embeddings(query: str):
        """Get embeddings for the query for semantic search"""
        # Use the same embedding generator as the storage class for consistency
        from .embeddings import EmbeddingGenerator

        generator = EmbeddingGenerator()
        return generator.generate(query)

    @staticmethod
    async def search_all_topics(
        query: str, topics: Dict[str, Any], limit: int = 5
    ) -> Dict[str, Any]:
        """Search across all topics with LLM-powered ranking and suggestions"""
        try:
            # First, check if LLM is available
            client = get_async_openai_client()
            use_llm_features = client is not None and config.USE_LLM_BY_DEFAULT

            # Search all topics in parallel
            search_tasks = []
            for name, topic in topics.items():
                search_tasks.append(topic.search_messages(query))

            search_results = await asyncio.gather(*search_tasks)

            # Combine results with topic information
            topic_results = []
            topic_names = list(topics.keys())

            for i, (name, results) in enumerate(zip(topic_names, search_results)):
                if results:
                    # Get topic description
                    description = topics[name].description

                    # Initialize with default values
                    fit_score = 0.5
                    explanation = ""
                    ranked_messages = [
                        {"message": msg, "explanation": ""} for msg in results[:limit]
                    ]

                    # Only call LLM methods if available and enabled
                    if use_llm_features:
                        # Classify topic fit for the query
                        fit_score, explanation = await SmartSearch.classify_topic_fit(
                            query, name, description
                        )

                        # Rank results with LLM
                        ranked_items = await SmartSearch.rank_results_with_llm(
                            query, results, min(limit, len(results))
                        )
                        ranked_messages = ranked_items
                    else:
                        # Basic relevance without LLM
                        ranked_messages = [
                            {"message": msg, "relevance": 1.0, "explanation": ""}
                            for msg in results[:limit]
                        ]

                    topic_results.append(
                        {
                            "topic_name": name,
                            "topic_description": description,
                            "relevance_score": fit_score,
                            "relevance_explanation": explanation,
                            "messages": [item["message"] for item in ranked_messages],
                            "explanations": [
                                item.get("explanation", "") for item in ranked_messages
                            ],
                        }
                    )

            # Sort topics by relevance
            topic_results.sort(key=lambda x: x["relevance_score"], reverse=True)

            # Generate overall response with insights
            if topic_results:
                # Use LLM to generate an overall insight about the query and results
                if use_llm_features:
                    insight = await SmartSearch.generate_query_insight(
                        query, topic_results
                    )
                else:
                    insight = "Search complete. Review the results to find what you're looking for."

                return {
                    "query": query,
                    "topic_results": topic_results,
                    "insight": insight,
                    "total_results": sum(len(t["messages"]) for t in topic_results),
                }
            else:
                return {
                    "query": query,
                    "topic_results": [],
                    "insight": "No matching results found for your query.",
                    "total_results": 0,
                }
        except Exception as e:
            logger.error(f"Error in SmartSearch: {e}")
            raise

    @staticmethod
    async def generate_query_insight(
        query: str, topic_results: List[Dict[str, Any]]
    ) -> str:
        """Generate an insightful overview of search results"""
        if not topic_results:
            return "No results found for your query."

        # Get the client only when needed
        client = get_async_openai_client()
        if client is None:
            return (
                "Search complete. Review the results to find what you're looking for."
            )

        try:
            # Create a summary of the results for the LLM
            summary = (
                f'Query: "{query}"\n\nResults found in {len(topic_results)} topics:\n'
            )

            for t in topic_results:
                summary += f"- {t['topic_name']} (Relevance: {t['relevance_score']:.1f}/1.0): {len(t['messages'])} messages\n"

            completion = await client.chat.completions.create(
                model="gpt-3.5-turbo",
                temperature=0.7,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an insightful search assistant that helps users understand the context and meaning of their search results.",
                    },
                    {
                        "role": "user",
                        "content": f"{summary}\n\nProvide a brief, helpful insight about these search results. What might the user be looking for and how well do the results match their query?",
                    },
                ],
            )

            return completion.choices[0].message.content.strip()

        except Exception as e:
            logger.error(f"Insight generation failed: {e}")
            return (
                "Search complete. Review the results to find what you're looking for."
            )
