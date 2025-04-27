import streamlit as st, requests, sqlite3, datetime, uuid, os
API_URL=os.getenv('API_URL','http://localhost:8000/search')
DB='feedback.sqlite'

def store(q,a,v):
    con=sqlite3.connect(DB);c=con.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS fb(time,query,answer,vote)')
    c.execute('INSERT INTO fb VALUES (?,?,?,?)',(datetime.datetime.utcnow(),q,a,v))
    con.commit();con.close()

st.title('🛍️ ShopTalk')
if 'hist' not in st.session_state: st.session_state.hist=[]
q=st.text_input('Ask for a product…')
if st.button('Search') and q:
    res=requests.post(API_URL,json={'query':q}).json()
    st.session_state.hist.append((q,res['answer']))
for uq,ua in st.session_state.hist[::-1]:
    st.markdown(f'**You:** {uq}')
    st.markdown(ua)
    c1,c2=st.columns(2)
    if c1.button('👍',key=str(uuid.uuid4())): store(uq,ua,1)
    if c2.button('👎',key=str(uuid.uuid4())): store(uq,ua,0)
