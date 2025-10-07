import streamlit as st
from langchain_community.document_loaders import WebBaseLoader, SeleniumURLLoader, UnstructuredURLLoader


st.set_page_config(page_title='Web Scrapper', layout='wide')

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/117.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 12; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36",
]


if 'scraped_content' not in st.session_state:
    st.session_state.scraped_content = None



st.title('⚒️ Web Scrapper')

with st.sidebar:
    st.title('Select the Scrapper')
    scraper_choice = st.selectbox("Choose Scrapper", ("WebBased", "SeleniumBased", "URLBased"))
    user_choice = st.selectbox('Choose User Agent', USER_AGENTS)

url = st.text_input('Enter the URL', placeholder="https://example.com")

col1, col2 = st.columns([1, 10])

with col1:
    scrape_button = st.button("⛏️ Scrape")
with col2:
    if st.session_state.scraped_content:
        clear_button = st.button("❌ Clear Results")
        if clear_button:
            st.session_state.scraped_content = None
            st.rerun()



if scrape_button:
    if not url:
        st.error("Please enter a URL")
    else:
        with st.spinner(f"Scraping {url} using {scraper_choice}..."):
            try:
                if scraper_choice == "URLBased": # BUG FIX: Was "UnstructuredBased"
                    loader = UnstructuredURLLoader(urls=[url], headers={"User-Agent": user_choice})
                    docs = loader.load()
                elif scraper_choice == "SeleniumBased":
                    # Note: Selenium needs geckodriver/chromedriver installed on the host
                    loader = SeleniumURLLoader(urls=[url], headless=True, browser='firefox')
                    docs = loader.load()
                elif scraper_choice == "WebBased":
                    loader = WebBaseLoader(url) # WebBaseLoader does not support custom user-agents directly
                    docs = loader.load()

                if docs:
                    full_text = "\n\n".join([d.page_content for d in docs])
                    # 4. Store the result in session state instead of a local variable
                    st.session_state.scraped_content = full_text
                else:
                    st.warning('⚠️ No content extracted. Try another scrapper or URL.')
                    st.session_state.scraped_content = None

            except Exception as e:
                st.error(f"An error occurred: {e}")
                st.session_state.scraped_content = None


if st.session_state.scraped_content:
    st.markdown("---")
    st.write('📍 Snippet Preview')
    
    preview_text = st.session_state.scraped_content
    st.info(preview_text[:1000] + ("..." if len(preview_text) > 1000 else ""))
    
    st.subheader("Full content")
    with st.expander('Click here to view the full text'):
        st.text_area('Scraped Text', preview_text, height=500, key="full_text_area")
        st.download_button(
            label="Download Text",
            data=preview_text,
            file_name="scraped_text.txt",
            mime="text/plain"
        )