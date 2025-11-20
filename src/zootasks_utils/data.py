"""Data access utilities for eggs-zoo-connect."""

import pooch

euclid_q1_morphology = pooch.create(
    path=pooch.os_cache("eggs-zoo-connect"),
    base_url="doi:10.5281/zenodo.15106473",  # Use DOI instead of hardcoding URL
    registry={
        "morphology_catalogue.parquet": "md5:79e7880d5989e05ec23205782c30025a",
    },
)
