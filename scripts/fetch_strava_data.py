import requests
import json
import os
from datetime import datetime, timedelta
import argparse
import time

# Define global variables (they are placeholders for now)
CLIENT_ID = None
CLIENT_SECRET = None
REFRESH_TOKEN = None
AUTH_CODE = None
RUN_MILES_FILE = 'docs/assets/data/running_data.json'

def initialize_globals():
    """
    Initialize the global variables by loading them from the environment variables.
    This function will be called after loading the .env file in the main function.
    """
    global CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN, AUTH_CODE
    CLIENT_ID = os.getenv('STRAVA_CLIENT_ID')
    CLIENT_SECRET = os.getenv('STRAVA_CLIENT_SECRET')
    REFRESH_TOKEN = os.getenv('STRAVA_REFRESH_TOKEN')
    AUTH_CODE = os.getenv('STRAVA_CODE')

# One time use functions to get code with appropriate permissions
# def get_authorization_url():
#     """
#     Returns the URL to redirect users to for authorization. Get CODE from URL and set environment variable
#     to continue upon next call.
#     """
#     redirect_uri = os.environ.get('STRAVA_REDIRECT_URI', 'http://localhost')
#     scope = "read,activity:read_all,profile:read_all"
    
#     auth_url = (
#         f"https://www.strava.com/oauth/authorize?"
#         f"client_id={CLIENT_ID}&"
#         f"redirect_uri={redirect_uri}&"
#         f"response_type=code&"
#         f"scope={scope}"
#     )
    
#     return auth_url

# One time use function to get appropriate tokens with scope
# def exchange_code_for_tokens():
#     """
#     Exchange the authorization code for access and refresh tokens.
#     Updates the refresh token in .env file.
#     Returns both access_token and refresh_token.
#     """
#     token_url = "https://www.strava.com/oauth/token"
#     payload = {
#         'client_id': CLIENT_ID,
#         'client_secret': CLIENT_SECRET,
#         'code': AUTH_CODE,
#         'grant_type': 'authorization_code'
#     }
    
#     try:
#         response = requests.post(token_url, data=payload, verify=False)
#         response.raise_for_status()
        
#         data = response.json()
        
#         # Save the refresh token
#         if "refresh_token" in data:
#             update_env_file('STRAVA_REFRESH_TOKEN', data["refresh_token"])
        
#         return data
    
#     except requests.exceptions.RequestException as e:
#         print(f"Error exchanging code for tokens: {e}")
#         if hasattr(response, 'json'):
#             try:
#                 print(f"Response: {response.json()}")
#             except:
#                 print(f"Status code: {response.status_code}")
#         return None

def update_env_file(key, value):
    """
    Updates a single value in the .env file.
    """
    try:
        # Read current .env content
        env_content = {}
        if os.path.exists(".env"):
            with open(".env", "r") as f:
                for line in f:
                    if '=' in line:
                        k, v = line.strip().split('=', 1)
                        env_content[k] = v
        
        # Update the value
        env_content[key] = value
        
        # Write back to .env
        with open(".env", "w") as f:
            for k, v in env_content.items():
                f.write(f"{k}={v}\n")
        
        # Reload environment variables
        os.environ[key] = value
    
    except Exception as e:
        print(f"Error updating .env file: {e}")

def refresh_access_token():
    """
    Uses the refresh token to get a new access token from Strava.
    Updates the refresh token in .env file if a new one is provided.
    Returns the access token.
    """
    auth_url = "https://www.strava.com/oauth/token"
    payload = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'refresh_token': REFRESH_TOKEN,
        'grant_type': 'refresh_token'
    }
    
    try:
        response = requests.post(auth_url, data=payload)
        response.raise_for_status()  # Raise exception for 4XX/5XX responses
        
        data = response.json()
        
        # Update the refresh token if a new one is provided
        if "refresh_token" in data:
            new_refresh_token = data["refresh_token"]
            update_env_file('STRAVA_REFRESH_TOKEN', new_refresh_token)
            
        return data['access_token']
    
    except requests.exceptions.RequestException as e:
        print(f"Error refreshing token: {e}")
        if hasattr(response, 'json'):
            try:
                print(f"Response: {response.json()}")
            except:
                print(f"Status code: {response.status_code}")
        return None

