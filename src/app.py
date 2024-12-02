import streamlit as st
import pandas as pd
from datetime import datetime
from database import DatabaseManager
from utils import validate_url, find_feed_url, parse_feed

# Initialize database
db = DatabaseManager()

def fetch_posts_from_source(source):
    """Fetch posts from a source and save them to the database."""
    if not source.feed_url:
        st.error(f"No feed URL found for source: {source.url}")
        return False
        
    try:
        # Delete existing posts from this source
        db.delete_posts_by_source(source.id)
        
        # Fetch and save new posts
        posts = parse_feed(source.feed_url)
        for post in posts:
            try:
                db.add_post(
                    source_id=source.id,
                    title=post['title'],
                    description=post.get('description', ''),
                    summary=post.get('summary', ''),
                    image_url=post.get('image_url'),
                    external_link=post['link'],
                    published_date=post['published_date']
                )
            except Exception as e:
                st.warning(f"Error adding post: {str(e)}")
        return True
    except Exception as e:
        st.error(f"Error fetching posts: {str(e)}")
        return False

def add_source():
    st.subheader("Add New Source")
    with st.form("add_source_form"):
        url = st.text_input("Enter website URL")
        name = st.text_input("Source Name (optional)")
        submitted = st.form_submit_button("Add Source")
        
        if submitted and url:
            if not validate_url(url):
                st.error("Please enter a valid URL")
                return
                
            # Try to find feed URL
            feed_url = find_feed_url(url)
            
            # Add to database
            try:
                source = db.add_source(url=url, feed_url=feed_url, name=name)
                st.success(f"Source added successfully!")
                
                if feed_url:
                    st.info(f"Found RSS feed: {feed_url}")
                    # Fetch initial posts
                    if fetch_posts_from_source(source):
                        st.success("Posts fetched successfully!")
                else:
                    st.warning("No RSS feed found for this source")
            except Exception as e:
                st.error(f"Error adding source: {str(e)}")

def view_sources():
    st.subheader("Current Sources")
    sources = db.get_all_sources()
    
    if not sources:
        st.info("No sources added yet")
        return
    
    # Create columns for the table header
    cols = st.columns([3, 2, 2, 1])
    cols[0].write("**Source**")
    cols[1].write("**Feed URL**")
    cols[2].write("**Last Checked**")
    cols[3].write("**Actions**")
    
    # Display each source with a refresh button
    for source in sources:
        cols = st.columns([3, 2, 2, 1])
        cols[0].write(source.name or source.url)
        cols[1].write(source.feed_url or "Not found")
        cols[2].write(source.last_checked.strftime("%Y-%m-%d %H:%M") if source.last_checked else "Never")
        
        # Add refresh button
        if cols[3].button("🔄", key=f"refresh_{source.id}"):
            with st.spinner(f"Refreshing posts from {source.name or source.url}..."):
                if fetch_posts_from_source(source):
                    st.success("Posts refreshed successfully!")
                    # Update last_checked timestamp
                    source.last_checked = datetime.utcnow()
                    db.session.commit()

def view_posts():
    st.subheader("Latest Posts")
    posts = db.get_all_posts(limit=50)
    
    if not posts:
        st.info("No posts available yet")
        return
        
    post_data = []
    for post in posts:
        post_data.append({
            "Title": post.title,
            "Source": post.source.name or post.source.url,
            "Published": post.published_date.strftime("%Y-%m-%d %H:%M") if post.published_date else "Unknown",
            "Link": post.external_link
        })
    
    df = pd.DataFrame(post_data)
    st.dataframe(df, column_config={
        "Link": st.column_config.LinkColumn("Link")
    })

def main():
    st.title("Content Aggregator")
    st.markdown("""
    This application helps you aggregate content from various sources.
    Add your favorite websites and we'll fetch their latest posts for you!
    """)
    
    tab1, tab2, tab3 = st.tabs(["Add Source", "View Sources", "View Posts"])
    
    with tab1:
        add_source()
    with tab2:
        view_sources()
    with tab3:
        view_posts()

if __name__ == "__main__":
    main()
