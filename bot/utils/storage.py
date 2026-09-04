# In-memory storage
user_data = {}
link_cache = {}
victim_data_store = {}

# When generating links, store the full link
def store_link(unique_id, user_id, link_type, full_link):
    link_cache[unique_id] = {
        "user_id": user_id,
        "type": link_type,
        "link": full_link,
        "time": time.time()
    }
