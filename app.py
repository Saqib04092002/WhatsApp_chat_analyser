import streamlit as st
import preprocessor, helper
import matplotlib.pyplot as plt
import seaborn as sns
import tempfile
import os
from fpdf import FPDF

# PDF creation function
def create_pdf_report(filename, selected_user, stats, plots):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, f"WhatsApp Chat Analysis: {filename}", ln=True, align='C')
    pdf.cell(0, 10, f"Analysis for: {selected_user}", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Top Statistics", ln=True)
    pdf.set_font("Arial", '', 10)
    pdf.cell(95, 10, f"Total Messages: {stats['num_messages']}", border=1)
    pdf.cell(95, 10, f"Total Words: {stats['words']}", border=1, ln=True)
    pdf.cell(95, 10, f"Media Shared: {stats['num_media_messages']}", border=1)
    pdf.cell(95, 10, f"Links Shared: {stats['num_links']}", border=1, ln=True)
    pdf.ln(10)
    with tempfile.TemporaryDirectory() as temp_dir:
        for title, fig in plots.items():
            if pdf.get_y() > 220:
                pdf.add_page()
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 10, title, ln=True)
            img_path = os.path.join(temp_dir, f"{title.replace(' ', '_').replace(':', '')}.png")
            try:
                fig.savefig(img_path, bbox_inches='tight', dpi=150)
                pdf.image(img_path, w=180)
                pdf.ln(5)
            except Exception as e:
                pdf.set_font("Arial", 'I', 10)
                pdf.cell(0, 10, f"(Could not generate plot: {title} - {e})", ln=True)
    return bytes(pdf.output())


# --- CORRECTED BACKGROUND AND STYLING FUNCTION ---
def set_background(mode):
    """Sets WhatsApp-style background with proper text visibility in both modes"""
    
    # Define colors for light and dark mode
    if mode == "Dark":
        main_bg_color = 'rgba(11, 20, 31, 0.9)'
        text_color = 'white'
        sidebar_bg_color = '#1e293b'
        button_text_color = 'white'
        app_bg = '#0e1117'
        bg_image = "https://web.whatsapp.com/img/bg-chat-tile-dark_a4be512e7195b6b733d9110b408f075d.png"
    else: # Light Mode
        main_bg_color = 'rgba(255, 255, 255, 0.95)'
        text_color = '#111827'  # Dark grey/black for text
        sidebar_bg_color = '#128C7E'
        button_text_color = '#111827' # Dark text for buttons
        app_bg = '#e5ddd5'
        bg_image = "https://web.whatsapp.com/img/bg-chat-tile-light_a4be512e7195b6b733d9110b408f075d.png"

    background_css = f"""
    <style>
        /* Main App background */
        .stApp {{
            background: {app_bg} url("{bg_image}");
            background-attachment: fixed;
        }}

        /* Main content container */
        .main .block-container {{
            background-color: {main_bg_color};
            border-radius: 10px;
            padding: 2rem;
            margin-top: 2rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}

        /* General text color for the main area */
        .stApp, .stMarkdown, .stText, .stTitle, .stHeader, .stSubheader, .stDataFrame, .stSlider {{
            color: {text_color} !important;
        }}
        h1, h2, h3, h4, h5, h6, p {{
            color: {text_color} !important;
        }}

        /* Sidebar styling */
        [data-testid="stSidebar"] {{
            background-color: {sidebar_bg_color} !important;
        }}

        /* Sidebar text color (for titles, labels, etc.) */
        [data-testid="stSidebar"] .stMarkdown,
        [data-testid="stSidebar"] .stRadio > label,
        [data-testid="stSidebar"] .stSelectbox > label,
        [data-testid="stSidebar"] .stFileUploader > label {{
            color: white !important;
        }}

        /* --- FIX for Button Text --- */
        /* This specifically targets the text inside buttons to make it visible */
        .stButton > button p {{
            color: {button_text_color};
            font-weight: bold;
        }}
        /* Fix for text on the file uploader's "Browse files" button */
        [data-testid="stFileUploadDropzone"] button p {{
             color: {button_text_color} !important;
             font-weight: bold;
        }}
    </style>
    """
    st.markdown(background_css, unsafe_allow_html=True)


# --- Main App Logic ---

mode = st.sidebar.radio("Theme", ["Light", "Dark"])
set_background(mode) # Apply the theme

st.sidebar.title("WhatsApp Chat Analyzer")
uploaded_file = st.sidebar.file_uploader("Choose a file")

