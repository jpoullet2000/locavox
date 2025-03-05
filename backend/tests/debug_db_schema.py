#!/usr/bin/env python3

import os
import sys
import lance
import json
from typing import List, Dict, Any
from locavox import config
from locavox.logger import setup_logger

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


logger = setup_logger("debug_db")


def list_topics() -> List[str]:
    """List all available topics in the database"""
    db_path = config.DATABASE_PATH
    if not os.path.exists(db_path):
        logger.warning(f"Database path {db_path} does not exist")
        return []

    topics = []
    for item in os.listdir(db_path):
        full_path = os.path.join(db_path, item)
        if os.path.isdir(full_path):
            topics.append(item)

    return topics


def examine_topic_schema(topic_name: str) -> Dict[str, Any]:
    """Examine the schema of a topic's table"""
    result = {}
    db_path = config.DATABASE_PATH
    topic_path = os.path.join(db_path, topic_name)
    table_path = os.path.join(topic_path, "messages.lance")

    if not os.path.exists(table_path):
        logger.warning(f"Table path {table_path} does not exist")
        return {"error": f"Table not found at {table_path}"}

    try:
        # Open the dataset and get schema
        ds = lance.dataset(table_path)
        schema = ds.schema
        result["schema"] = str(schema)
        result["field_names"] = [field.name for field in schema.fields]

        # Get indices
        indices = ds.list_indices()
        result["indices"] = indices

        # Get sample data
        df = ds.to_pandas(limit=5)
        if len(df) > 0:
            sample_data = []
            for _, row in df.iterrows():
                record = row.to_dict()
                if "metadata" in record and isinstance(record["metadata"], str):
                    try:
                        record["metadata"] = json.loads(record["metadata"])
                    except json.JSONDecodeError:
                        pass
                sample_data.append(record)
            result["sample_data"] = sample_data

        return result
    except Exception as e:
        logger.error(f"Error examining topic schema: {e}")
        return {"error": str(e)}


def main():
    """Main function to debug database schema"""
    topics = list_topics()
    logger.info(f"Found {len(topics)} topics: {topics}")

    for topic in topics:
        logger.info(f"Examining schema for topic: {topic}")
        schema_info = examine_topic_schema(topic)

        if "error" in schema_info:
            logger.error(f"Error for {topic}: {schema_info['error']}")
            continue

        logger.info(f"Schema: {schema_info['schema']}")
        logger.info(f"Fields: {schema_info['field_names']}")

        if "indices" in schema_info:
            logger.info(f"Indices: {json.dumps(schema_info['indices'], indent=2)}")

        if "sample_data" in schema_info:
            logger.info("Sample data:")
            for i, sample in enumerate(schema_info["sample_data"]):
                logger.info(
                    f"Record {i + 1}: {json.dumps(sample, default=str, indent=2)}"
                )

        # Test a query
        try:
            ds = lance.dataset(
                os.path.join(config.DATABASE_PATH, topic, "messages.lance")
            )
            # Try different variations to see what works
            logger.info("Testing different query formats...")

            # Test 1: Standard quoted format
            try:
                _ = ds.to_table(filter="\"userId\" = 'test'", limit=1)
                logger.info("Query 1 succeeded with format: \"userId\" = 'test'")
            except Exception as e1:
                logger.error(f"Query 1 failed: {e1}")

            # Test 2: Alternative quote format
            try:
                _ = ds.to_table(filter='userId = "test"', limit=1)
                logger.info('Query 2 succeeded with format: userId = "test"')
            except Exception as e2:
                logger.error(f"Query 2 failed: {e2}")

            # Test 3: Backtick format
            try:
                _ = ds.to_table(filter='`userId` = "test"', limit=1)
                logger.info('Query 3 succeeded with format: `userId` = "test"')
            except Exception as e3:
                logger.error(f"Query 3 failed: {e3}")

        except Exception as e:
            logger.error(f"Query tests failed: {e}")


if __name__ == "__main__":
    main()
