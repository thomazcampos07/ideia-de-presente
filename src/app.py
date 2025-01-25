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


def main():
    # Título do App
    st.title("Escolha o Presente Perfeito 🎁")

    # Instruções
    st.write(
        """
        Bem-vindo ao app para escolher presentes! Siga as instruções abaixo:

        1. Escolha para quem é o presente.
        2. Selecione a ocasião.
        3. Indique características da pessoa.
        4. Diga algo mais sobre a pessoa para personalizar o presente!
        """
    )

    # Escolha do destinatário
    destinatario = st.selectbox(
        "Para quem é o presente?",
        ["Namorado(a)", "Amigo(a)", "Colega de Trabalho", "Outros"]
    )

    # Escolha da ocasião
    ocasiao = st.selectbox(
        "Qual é a ocasião?",
        ["Aniversário", "Natal", "Casamento", "Formatura", "Outro"]
    )

    # Características da pessoa
    caracteristicas = st.multiselect(
        "Selecione as características da pessoa:",
        ["Esportista", "Nerd", "Aventureiro(a)", "Artístico(a)", "Tecnológico(a)", "Fashionista"]
    )

    # Mais detalhes sobre a pessoa
    detalhes = st.text_area(
        "Diga mais sobre a pessoa (hobbies, gostos, interesses, etc.):"
    )

    # Armazenar as escolhas em uma variável
    if st.button("Finalizar e salvar informações"):
        escolhas = {
            "destinatario": destinatario,
            "ocasiao": ocasiao,
            "caracteristicas": caracteristicas,
            "detalhes": detalhes
        }
        st.success("Informações salvas com sucesso! 🎉")

        # Exibir o resultado
        st.write("### Resumo das escolhas:")
        st.json(escolhas)

if __name__ == "__main__":
    main()
