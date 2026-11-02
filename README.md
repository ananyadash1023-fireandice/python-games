# Python Games

Small desktop games built with Python and Tkinter.

## Games

- `flames.py` — a name-based FLAMES game.
- `tic_tac_toe.py` — two-player Tic-Tac-Toe with player names and scorekeeping.
- `etl_memory_match.py` — a memory-matching game that teaches the Extract,
  Transform, and Load (ETL) workflow using sample customer records. The final
  stage exports cleaned data to `etl_warehouse.csv`.

## Run a game

Install Python 3, open a terminal in this folder, and run a script:

```powershell
python etl_memory_match.py
```

Replace `etl_memory_match.py` with `flames.py` or `tic_tac_toe.py` to play another
game. These are desktop apps and require a graphical desktop session.

## Create the ETL game intro video

On Windows, install the video-rendering dependencies and run the generator:

```powershell
python -m pip install -r requirements-video.txt
python create_etl_video.py
```

The script creates `etl_memory_match_intro.mp4` with animated illustrations and
narration from Windows' built-in speech voices. It renders locally and does not
send project files to an online video service.
