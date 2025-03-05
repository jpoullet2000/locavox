import lance
import os
from typing import List, Any
from locavox.logger import setup_logger
import re

logger = setup_logger("locavox.lance_query_builder")


class LanceQueryBuilder:
    """Base class for building and executing Lance queries"""

    def __init__(self, dataset_uri: str):
        """
        Initialize with a Lance dataset URI

        Args:
            dataset_uri: Path to the Lance dataset
        """
        self.dataset_uri = dataset_uri
        self.dataset = None
        self._connect_to_dataset()

    def _connect_to_dataset(self):
        """Connect to the Lance dataset"""
        try:
            # Verify the path exists
            if not os.path.exists(self.dataset_uri):
                logger.error(f"Dataset path does not exist: {self.dataset_uri}")
                # Try to resolve relative paths
                abs_path = os.path.abspath(self.dataset_uri)
                logger.debug(f"Trying absolute path: {abs_path}")
                if os.path.exists(abs_path):
                    self.dataset_uri = abs_path
                    logger.info(f"Using resolved absolute path: {abs_path}")
                else:
                    # Try to find the common lance file extension
                    if not self.dataset_uri.endswith(".lance"):
                        with_ext = f"{self.dataset_uri}.lance"
                        if os.path.exists(with_ext):
                            self.dataset_uri = with_ext
                            logger.info(f"Using path with .lance extension: {with_ext}")
                        else:
                            logger.error(
                                f"Could not find dataset at: {self.dataset_uri}"
                            )
                            self.dataset = None
                            return

            # Use the correct API based on what's available
            try:
                # Try the newer API (lance 0.3+)
                self.dataset = lance.dataset(self.dataset_uri)
                logger.debug(
                    f"Connected to dataset using lance.dataset() at {self.dataset_uri}"
                )
            except (AttributeError, ImportError) as e:
                logger.warning(
                    f"Could not use lance.dataset(): {e}, trying alternate API"
                )
                # Try an alternate API if available
                try:
                    import lancedb

                    db = lancedb.connect(os.path.dirname(self.dataset_uri))
                    table_name = os.path.basename(self.dataset_uri).replace(
                        ".lance", ""
                    )
                    self.dataset = db.open_table(table_name)
                    logger.debug(
                        f"Connected to dataset using lancedb at {self.dataset_uri}"
                    )
                except Exception as e2:
                    logger.error(f"All connection attempts failed: {e2}")
                    self.dataset = None
                    return

            # Verify the connection
            if not self.dataset:
                logger.error("Dataset connection is None after connection attempt")
            else:
                # Validate the dataset by checking if we can access schema or scanner
                try:
                    # Try to get a scanner to validate the connection
                    scanner = self.dataset.scanner()
                    logger.debug(
                        f"Dataset connection validated. Scanner available: {scanner}"
                    )
                except Exception as e:
                    logger.error(f"Dataset connection validation failed: {e}")
                    self.dataset = None
                    return

        except Exception as e:
            logger.error(
                f"Failed to connect to Lance dataset at {self.dataset_uri}: {e}"
            )
            # Print more details for debugging
            import traceback

            logger.debug(f"Connection error details: {traceback.format_exc()}")
            self.dataset = None

    def execute(self):
        """
        Execute the query - base implementation returns an empty result

        Returns:
            Empty list as default implementation
        """
        logger.warning("Base execute method called, no implementation provided")
        return []


class LanceEmptyQueryBuilder(LanceQueryBuilder):
    """Empty query builder for Lance datasets that supports where conditions"""

    def __init__(self, dataset_uri: str):
        """Initialize with dataset URI"""
        super().__init__(dataset_uri)
        self.conditions = {}

    def where(self, field: str, value: Any):
        """
        Add a where condition to filter results

        Args:
            field: Field name to filter on
            value: Value to filter for

        Returns:
            self for method chaining
        """
        self.conditions[field] = value
        return self

    def execute(self):
        """
        Execute the query with the specified conditions

        Returns:
            List of results matching the query conditions
        """
        if not self.dataset:
            logger.warning("No dataset connection available")
            # Try reconnecting once before giving up
            logger.info(f"Attempting to reconnect to {self.dataset_uri}")
            self._connect_to_dataset()
            if not self.dataset:
                logger.error(
                    f"Reconnection failed, cannot execute query on {self.dataset_uri}"
                )
                return []

        try:
            # Get a scanner from the dataset
            scanner = self.dataset.scanner()

            # Log available methods for debugging
            available_methods = [
                method for method in dir(scanner) if not method.startswith("_")
            ]
            logger.debug(f"Scanner has methods: {available_methods}")

            # Get all data as a table and convert to pandas for filtering
            table = scanner.to_table()
            df = table.to_pandas()
            logger.debug(f"Retrieved DataFrame with {len(df)} rows")

            # Apply filtering in Python
            if self.conditions:
                for field, value in self.conditions.items():
                    logger.debug(f"Filtering on {field} = {value}")
                    if field not in df.columns:
                        logger.warning(
                            f"Field {field} not found in dataset. Available columns: {df.columns.tolist()}"
                        )
                        continue

                    if isinstance(value, str):
                        df = df[df[field] == value]
                    else:
                        df = df[df[field] == value]

                logger.debug(f"After filtering, {len(df)} rows remain")

            result = df.to_dict("records")
            logger.debug(f"Query executed successfully, returned {len(result)} records")
            return result

        except Exception as e:
            logger.warning(f"Lance query execution failed: {str(e)}")
            logger.debug(f"Dataset URI: {self.dataset_uri}")
            # Return empty list on failure
            return []


