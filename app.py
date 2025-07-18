import streamlit as st
import preprocessor, helper
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import tempfile
import os
from fpdf import FPDF

# PDF creation function
def create_pdf_report(filename, selected_user, stats, plots):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", 'B', 20)
    pdf.cell(0, 10, f"WhatsApp Chat Analysis Report", ln=True, align='C')
    pdf.set_font("Arial", 'I', 12)
    pdf.cell(0, 10, f"Chat File: {filename}", ln=True, align='C')
    pdf.cell(0, 10, f"Analysis for: {selected_user}", ln=True, align='C')
    pdf.ln(10)

    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "Key Metrics", ln=True, align='L')
    pdf.set_font("Arial", '', 12)
    pdf.cell(95, 10, f"Total Messages: {stats['num_messages']}", border=1)
    pdf.cell(95, 10, f"Total Words: {stats['words']}", border=1, ln=True)
    pdf.cell(95, 10, f"Media Shared: {stats['num_media_messages']}", border=1)
    pdf.cell(95, 10, f"Links Shared: {stats['num_links']}", border=1, ln=True)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        for title, fig in plots.items():
            pdf.add_page()
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(0, 10, title, ln=True, align='C')
            pdf.ln(10)
            
            img_path = os.path.join(temp_dir, f"{title.replace(' ', '_').replace(':', '')}.png")
            try:
                fig.savefig(img_path, bbox_inches='tight', dpi=150)
                
                img_width = 180
                x_pos = (pdf.w - img_width) / 2
                pdf.image(img_path, x=x_pos, w=img_width)
                
            except Exception as e:
                pdf.set_font("Arial", 'I', 10)
                pdf.cell(0, 10, f"(Could not generate plot: {title} - {e})", ln=True)
                
    return bytes(pdf.output())

# Styling function
def set_background(mode):
    if mode == "Dark":
        main_bg_color = 'rgba(11, 20, 31, 0.9)'
        text_color = 'white'
        sidebar_bg_color = '#1e293b'
        button_text_color = 'white'
        app_bg = '#0e1117'
        bg_image = "https://web.whatsapp.com/img/bg-chat-tile-dark_a4be512e7195b6b733d9110b408f075d.png"
    else:
        main_bg_color = 'rgba(255, 255, 255, 0.95)'
        text_color = '#111827'
        sidebar_bg_color = '#128C7E'
        button_text_color = '#111827'
        app_bg = '#e5ddd5'
        bg_image = "https://web.whatsapp.com/img/bg-chat-tile-light_a4be512e7195b6b733d9110b408f075d.png"

    background_css = f"""
    <style>
        .stApp {{ background: {app_bg} url("{bg_image}"); background-attachment: fixed; }}
        .main .block-container {{ background-color: {main_bg_color}; border-radius: 10px; padding: 2rem; margin-top: 2rem; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); }}
        .stApp, .stMarkdown, .stText, .stTitle, .stHeader, .stSubheader, .stDataFrame, .stSlider {{ color: {text_color} !important; }}
        h1, h2, h3, h4, h5, h6, p {{ color: {text_color} !important; }}
        [data-testid="stSidebar"] {{ background-color: {sidebar_bg_color} !important; }}
        [data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] .stRadio > label, [data-testid="stSidebar"] .stSelectbox > label, [data-testid="stSidebar"] .stFileUploader > label {{ color: white !important; }}
        .stButton > button p {{ color: {button_text_color}; font-weight: bold; }}
        [data-testid="stFileUploadDropzone"] button p {{ color: {button_text_color} !important; font-weight: bold; }}
    </style>
    """
    st.markdown(background_css, unsafe_allow_html=True)

# --- Main App Logic ---
mode = st.sidebar.radio("Theme", ["Light", "Dark"])
set_background(mode)

st.sidebar.title("WhatsApp Chat Analyzer")
uploaded_file = st.sidebar.file_uploader("Choose a file")

