from urlextract import URLExtract
from wordcloud import WordCloud
import pandas as pd
from collections import Counter
import emoji

extract = URLExtract()

def fetch_stats(selected_user,df):
    # Filter data if a specific user is selected
    if selected_user != "Overall":
        df = df[df['user'] == selected_user]
    
    # Calculate statistics
    num_messages = df.shape[0]
    
    words = []
    for message in df['message']:
        words.extend(message.split())
    
    num_media_messages = df[df['message'] == '<Media omitted>\n'].shape[0]
    
    # Count links using regex
   
    links = []
    for message in df['message']:
        links.extend(extract.find_urls(message)) 
    
    return num_messages, len(words), num_media_messages, len(links)


def most_busy_users(df):
    x = df['user'].value_counts().head()
    df = round((df['user'].value_counts()/df.shape[0])*100,2).reset_index().rename(columns={'index':'name','user':'percent'})

    return x,df


def create_wordcloud(selected_user, df):
    
    f = open('stop_hinglish.txt','r')
    stop_words = f.read()

    if selected_user != "Overall":
        df = df[df['user'] == selected_user]
    
    temp = df[df['user'] != 'group_notification']
    temp = temp[temp['message'] != '<Media omitted>\n']

    def remove_stop_words(message):
        y = []
        for word in message.lower().split():
            if word not in stop_words:
                y.append(word)
        return " ".join(y)
    # Generate text by joining all messages
    text = " ".join(message for message in df['message'])
    
    # Create WordCloud object (note the correct class name)
    wc = WordCloud(width=500, 
                  height=500, 
                  min_font_size=10, 
                  background_color='white')
    temp['message'] = temp['message'].apply(remove_stop_words)
    
    # Generate word cloud
    df_wc = wc.generate(temp['message'].str.cat(sep=""))
    return df_wc


def most_common_words(selected_user, df):

    f = open('stop_hinglish.txt','r')
    stop_words = f.read()

    if selected_user != "Overall":
        df = df[df['user'] == selected_user]
    
    temp = df[df['user'] != 'group_notification']
    temp = temp[temp['message'] != '<Media omitted>\n']

    words = []
    for message in temp['message']:
        for word in message.lower().split():
            if word not in stop_words:
                words.append(word)
     
    most_common_df = pd.DataFrame(Counter(words).most_common(20))
    return most_common_df


def emoji_helper(selected_user, df):
    if selected_user != "Overall":
        df = df[df['user'] == selected_user]
    
    emojis = []
    for message in df['message']:
        emojis.extend([c for c in message if c in emoji.EMOJI_DATA])
    
    emoji_df = pd.DataFrame(Counter(emojis).most_common(len(Counter(emojis))))
    return emoji_df


def monthly_timeline(selected_user, df):
    if selected_user != "Overall":
        df = df[df['user'] == selected_user]
    
    # First ensure 'date' is datetime type and extract components
    df['date'] = pd.to_datetime(df['date'])
    df['year'] = df['date'].dt.year
    df['month_num'] = df['date'].dt.month
    df['month'] = df['date'].dt.month_name()  # Full month names
    
    timeline = df.groupby(['year', 'month_num', 'month']).count()['message'].reset_index()
    
    # Create time format (e.g., "January-2023")
    timeline['time'] = timeline['month'] + "-" + timeline['year'].astype(str)
    
    return timeline

def daily_timeline(selected_user, df):
    if selected_user != "Overall":
        df = df[df['user'] == selected_user]
    
    daily_timeline  = df.groupby('only_date').count()['message'].reset_index()

    return daily_timeline


def week_activity_map(selected_user, df):
    if selected_user != "Overall":
        df = df[df['user'] == selected_user]

    return df['day_name'].value_counts()

def month_activity_map(selected_user, df):
    if selected_user != "Overall":
        df = df[df['user'] == selected_user]

    return df['Months'].value_counts()


def activity_heatmap(selected_user,df):
    if selected_user != "Overall":
        df = df[df['user'] == selected_user]
    user_heatmap = df.pivot_table(index='day_name',columns='period',values='message',aggfunc='count').fillna(0)
    
    return user_heatmap

# In helper.py - Add this with your other functions
def calculate_response_times(df):
    """Calculate time differences between consecutive messages"""
    df = df.copy()
    df['response_time'] = df.groupby('user')['date'].diff().dt.total_seconds() / 60  # in minutes
    return df[df['response_time'] > 0]  # Filter out first messages


