import streamlit as st
import preprocessor, helper
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px  
import tempfile  


# Light/Dark Mode Toggle
mode = st.sidebar.radio("Theme", ["Light", "Dark"])

def set_background(mode):
    """Sets WhatsApp-style background with proper text visibility in both modes"""
    background_css = f"""
    <style>
        
        .stApp {{
            background: {'#0e1117' if mode == "Dark" else '#e5ddd5'} 
                       url("https://web.whatsapp.com/img/bg-chat-tile-{'dark' if mode == "Dark" else 'light'}_a4be512e7195b6b733d9110b408f075d.png");
            background-attachment: fixed;
            background-size: {'350px 350px' if mode == "Dark" else '400px 400px'};
            background-blend-mode: {'multiply' if mode == "Dark" else 'overlay'};
        }}
        
        /* Main content container */
        .main .block-container {{
            background-color: {'rgba(11, 20, 31, 0.9)' if mode == "Dark" else 'rgba(255, 255, 255, 0.95)'};
            border-radius: 10px;
            padding: 2rem;
            margin-top: 2rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        
        /* All text elements */
        .stMarkdown, .stText, .stTitle, .stHeader, .stSubheader,
        .stAlert, .stDataFrame, .stSlider, .stSelectbox, .stRadio {{
            color: {'white' if mode == "Dark" else '#111827'} !important;
        }}
        
        /* Sidebar */
        [data-testid="stSidebar"] {{
            background-color: {'#1e293b' if mode == "Dark" else '#128C7E'} !important;
        }}
        
        /* Sidebar text */
        [data-testid="stSidebar"] * {{
            color: white !important;
        }}
        
        /* Charts background */
        .stPlot {{
            background-color: {'rgba(255, 255, 255, 0.1)' if mode == "Dark" else 'rgba(255, 255, 255, 0.9)'} !important;
            border-radius: 8px;
            padding: 15px;
        }}
        
        /* Dataframes */
        .dataframe {{
            background-color: {'rgba(30, 41, 59, 0.8)' if mode == "Dark" else 'rgba(255, 255, 255, 0.95)'} !important;
        }}
        
        /* Specific text elements that need stronger contrast */
        h1, h2, h3, h4, h5, h6, p, div, span {{
            color: {'white' if mode == "Dark" else '#111827'} !important;
        }}
    </style>
    """
    st.markdown(background_css, unsafe_allow_html=True)

# Apply background style
set_background(mode)      





st.sidebar.title("WhatsApp Chat Analyzer")

uploaded_file = st.sidebar.file_uploader("Choose a file")
if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        data = bytes_data.decode("utf-8")
        df = preprocessor.preprocess(data)

       
        
        # fetch unique users
        user_list = df['user'].unique().tolist()
       
        user_list.remove('group_notification')
        
        user_list.sort()
        user_list.insert(0, "Overall")

        selected_user = st.sidebar.selectbox("Show analysis wrt:", user_list)

        if st.sidebar.button("Show Analysis"):
            
            # Get stats Area - make sure helper.fetch_stats() returns 4 values
            num_messages, words, num_media_messages, num_links = helper.fetch_stats(selected_user, df)
            
            st.title("Top Statistics")   

            col1, col2, col3, col4 = st.columns(4)

               

            with col1:
                st.header("Total Messages")
                st.title(num_messages)
            with col2:
                st.header("Total Words")
                st.title(words)
            with col3:
                st.header("Media Shared")
                st.title(num_media_messages)
            with col4:
                st.header("Links Shared")
                st.title(num_links)
                

            # monthly _ timeline
            st.title("Monthly Timeline")
            timeline = helper.monthly_timeline(selected_user, df)
            fig, ax = plt.subplots()
            ax.plot(timeline['time'],timeline['message'],color = 'green')
            plt.xticks(rotation = 'vertical')
            st.pyplot(fig)

            #daily timeline
            st.title("Daily Timeline")
            daily_timeline = helper.daily_timeline(selected_user, df)  # Store in 'daily_timeline'
            fig, ax = plt.subplots()
            ax.plot(daily_timeline['only_date'], daily_timeline['message'], color='black')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

            # activity map
            st.title("Activity Map")
            col1, col2 = st.columns(2)
            with col1:
                 st.header("Most Busy day")
                 busy_day = helper.week_activity_map(selected_user, df)
                 fig, ax = plt.subplots()
                 ax.bar(busy_day.index, busy_day.values)
                 plt.xticks(rotation='vertical')
                 st.pyplot(fig)
            
            with col2:
                 st.header("Most Busy Month")
                 busy_month = helper.month_activity_map(selected_user, df)
                 fig, ax = plt.subplots()
                 ax.bar(busy_month.index, busy_month.values, color='orange')
                 plt.xticks(rotation='vertical')
                 st.pyplot(fig)

            
            st.title("Weekly Activity Map")
            user_heatmap = helper.activity_heatmap(selected_user, df)
            fig,ax = plt.subplots()
            ax = sns.heatmap(user_heatmap)
            st.pyplot(fig)
            

            # Finding the most active users in the group
            if selected_user == "Overall":
                st.title('Most Busy Users')
                x,new_df = helper.most_busy_users(df)
                fig, ax = plt.subplots()
               
                col1,col2 = st.columns(2)

                with col1:
                      ax.bar(x.index, x.values,color='Red')
                      plt.xticks(rotation='vertical')
                      st.pyplot(fig)
                
                with col2:
                        st.dataframe(new_df)


            # World Cloud
            st.title("Word Cloud")
            df_wc = helper.create_wordcloud(selected_user, df)
            fig, ax = plt.subplots()
            ax.imshow(df_wc, interpolation='bilinear')
            ax.axis('off')  # To remove axes
            st.pyplot(fig)

    
            # Most common words
            most_common_df = helper.most_common_words(selected_user, df)

            fig,ax = plt.subplots()

            ax.barh(most_common_df[0],most_common_df[1])

            plt.xticks(rotation='vertical') 

            st.title("Most Common Words")

            st.pyplot(fig)

            st.dataframe(most_common_df)

           # Emoji Analysis