def fetch_activities(access_token, after=None, before=None):
    activities_url = "https://www.strava.com/api/v3/athlete/activities"
    headers = {'Authorization': f'Bearer {access_token}'}
    
    # Initialize empty list for all activities
    all_activities = []
    page = 1
    per_page = 100
    
    # Set up date parameters
    params = {'per_page': per_page, 'page': page}
    if after:
        params['after'] = after
    if before:
        params['before'] = before
    
    # Strava API returns max 200 activities per request; paginate
    while True:
        response = requests.get(activities_url, headers=headers, params=params)
        
        # Check for rate limiting
        if response.status_code == 429:
            print("Rate limited. Waiting 15 minutes...")
            time.sleep(900)  # Wait 15 minutes
            continue
            
        new_activities = response.json()
        
        if not new_activities:
            break
            
        print(f"{len(new_activities)} new activities found for page {page}.")
        all_activities.extend(new_activities)
        page += 1
        params['page'] = page
        
        # Be nice to the API - small pause between requests
        time.sleep(0.5)

    return all_activities

def process_activities(activities):
    # Process activities into format needed for heatmap
    running_data = {}
    
    for activity in activities:
        if activity['type'] == 'Run':
            date = activity['start_date_local'].split('T')[0]  # Get just the date part
            distance_miles = activity['distance'] * 0.000621371  # Convert meters to miles
            
            if date in running_data:
                running_data[date] += distance_miles
            else:
                running_data[date] = distance_miles
    
    return running_data

def load_existing_data():
    # Load existing data if available
    try:
        with open(RUN_MILES_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_data(data, filename=RUN_MILES_FILE):
    # Ensure directory exists
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    # Save to JSON file
    with open(filename, 'w') as f:
        json.dump(data, f)

def get_latest_activity_timestamp(data):
    # Find the latest activity date
    if not data:
        # Default to 1 year ago if no data
        return int((datetime.now() - timedelta(days=365)).timestamp())
    
    latest_date = max(data.keys())
    # Add 1 day to avoid duplicates
    timestamp = int(datetime.strptime(latest_date, '%Y-%m-%d').timestamp()) + 86400
    return timestamp

def generate_heatmap_data(start_date=None, end_date=None, incremental=False):
    access_token = refresh_access_token()
    
    # Load existing data
    existing_data = load_existing_data()
    
    # Handle date parameters
    after = None
    before = None
    
    if incremental and existing_data:
        # Use the latest activity date as the starting point
        after = get_latest_activity_timestamp(existing_data)
        print(f"Fetching activities after {datetime.fromtimestamp(after).strftime('%Y-%m-%d')}")
    elif start_date:
        # Convert start_date string to timestamp
        after = int(datetime.strptime(start_date, '%Y-%m-%d').timestamp())
    
    if end_date:
        # Convert end_date string to timestamp
        before = int(datetime.strptime(end_date, '%Y-%m-%d').timestamp())
    
    # Fetch new activities
    activities = fetch_activities(access_token, after, before)
    
    if not activities:
        print("No new activities found")
        return existing_data
    
    # Process new activities
    new_running_data = process_activities(activities)
    
    # Merge with existing data
    for date, miles in new_running_data.items():
        if date in existing_data:
            # Uncomment if you want to replace existing data
            # existing_data[date] = miles
            # Or add to existing data
            existing_data[date] += miles
        else:
            existing_data[date] = miles
    
    # Save merged data
    save_data(existing_data)
    
    print(f"Updated data with {len(new_running_data)} new running days")
    return existing_data

if __name__ == "__main__":
    # Set up command line arguments
    parser = argparse.ArgumentParser(description='Fetch Strava running data')
    parser.add_argument('--start', help='Start date in YYYY-MM-DD format')
    parser.add_argument('--end', help='End date in YYYY-MM-DD format')
    parser.add_argument('--incremental', action='store_true', 
                        help='Only fetch new activities since last run')
    
    args = parser.parse_args()
    
    try:
        from dotenv import load_dotenv
        load_dotenv(override=True)  # Load environment variables from .env file for local development
        initialize_globals()
    except ImportError:
        pass  # Skip if running in GitHub Actions
    
    access_token = refresh_access_token()

    generate_heatmap_data(
        start_date=args.start,
        end_date=args.end,
        incremental=args.incremental
    )

    # data = fetch_activities(access_token)
    # save_data(data, 'docs/assets/data/all_activities.json')