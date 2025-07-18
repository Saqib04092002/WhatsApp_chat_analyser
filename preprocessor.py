import re
import pandas as pd

def preprocess(data):
    # Regex for both 12-hour and 24-hour formats
    pattern_12h = r'\d{1,2}/\d{1,2}/\d{2,4}, \d{1,2}:\d{2}\s?[ap]m\s-\s'
    pattern_24h = r'\d{1,2}/\d{1,2}/\d{2,4}, \d{1,2}:\d{2}\s-\s'
    
    # Check which pattern matches
    if re.search(pattern_12h, data):
        pattern = pattern_12h
        date_format = '%d/%m/%y, %I:%M %p'
    elif re.search(pattern_24h, data):
        pattern = pattern_24h
        date_format = '%d/%m/%y, %H:%M'
    else:
        # Fallback for other potential formats, might need adjustment
        pattern = r'(\d{1,2}/\d{1,2}/\d{2,4}, \d{1,2}:\d{2})\s-\s'
        date_format = '%d/%m/%y, %H:%M'

    messages = re.split(pattern, data)[1:]
    dates = re.findall(pattern, data)

    df = pd.DataFrame({'user_message': messages, 'message_date': dates})

    # Clean up and convert date column
    df['message_date'] = df['message_date'].str.replace(r'\s-\s', '', regex=True).str.strip()
    df['message_date'] = df['message_date'].str.replace('\u202f', ' ', regex=False) # Handles non-breaking space
    df['date'] = pd.to_datetime(df['message_date'], format=date_format, errors='coerce')

    df.dropna(subset=['date'], inplace=True)
    df.drop(columns=['message_date'], inplace=True)

    users = []
    messages = []
    for message in df['user_message']:
        entry = re.split(r'([\w\W]+?):\s', message, maxsplit=1)
        if len(entry) > 1 and entry[1]:
            users.append(entry[1])
            messages.append(entry[2])
        else:
            users.append('group_notification')
            messages.append(entry[0])

    df['user'] = users
    df['message'] = messages
    df.drop(columns=['user_message'], inplace=True)

    # --- THIS IS THE CORRECTED PART ---
    # Using consistent, lowercase column names
    df['only_date'] = df['date'].dt.date
    df['year'] = df['date'].dt.year
    df['month_num'] = df['date'].dt.month
    df['month'] = df['date'].dt.month_name()
    df['day'] = df['date'].dt.day
    df['day_name'] = df['date'].dt.day_name()
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute

    period = []
    for hour in df['hour']:
        if hour == 23:
            period.append(f"{hour}-00")
        else:
            period.append(f"{hour}-{hour+1}")
    df['period'] = period
    
    return df