st.title("Emoji Analysis")

# Get Emoji DataFrame
emoji_df = helper.emoji_helper(selected_user, df)

# Top N selector
top_n = st.slider("Select number of top emojis to display", min_value=5, max_value=30, value=10)

# Display DataFrame
col1, col2 = st.columns(2)

with col1:
    st.subheader("Top Emojis")
    st.dataframe(emoji_df.head(top_n))

with col2:
    st.subheader("Emoji Frequency Pie Chart")
    fig1, ax1 = plt.subplots()
    ax1.pie(emoji_df[1].head(top_n),
            labels=emoji_df[0].head(top_n),
            autopct=lambda pct: f"{pct:.1f}%",
            startangle=90)
    ax1.axis('equal')
    st.pyplot(fig1)

# Add a horizontal bar chart
st.subheader("Emoji Frequency Bar Chart")
fig2, ax2 = plt.subplots()
ax2.barh(emoji_df[0].head(top_n).astype(str), emoji_df[1].head(top_n), color='orange')
plt.xlabel("Frequency")
plt.ylabel("Emoji")
plt.xticks(rotation='horizontal')
st.pyplot(fig2)



# In app.py - Replace your monthly timeline section with this:

st.title("📅 Interactive Timeline")
timeline = helper.monthly_timeline(selected_user, df)

# Create interactive plot
try:
    # Set appropriate colors based on theme
    line_color = '#25D366'  # WhatsApp green
    text_color = '#FFFFFF' if mode == "Dark" else '#000000'
    bg_color = 'rgba(0,0,0,0.7)' if mode == "Dark" else 'rgba(255,255,255,0.7)'
    
    fig = px.line(timeline, 
                 x='time', 
                 y='message',
                 title='<b>Message Trend Over Time</b>',
                 labels={'message': 'Number of Messages', 'time': 'Month'},
                 template='plotly_dark' if mode == "Dark" else 'plotly_white',
                 color_discrete_sequence=[line_color])
    
    # Style the figure
    fig.update_layout(
        hovermode='x unified',
        xaxis_title='Month',
        yaxis_title='Messages Count',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color=text_color),
        hoverlabel=dict(
            bgcolor=bg_color,
            font_size=12,
            font_color=text_color
        )
    )
    
    fig.update_traces(
        line=dict(width=3),
        hovertemplate='<b>%{x}</b><br>Messages: %{y}',
        marker=dict(size=8)
    )
    
    # Adjust grid lines for visibility
    fig.update_xaxes(showgrid=True, gridwidth=0.5, gridcolor='rgba(128,128,128,0.2)')
    fig.update_yaxes(showgrid=True, gridwidth=0.5, gridcolor='rgba(128,128,128,0.2)')
    
    st.plotly_chart(fig, use_container_width=True, theme="streamlit" if mode == "Light" else None)
    
except Exception as e:
    st.error(f"Error creating interactive timeline: {str(e)}")
    # Fallback to matplotlib
    fig, ax = plt.subplots(figsize=(10,5))
    ax.plot(timeline['time'], timeline['message'], color='#25D366', linewidth=2.5)
    ax.set_title('Message Trend Over Time', pad=20)
    ax.set_xlabel('Month')
    ax.set_ylabel('Messages Count')
    ax.grid(alpha=0.2)
    plt.xticks(rotation=45)
    
    # Set background color based on theme
    if mode == "Dark":
        fig.patch.set_facecolor('#0e1117')
        ax.set_facecolor('#0e1117')
        ax.xaxis.label.set_color('white')
        ax.yaxis.label.set_color('white')
        ax.title.set_color('white')
        ax.tick_params(colors='white')
    
    st.pyplot(fig)