if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")
    df = preprocessor.preprocess(data)
    
    # The user dropdown will appear after file is processed
    user_list = df['user'].unique().tolist()
    user_list.remove('group_notification')
    user_list.sort()
    user_list.insert(0, "Overall")
    selected_user = st.sidebar.selectbox("Show analysis with respect to:", user_list)

    st.title(f"📄 Analysis of: {uploaded_file.name}")
    st.markdown("---")
    plots_for_pdf = {}
    num_messages, words, num_media_messages, num_links = helper.fetch_stats(selected_user, df)
    stats_data = { "num_messages": num_messages, "words": words, "num_media_messages": num_media_messages, "num_links": num_links }
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
    
    # Monthly Timeline (Using Matplotlib)
    st.title("📅 Monthly Timeline")
    timeline = helper.monthly_timeline(selected_user, df)
    fig_monthly, ax_monthly = plt.subplots()
    ax_monthly.plot(timeline['time'], timeline['message'], color='#25D366', marker='o')
    plt.xticks(rotation='vertical')
    ax_monthly.grid(True, linestyle='--', alpha=0.6)
    st.pyplot(fig_monthly)
    plots_for_pdf['Monthly Timeline'] = fig_monthly

    # Daily Timeline
    st.title("Daily Timeline")
    daily_timeline = helper.daily_timeline(selected_user, df)
    fig_daily, ax_daily = plt.subplots()
    ax_daily.plot(daily_timeline['only_date'], daily_timeline['message'], color='black')
    plt.xticks(rotation='vertical')
    st.pyplot(fig_daily)
    plots_for_pdf['Daily Timeline'] = fig_daily

    # Activity Map
    st.title("Activity Map")
    col1, col2 = st.columns(2)
    with col1:
        st.header("Most Busy Day")
        busy_day = helper.week_activity_map(selected_user, df)
        fig_day, ax_day = plt.subplots()
        ax_day.bar(busy_day.index, busy_day.values)
        plt.xticks(rotation='vertical')
        st.pyplot(fig_day)
        plots_for_pdf['Most Busy Day'] = fig_day
    with col2:
        st.header("Most Busy Month")
        busy_month = helper.month_activity_map(selected_user, df)
        fig_month, ax_month = plt.subplots()
        ax_month.bar(busy_month.index, busy_month.values, color='orange')
        plt.xticks(rotation='vertical')
        st.pyplot(fig_month)
        plots_for_pdf['Most Busy Month'] = fig_month
    
    # Weekly Activity Heatmap
    st.title("Weekly Activity Map")
    user_heatmap = helper.activity_heatmap(selected_user, df)
    fig_heatmap, ax_heatmap = plt.subplots()
    ax_heatmap = sns.heatmap(user_heatmap)
    st.pyplot(fig_heatmap)
    plots_for_pdf['Weekly Activity Heatmap'] = fig_heatmap
    
    # Most Busy Users
    if selected_user == "Overall":
        st.title('Most Busy Users')
        x, new_df = helper.most_busy_users(df)
        fig_busy, ax_busy = plt.subplots()
        col1, col2 = st.columns(2)
        with col1:
            ax_busy.bar(x.index, x.values, color='red')
            plt.xticks(rotation='vertical')
            st.pyplot(fig_busy)
            plots_for_pdf['Most Busy Users'] = fig_busy
        with col2:
            st.dataframe(new_df)

    # WordCloud
    st.title("WordCloud")
    df_wc = helper.create_wordcloud(selected_user, df)
    fig_wc, ax_wc = plt.subplots()
    ax_wc.imshow(df_wc)
    ax_wc.axis('off')
    st.pyplot(fig_wc)
    plots_for_pdf['WordCloud'] = fig_wc

    # Most common words
    st.title("Most Common Words")
    most_common_df = helper.most_common_words(selected_user, df)
    fig_common, ax_common = plt.subplots()
    ax_common.barh(most_common_df[0], most_common_df[1])
    plt.xticks(rotation='vertical')
    st.pyplot(fig_common)
    plots_for_pdf['Most Common Words'] = fig_common

    # Emoji Analysis
    st.title("Emoji Analysis")
    emoji_df = helper.emoji_helper(selected_user, df)
    if not emoji_df.empty:
        st.dataframe(emoji_df.head())
        fig_emoji, ax_emoji = plt.subplots()
        top_emojis = emoji_df.head(7)
        ax_emoji.pie(top_emojis[1], labels=top_emojis[0], autopct="%1.1f%%", startangle=90)
        ax_emoji.set_title("Top 7 Emojis")
        st.pyplot(fig_emoji)
        plots_for_pdf['Emoji Distribution'] = fig_emoji
    else:
        st.write("No emojis found in the selected chat.")

    # PDF Download Button
    st.markdown("---")
    st.title("📥 Download Full Report")
    pdf_bytes = create_pdf_report(uploaded_file.name, selected_user, stats_data, plots_for_pdf)
    st.download_button(
        label="Download Analysis as PDF",
        data=pdf_bytes,
        file_name=f"whatsapp_analysis_{uploaded_file.name}.pdf",
        mime="application/pdf"
    )