import re
from datetime import datetime,timedelta
import requests

def process_events(timeframe):
    today = datetime.now().strftime('%Y-%m-%d')
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')

    # Regular expressions to match date patterns (YYYYMMDD, today, tomorrow)
    date_pattern = r"(\d{4})(\d{2})(\d{2})"
    today_pattern = r"\b(today)\b"
    tomorrow_pattern = r"\b(tomorrow)\b"

    # Try to find dates in the input text using regex
    date_matches = re.findall(date_pattern, timeframe)
    today_match = re.search(today_pattern, timeframe, re.IGNORECASE)
    tomorrow_match = re.search(tomorrow_pattern, timeframe, re.IGNORECASE)
    
    # Check various date formats and return the appropriate message
    if today_match:
        return today, today
    elif tomorrow_match:
        return tomorrow, tomorrow
    elif len(date_matches) == 2:
        start_date = datetime.strptime(''.join(date_matches[0]), '%Y%m%d').strftime('%Y-%m-%d')
        end_date = datetime.strptime(''.join(date_matches[1]), '%Y%m%d').strftime('%Y-%m-%d')
        return start_date, end_date
    elif len(date_matches) == 1:
        single_date = datetime.strptime(''.join(date_matches[0]), '%Y%m%d').strftime('%Y-%m-%d')
        return single_date, single_date
    else:
        print('error')

def validate_llm_token(token):
    url = 'https://api.openai.com/v1/files'
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return True
    else:
        return False