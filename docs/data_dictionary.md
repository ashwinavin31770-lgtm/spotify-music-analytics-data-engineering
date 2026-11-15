# Data dictionary

All rows are synthetic and generated for technical practice. None of these values describe actual Spotify artists, tracks, followers, streams, or listeners.

## tracks.csv.gz
- `track_id`: synthetic unique track identifier
- `track_name`: generated track title
- `artist_id`, `artist_name`: generated artist reference
- `album_id`, `album_name`: generated album reference
- `release_date`: generated calendar date
- `genre`: one of 50 generated genre labels
- `popularity`: synthetic integer score from 0 to 100
- `duration_ms`: generated duration in milliseconds
- `danceability`, `energy`, `valence`, `acousticness`, `instrumentalness`, `speechiness`: synthetic values between 0 and 1
- `tempo`: generated BPM-like value
- `loudness`: generated dB-like value

## artists.csv.gz
`artist_id`, `artist_name`, `country`, `followers`, `monthly_listeners`, `primary_genre`. Follower/listener values are fictional.

## albums.csv.gz
`album_id`, `album_name`, `artist_id`, `release_date`, `album_type`, `total_tracks`.
