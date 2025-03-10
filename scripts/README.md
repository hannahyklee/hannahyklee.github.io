# Scripts

### fetch_strava_data.py

```
# Create the environment
conda env create -f environment.yml

# Activate the environment
conda activate strava-vis
```

Incremental updates:
```
python scripts/fetch_strava_data.py --incremental
```

Specific dates:
```
python scripts/fetch_strava_data.py --start 2023-01-01 --end 2023-12-31
```

Initial setup:
```
python scripts/fetch_strava_data.py
```