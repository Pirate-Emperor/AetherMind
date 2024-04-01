import streamlit as st

from AetherMind.configs.access import access_level

PAGES = [
    {
        "label": "AetherChat",
        "icon": "🎭",
        "link": "AetherMind.py",
        "access": access_level['visitor'],
    },
    {
        "label": "Retriever #42",
        "icon": "👓",
        "link": "pages/retriever_42.py",
        "access": access_level['visitor'],
    },
    {
        "label": "divider",
        "access": access_level['friend'],
    },
    {
        "label": "User Panel",
        "icon": "🧐",
        "link": "pages/user_panel.py",
        "access": access_level['friend'],
    },
    {
        "label": "Book Manager",
        "icon": "📚",
        "link": "pages/book_manager.py",
        "access": access_level['admin'],
    },
]

def render_toc_with_expander():
    with st.expander("👻 **Meet all our agents**"):
        render_toc()
            
def render_toc():
    for page in PAGES:
        if st.session_state.get('access_level', 0) < page['access']:
            continue
        if page['label'] == "divider":
            st.divider()
            continue
        st.page_link(
            label=page['label'],
            icon=page['icon'],
            page=page['link'],
        )