class LanceComplexQueryBuilder(LanceQueryBuilder):
    """More advanced query builder for Lance datasets with additional capabilities"""

    def __init__(self, dataset_uri: str):
        """Initialize with dataset URI"""
        super().__init__(dataset_uri)
        self.filter_expressions = []
        self.limit_val = None
        self.offset_val = None
        self.select_fields = None
        self.order_by_clauses = []

    def where(self, expression: str):
        """Add a where condition using SQL-like expression"""
        self.filter_expressions.append(expression)
        return self

    def limit(self, count: int):
        """Limit the number of results"""
        self.limit_val = count
        return self

    def offset(self, count: int):
        """Offset the results"""
        self.offset_val = count
        return self

    def select(self, fields: List[str]):
        """Select specific fields"""
        self.select_fields = fields
        return self

    def order_by(self, field: str, descending: bool = False):
        """Order results by field"""
        direction = "DESC" if descending else "ASC"
        self.order_by_clauses.append(f"{field} {direction}")
        return self

    def _parse_simple_expression(self, expression, df):
        """Parse a simple expression and apply it to the dataframe"""
        try:
            # Simple equality expression: "field = value"
            equality_match = re.match(r"([^\s=<>]+)\s*=\s*(.+)", expression)
            if equality_match:
                field, value = equality_match.groups()
                field = field.strip("\"'")

                # Handle quoted string values
                if (value.startswith("'") and value.endswith("'")) or (
                    value.startswith('"') and value.endswith('"')
                ):
                    value = value[1:-1]  # Remove quotes
                    return df[df[field] == value]
                else:
                    # Try to convert to numeric if possible
                    try:
                        numeric_value = float(value)
                        return df[df[field] == numeric_value]
                    except ValueError:
                        return df[df[field] == value]

            # Greater than expression: "field > value"
            gt_match = re.match(r"([^\s=<>]+)\s*>\s*(.+)", expression)
            if gt_match:
                field, value = gt_match.groups()
                field = field.strip("\"'")
                try:
                    numeric_value = float(value)
                    return df[df[field] > numeric_value]
                except ValueError:
                    logger.warning(
                        f"Cannot apply > operator to non-numeric value: {value}"
                    )
                    return df

            # Less than expression: "field < value"
            lt_match = re.match(r"([^\s=<>]+)\s*<\s*(.+)", expression)
            if lt_match:
                field, value = lt_match.groups()
                field = field.strip("\"'")
                try:
                    numeric_value = float(value)
                    return df[df[field] < numeric_value]
                except ValueError:
                    logger.warning(
                        f"Cannot apply < operator to non-numeric value: {value}"
                    )
                    return df

            # Default: return unchanged dataframe
            logger.warning(f"Could not parse expression: {expression}")
            return df
        except Exception as e:
            logger.error(f"Error parsing expression '{expression}': {e}")
            return df

    def execute(self):
        """Execute the complex query using available methods"""
        if not self.dataset:
            logger.warning("No dataset connection available")
            return []

        try:
            # Start with a base scanner
            scanner = self.dataset.scanner()

            # Get available methods
            available_methods = [
                method for method in dir(scanner) if not method.startswith("_")
            ]
            logger.debug(f"Available methods: {available_methods}")

            # Apply projection if supported and fields are specified
            if self.select_fields and "projected_schema" in available_methods:
                try:
                    # This doesn't actually project yet, just checks if we could
                    projected_schema = scanner.projected_schema(self.select_fields)
                    logger.debug(
                        f"Projection validated with schema: {projected_schema}"
                    )
                except Exception as e:
                    logger.warning(f"Projection validation failed: {e}")
                    self.select_fields = None

            # Get all data as a table and convert to pandas for operations
            result_df = scanner.to_table().to_pandas()
            logger.debug(f"Retrieved {len(result_df)} rows from dataset")

            # Apply filtering in Python
            if self.filter_expressions:
                for expression in self.filter_expressions:
                    result_df = self._parse_simple_expression(expression, result_df)
                logger.debug(f"After filtering, {len(result_df)} rows remain")

            # Apply ordering
            if self.order_by_clauses:
                for clause in self.order_by_clauses:
                    parts = clause.split()
                    if len(parts) == 2:
                        field, direction = parts
                        ascending = direction.upper() != "DESC"
                        result_df = result_df.sort_values(field, ascending=ascending)
                logger.debug(
                    f"Applied ordering with {len(self.order_by_clauses)} clauses"
                )

            # Apply offset
            if self.offset_val is not None:
                result_df = result_df.iloc[self.offset_val :]
                logger.debug(f"Applied offset {self.offset_val}")

            # Apply limit
            if self.limit_val is not None:
                result_df = result_df.head(self.limit_val)
                logger.debug(f"Applied limit {self.limit_val}")

            # Apply projection last (select only specified columns)
            if self.select_fields:
                # Filter to only columns that actually exist
                valid_cols = [
                    col for col in self.select_fields if col in result_df.columns
                ]
                if not valid_cols:
                    logger.warning(
                        f"None of the requested columns {self.select_fields} exist in the dataset"
                    )
                else:
                    result_df = result_df[valid_cols]
                    logger.debug(f"Applied projection to columns: {valid_cols}")

            # Convert to records
            result = result_df.to_dict("records")
            logger.debug(f"Query executed successfully, returned {len(result)} records")
            return result

        except Exception as e:
            logger.warning(f"Complex Lance query execution failed: {str(e)}")
            return []
