"""Common utilities for the Zooniverse Mobile App."""

__all__ = ("get_hash_id", "make_id_str")

import hashlib

import numpy as np
import polars as pl
from plum import dispatch


def get_hash_id(subject_id: str, /, *, extra_key: str) -> str:
    """Generate a hash ID for a subject.

    This function combines the subject ID with an extra key to ensure uniqueness
    and returns a SHA-256 hash of the combined string as a hexadecimal digest.

    Notes:
    For Euclid a good subject ID is "Q{N}_R{N}_{tile_index}_{object_id}".

    Args:
        subject_id: The subject ID to hash.
        extra_key: An additional key to ensure uniqueness.

    Returns:
        The hexadecimal digest of the hash of the subject ID and extra key.

    """
    # Combine the subject ID with an extra key to ensure uniqueness
    str_to_hash = subject_id + extra_key
    # Create a SHA-256 hash of the combined string
    hash_str = hashlib.sha256(str_to_hash.encode())
    # Return the hexadecimal digest of the hash
    return hash_str.hexdigest()


# ===================================================================
# ID string generation


@dispatch
def make_id_str(
    tile_index: int | str, object_id: str, release_name: str | None = None, /
) -> str:
    """Generate a unique identifier string for a subject.

    Args:
        release_name: The release name of the subject. Ignored if `None`.
        tile_index: The tile index of the subject.
        object_id: The object ID of the subject.

    Returns:
        A unique identifier string for the subject.

    Examples:
    >>> make_id_str(12345, "abc-123", "Q1_R1")
    "Q1_R1_12345_abc-123"

    >>> make_id_str(12345, "abc-123")
    "12345_abc-123"

    """
    # Create the prefix based on the release name
    prefix = f"{release_name}_" if release_name is not None else ""
    # Replace hyphens in the object ID with 'NEG' and convert to string
    obj_id = np.char.replace(object_id, "-", "NEG")
    # Combine release name, tile index, and object ID to create a unique identifier
    return prefix + f"{tile_index}_{obj_id}"


@dispatch
def make_id_str(df: pl.DataFrame, /, *, include_release_name: bool = True) -> pl.Series:
    """Generate a unique identifier string for each row in the DataFrame.

    Args:
        df: The DataFrame containing the necessary columns.
        include_release_name: Whether to include the release name in the ID.

    Returns:
        A Series of unique identifier strings for each row in the DataFrame.

    """
    # Create the prefix expression based on whether to include the release name
    prefix_expr = (
        (pl.col("release_name").cast(str) + "_") if include_release_name else pl.lit("")
    )

    # Create the full ID expression
    id_expr = (
        prefix_expr
        + pl.col("tile_index").cast(pl.Int64).cast(str)
        + "_"
        + pl.col("object_id").cast(str).str.replace("-", "NEG")
    )

    # Evaluate the expression on the DataFrame and return as Series
    # Note that this does NOT modify the original DataFrame
    return df.select(id_expr.alias("unique_id")).get_column("unique_id")
