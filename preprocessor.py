import re
import pandas as pd

def preprocess(data):
    pattern = r'\d{2}/\d{2}/\d{2}, \d{1,2}:\d{2}\u202f[ap]m - '
    messages = re.split(pattern, data)[1:]
    dates = re.findall(pattern, data)
    dates = [d.replace(' - ', '') for d in dates]
    df = pd.DataFrame({'user_message': messages, 'message_date': dates})
    # Convert to datetime (note: %I is for 12-hour, %p is for am/pm)
    df['message_date'] = df['message_date'].str.replace('\u202f', ' ', regex=False)
    df['message_date'] = pd.to_datetime(df['message_date'], format='%d/%m/%y, %I:%M %p')


    # Rename column
    df.rename(columns={'message_date': 'date'}, inplace=True)

    # Show first few rows
    print(df.head())
    users = []
    messages = []
    for message in df['user_message']:
        entry = re.split(r'([\w\W]+?):\s ', message)
        if entry[1:]:# user name
            users.append(entry[1])
            messages.append(entry[2])
        else:
            users.append('group_notification')
            messages.append(entry[0])

    df['user'] = users
    df['message'] = messages
    df.drop(columns = ['user_message'], inplace=True)

    df['only_date'] = df['date'].dt.date
    df['Year'] = df['date'].dt.year
    df['month_num'] = df['date'].dt.month
    df['Months'] = df['date'].dt.month_name()
    df['Day'] = df['date'].dt.day_name()
    df['day_name'] = df['date'].dt.day_name()
    df['Hour'] = df['date'].dt.hour
    df['Minute'] = df['date'].dt.minute

    period = []
    for Hour in df[['day_name','Hour']]['Hour']:
        if Hour == 23:
            period.append(str(Hour)+"-"+str('00'))
        elif Hour == 0:
            period.append(str('00')+"-"+str(Hour+1))
        else:
            period.append(str(Hour)+"-"+str(Hour+1))

    df['period'] = period
    
    return df