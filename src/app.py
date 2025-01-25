import streamlit as st
from langchain.globals import set_llm_cache
from langchain_community.cache import InMemoryCache
from src.backend.gen_ai import Rag 
import os
import re

os.environ["OPENAI_API_KEY"] = st.secrets('openai-key-ideia-presente')

with open('styles.css') as f:
    css = f.read()

st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)


def handle_like_change(recom):
    # Se o checkbox "like" for marcado, desmarca o "dislike"
    if st.session_state.get(f'{recom}_like', False):
        st.session_state[f'{recom}_dislike'] = False

def handle_dislike_change(recom):
    # Se o checkbox "dislike" for marcado, desmarca o "like"
    if st.session_state.get(f'{recom}_dislike', False):
        st.session_state[f'{recom}_like'] = False
        
        
def get_like_dislike_status(recom):
    like = st.session_state[f'{recom}_like']
    dislike = st.session_state[f'{recom}_dislike'] 
    
    if like:
        return "liked"
    
    if dislike:
        return 'disliked'
        
    return 'unvalued'
    
def salvar_comentarios():
    comments = {}
    
    for topic in st.session_state['topics']:
        comments[topic] = {}
        comments[topic]['status'] = get_like_dislike_status(topic)
        comments[topic]['comment'] = st.session_state[f'{topic}_comment'] 
        
    saver.save_comments(comments_json=comments, response_json=rag.last_json)
    
def clear_inputs():
    inputs = ['assunto', 'from_name', 'pre_header', 'copy', 'ctas']
    for key in st.session_state.keys():
        if key in inputs:
            st.session_state[key] = ""

@st.experimental_fragment
def print_buttons(text):
    chunks = re.split(r'(<!-- avaliacao  \[\w*-\d+\] -->)', text)
    recomendation = []
    texts = []
    st.session_state['topics'] = []
    
    for chunk in chunks:
        if chunk.startswith('<!--'):
            recomendation.append(re.search(r'(\w*-\d+)', chunk)[0])
        else:
            texts.append(chunk)
    
    col1, col2 = None, None
    
    with st.container():
        for recom, text in zip(recomendation, texts):
            print_text = text
            if '<!-- container -->' in text:
                clean_text = text.split('<!-- container -->')
                st.markdown(clean_text[0], unsafe_allow_html=True)
                print_text = clean_text[1]
                
                cont = st.container()
                col1, col2 = cont.columns([0.9,0.1])
            
            st.session_state['topics'].append(recom)
            
            col1.markdown(print_text, unsafe_allow_html=True)
            col1.text_input("Comentários", key=f"{recom}_comment")
            
            
            like_key = f'{recom}_like'
            dislike_key = f'{recom}_dislike'
            col2.checkbox(label=":thumbsup:", key=like_key, on_change=handle_like_change, args=(recom,))
            col2.checkbox(label=":thumbsdown:", key=dislike_key, on_change=handle_dislike_change, args=(recom,))       
            st.divider()

    

set_llm_cache(InMemoryCache())

rag = Rag()
saver = SaverResponse()

st.image('logo-acerto-verde.svg', width = 200)

st.title("IA Entregabilidade")

st.markdown("**Aumente a entregabilidade de e-mails com a nossa solução inteligente!**")

st.write("Visite a nossa documentação para mais informações sobre como funciona e como utilizar a IA Entregabilidade:")

st.page_link(doc, label="Documentação")

with st.form(key='forml'):
    assunto = st.text_input("Assunto *", key='assunto')
    from_name= st.text_input("From name", key='from_name')
    pre_header = st.text_input("Pré-header", key='pre_header')
    copy = st.text_area("Corpo do e-mail *", height = 270, key='copy')
    ctas = st.text_input("CTA's", key='ctas')
    

    col1, col2, col3 = st.columns([0.7,0.15,0.15])

    with col2:
        erase_button = st.form_submit_button(label = 'Limpar', type="secondary", on_click=clear_inputs)
    with col3:
        submit_button = st.form_submit_button(label = 'Enviar', type="primary")


streaming_finalized = False
container_streaming = st.empty()

if submit_button:
    with container_streaming.container():
        with st.empty():
            if (assunto and copy):
                    st.subheader("Estamos analisando o e-mail enviado. Aguarde...")
                    response = streaming_parse(rag.run(assunto, from_name, pre_header, copy, ctas))
                    for chunk in response:
                        st.markdown(chunk, unsafe_allow_html=True)
                        
                    streaming_finalized = True
                    
            else:
                st.markdown(":red[*Preencha os campos obrigatórios**]")

if streaming_finalized:
    container_streaming.empty()
    
    form_json = { "assunto": assunto, "from_name": from_name, "pre_header": pre_header,
                                    "copy": copy, "ctas": ctas}
    saver.save_response(response=rag.last_response, form_json=form_json, response_json=rag.last_json)

    print_buttons(rag.last_response)    
    st.button(label = 'Salvar Comentários', on_click=salvar_comentarios)