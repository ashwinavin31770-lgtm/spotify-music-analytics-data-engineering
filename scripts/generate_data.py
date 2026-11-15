#!/usr/bin/env python3
"""Generate reproducible synthetic music analytics datasets in compressed CSV.

These rows are fictional practice data, not Spotify records or real listening metrics.
Writes in batches so a million-track dataset can be generated with bounded memory.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import random
from pathlib import Path
from typing import Iterable

import numpy as np

GENRES = [
    "pop", "rock", "hip-hop", "rap", "electronic", "dance", "indie",
    "alternative", "r&b", "soul", "jazz", "blues", "country", "folk",
    "classical", "metal", "punk", "reggae", "latin", "afrobeat", "k-pop",
    "j-pop", "ambient", "house", "techno", "disco", "funk", "gospel",
    "world", "soundtrack", "acoustic", "lo-fi", "trap", "drum-and-bass",
    "dubstep", "progressive", "singer-songwriter", "opera", "bluegrass",
    "ska", "salsa", "bachata", "reggaeton", "flamenco", "new-age", "trance",
    "garage", "grime", "spoken-word", "experimental",
]
COUNTRIES = ["US", "GB", "IN", "CA", "AU", "BR", "DE", "FR", "JP", "KR", "SE", "NG", "MX", "ES", "IT"]
PREFIXES = ["Midnight", "Golden", "Electric", "Broken", "Summer", "Silent", "Dancing", "Lost", "Blue", "Falling", "Neon", "Wild", "Forever", "Ocean", "Dream", "Shadows", "Higher", "Little", "Crystal", "Running"]
SUFFIXES = ["Hearts", "Lights", "Memories", "Road", "Skies", "Fire", "Rain", "Echoes", "City", "Love", "Motion", "World", "Stories", "Waves", "Again", "Paradise", "Feeling", "Rhythm", "Days", "Night"]

def write_gzip_csv(path: Path, header: list[str], rows: Iterable[list[object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(path, "wt", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(header)
        writer.writerows(rows)

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tracks", type=int, default=1_000_000)
    parser.add_argument("--artists", type=int, default=100_000)
    parser.add_argument("--albums", type=int, default=200_000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--batch-size", type=int, default=25_000)
    parser.add_argument("--output", type=Path, default=Path("data"))
    args = parser.parse_args()

    for name in ("tracks", "artists", "albums", "batch_size"):
        if getattr(args, name) < 1:
            parser.error(f"--{name.replace('_', '-')} must be at least 1")

    rng = np.random.default_rng(args.seed)
    py_rng = random.Random(args.seed)
    output = args.output
    output.mkdir(parents=True, exist_ok=True)

    def artist_rows():
        for i in range(args.artists):
            yield [
                f"ART{i:07d}", f"Artist_{i:06d}", py_rng.choice(COUNTRIES),
                int(rng.integers(100, 50_000_001)),
                int(rng.integers(100, 30_000_001)),
                py_rng.choice(GENRES),
            ]

    write_gzip_csv(
        output / "artists.csv.gz",
        ["artist_id", "artist_name", "country", "followers", "monthly_listeners", "primary_genre"],
        artist_rows(),
    )

    def album_rows():
        for i in range(args.albums):
            date = np.datetime64("1980-01-01") + np.timedelta64(int(rng.integers(0, 16_800)), "D")
            yield [
                f"ALB{i:07d}", f"Album_{i:06d}",
                f"ART{int(rng.integers(0, args.artists)):07d}", str(date),
                py_rng.choice(["album", "single", "compilation", "EP"]),
                int(rng.integers(1, 26)),
            ]

    write_gzip_csv(
        output / "albums.csv.gz",
        ["album_id", "album_name", "artist_id", "release_date", "album_type", "total_tracks"],
        album_rows(),
    )

    track_header = [
        "track_id", "track_name", "artist_id", "artist_name", "album_id", "album_name",
        "release_date", "genre", "popularity", "duration_ms", "danceability", "energy",
        "tempo", "valence", "acousticness", "instrumentalness", "speechiness", "loudness",
    ]
    start = np.datetime64("1980-01-01")
    days = 16_800
    path = output / "tracks.csv.gz"
    with gzip.open(path, "wt", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(track_header)
        for offset in range(0, args.tracks, args.batch_size):
            size = min(args.batch_size, args.tracks - offset)
            artist_idx = rng.integers(0, args.artists, size=size)
            album_idx = rng.integers(0, args.albums, size=size)
            popularity = rng.integers(0, 101, size=size)
            danceability = rng.beta(2.2, 2.0, size=size)
            energy = rng.beta(2.0, 1.8, size=size)
            tempo = rng.normal(120, 25, size=size).clip(50, 220)
            valence = rng.beta(2.0, 2.0, size=size)
            acousticness = rng.beta(1.2, 3.5, size=size)
            instrumentalness = rng.beta(0.7, 5.0, size=size)
            speechiness = rng.beta(1.1, 8.0, size=size)
            loudness = rng.normal(-7, 3, size=size).clip(-30, 0)
            rows = []
            for j in range(size):
                idx = offset + j
                date = start + np.timedelta64(int(rng.integers(0, days)), "D")
                a_idx, al_idx = int(artist_idx[j]), int(album_idx[j])
                rows.append([
                    f"TRK{idx:08d}",
                    f"{py_rng.choice(PREFIXES)} {py_rng.choice(SUFFIXES)} {idx:07d}",
                    f"ART{a_idx:07d}", f"Artist_{a_idx:06d}",
                    f"ALB{al_idx:07d}", f"Album_{al_idx:06d}", str(date),
                    py_rng.choice(GENRES), int(popularity[j]),
                    int(rng.integers(90_000, 600_001)),
                    round(float(danceability[j]), 4), round(float(energy[j]), 4),
                    round(float(tempo[j]), 2), round(float(valence[j]), 4),
                    round(float(acousticness[j]), 4), round(float(instrumentalness[j]), 4),
                    round(float(speechiness[j]), 4), round(float(loudness[j]), 2),
                ])
            writer.writerows(rows)

    with (output / "genres.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["genre"])
        writer.writerows([[g] for g in GENRES])

    print(f"Created synthetic datasets in: {output.resolve()}")
    print(f"Tracks: {args.tracks:,}; artists: {args.artists:,}; albums: {args.albums:,}; genres: {len(GENRES)}")

if __name__ == "__main__":
    main()