if uploaded_file is not None:
    try:
        bytes_data = uploaded_file.getvalue()
        data = bytes_data.decode("utf-8")
        df = preprocessor.preprocess(data)
    except Exception as e:
        st.error(f"Error processing file: {e}")
        st.stop()
    
    user_list = df['user'].unique().tolist()
    if 'group_notification' in user_list:
        user_list.remove('group_notification')
    user_list.sort()
    user_list.insert(0, "Overall")
    selected_user = st.sidebar.selectbox("Show analysis for:", user_list)

    st.title(f"📄 Analysis of: {uploaded_file.name}")
    
    plots_for_pdf = {}
    num_messages, words, num_media_messages, num_links = helper.fetch_stats(selected_user, df)
    stats_data = { "num_messages": num_messages, "words": words, "num_media_messages": num_media_messages, "num_links": num_links }

    st.markdown("---")
    st.title("At a Glance: Key Metrics")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""<div style="background-color: #25D366; padding: 15px; border-radius: 10px; text-align: center;"><h3 style="color: white;">Total Messages</h3><p style="color: white; font-size: 24px; font-weight: bold;">{num_messages}</p></div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""<div style="background-color: #128C7E; padding: 15px; border-radius: 10px; text-align: center;"><h3 style="color: white;">Total Words</h3><p style="color: white; font-size: 24px; font-weight: bold;">{words}</p></div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""<div style="background-color: #075E54; padding: 15px; border-radius: 10px; text-align: center;"><h3 style="color: white;">Media Shared</h3><p style="color: white; font-size: 24px; font-weight: bold;">{num_media_messages}</p></div>""", unsafe_allow_html=True)
    with col4:
        st.markdown(f"""<div style="background-color: #34B7F1; padding: 15px; border-radius: 10px; text-align: center;"><h3 style="color: white;">Links Shared</h3><p style="color: white; font-size: 24px; font-weight: bold;">{num_links}</p></div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.title("😃😠 Emotional Tone")
    sentiment_counts = helper.sentiment_analysis(selected_user, df)
    if not sentiment_counts.empty:
        fig_sentiment, ax_sentiment = plt.subplots()
        ax_sentiment.pie(sentiment_counts, labels=sentiment_counts.index, autopct="%1.1f%%", colors=['#25D366','#6c757d','#dc3545'], startangle=90)
        st.pyplot(fig_sentiment)
        plots_for_pdf['Sentiment Analysis'] = fig_sentiment
    else:
        st.write("Not enough data to perform sentiment analysis.")

    st.markdown("---")
    st.title("Message Timelines")
    col1, col2 = st.columns(2)
    with col1:
        st.header("Monthly")
        timeline = helper.monthly_timeline(selected_user, df)
        if not timeline.empty:
            fig_monthly, ax_monthly = plt.subplots()
            ax_monthly.plot(timeline['time'], timeline['message'], color='#25D366', marker='o')
            plt.xticks(rotation=90)
            st.pyplot(fig_monthly)
            plots_for_pdf['Monthly Timeline'] = fig_monthly
        else:
            st.write("No data available.")
            
    with col2:
        st.header("Daily")
        daily_timeline = helper.daily_timeline(selected_user, df)
        if not daily_timeline.empty:
            fig_daily, ax_daily = plt.subplots()
            ax_daily.plot(daily_timeline['only_date'], daily_timeline['message'], color='black')
            plt.xticks(rotation=90)
            st.pyplot(fig_daily)
            plots_for_pdf['Daily Timeline'] = fig_daily
        else:
            st.write("No data available.")

    st.markdown("---")
    st.title("Activity Maps")
    col1, col2 = st.columns(2)
    with col1:
        st.header("Most Busy Day")
        busy_day = helper.week_activity_map(selected_user, df)
        fig_day, ax_day = plt.subplots()
        ax_day.bar(busy_day.index, busy_day.values)
        plt.xticks(rotation=45)
        st.pyplot(fig_day)
        plots_for_pdf['Most Busy Day'] = fig_day
    with col2:
        st.header("Most Busy Month")
        busy_month = helper.month_activity_map(selected_user, df)
        fig_month, ax_month = plt.subplots()
        ax_month.bar(busy_month.index, busy_month.values, color='orange')
        plt.xticks(rotation=45)
        st.pyplot(fig_month)
        plots_for_pdf['Most Busy Month'] = fig_month
    
    st.markdown("---")
    st.title("Hourly Activity Heatmap")
    user_heatmap = helper.activity_heatmap(selected_user, df)
    fig_heatmap, ax_heatmap = plt.subplots()
    ax_heatmap = sns.heatmap(user_heatmap)
    st.pyplot(fig_heatmap)
    plots_for_pdf['Activity Heatmap'] = fig_heatmap
    
    if selected_user == 'Overall':
        st.markdown("---")
        st.title('Most Active Users')
        x, new_df = helper.most_busy_users(df)
        fig_busy, ax_busy = plt.subplots()
        col1, col2 = st.columns(2)
        with col1:
            st.header("By Message Count")
            ax_busy.bar(x.index, x.values, color='red')
            plt.xticks(rotation=45)
            st.pyplot(fig_busy)
            plots_for_pdf['Most Active Users (Chart)'] = fig_busy
        with col2:
            st.header("By Percentage (%)")
            st.dataframe(new_df)

    st.markdown("---")
    st.title("Word & Emoji Analysis")
    col1, col2 = st.columns(2)
    with col1:
        st.header("Most Common Words")
        most_common_df = helper.most_common_words(selected_user, df)
        fig_common, ax_common = plt.subplots()
        ax_common.barh(most_common_df[0], most_common_df[1])
        st.pyplot(fig_common)
        plots_for_pdf['Most Common Words'] = fig_common
    with col2:
        st.header("Most Used Emojis")
        emoji_df = helper.emoji_helper(selected_user, df)
        if not emoji_df.empty:
            st.dataframe(emoji_df)
        else:
            st.write("No Emojis Found")

    # --- NEW SECTION: Display Shared Media ---
    st.markdown("---")
    st.title("📷 Shared Media")
    all_media = helper.fetch_all_media(selected_user, df)
    if not all_media.empty:
        st.dataframe(all_media)
    else:
        st.write("No media files were shared in this selection.")

    st.markdown("---")
    st.title("🔗 Shared Links")
    all_links = helper.fetch_all_links(selected_user, df)
    if all_links:
        link_df = pd.DataFrame(all_links, columns=["URL"])
        st.dataframe(link_df)
    else:
        st.write("No links were shared in this selection.")

    st.markdown("---")
    st.title("WordCloud")
    df_wc = helper.create_wordcloud(selected_user, df)
    fig_wc, ax_wc = plt.subplots()
    ax_wc.imshow(df_wc)
    ax_wc.axis('off')
    st.pyplot(fig_wc)
    plots_for_pdf['WordCloud'] = fig_wc

    st.markdown("---")
    st.title("📥 Download Full Report")
    pdf_bytes = create_pdf_report(uploaded_file.name, selected_user, stats_data, plots_for_pdf)
    st.download_button(
        label="Download Analysis as PDF",
        data=pdf_bytes,
        file_name=f"whatsapp_analysis_{uploaded_file.name}.pdf",
        mime="application/pdf"
    )