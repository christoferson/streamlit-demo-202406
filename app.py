import streamlit as st

st.set_page_config(
    page_title="Demo",
    page_icon="🧊",
    layout="centered", # "centered" or "wide"
    initial_sidebar_state="expanded", #"auto", "expanded", or "collapsed"
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None
    }
)

st.logo(icon_image="images/logo.png", image="images/logo_text.png")

pages = {
    "Tools": [ # "Overview" becomes a section header
        st.Page("navigation/overview.py", title="Overview", icon=":material/home:"),
        st.Page("navigation/chat.py", title="Chat", icon="🌷"),
    ],
    "Metrics": [ # "Metrics becomes a section header
        #st.Page("core_metrics.py"),
        # ...
    ],
}

#if not user_logon():
#    pages.append(st.Page("step_1.py", title="Step 1", icon="1️⃣"))
#    pages.append(st.Page("step_2.py", title="Step 2", icon="2️⃣"))
# else:

navigation = st.navigation(pages)

navigation.run()