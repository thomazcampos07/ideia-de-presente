import streamlit as st
#from langchain.globals import set_llm_cache
#from langchain_community.cache import InMemoryCache
#from src.backend.gen_ai import Rag 
import os
#import re
import openai

#os.environ["OPENAI_API_KEY"] = st.secrets('openai-key-ideia-presente')

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

        # Exibir o resumo das escolhas
        st.write("### Resumo das escolhas:")
        st.json(escolhas)

        # Gerar sugestões de presentes com OpenAI
        if st.button("Gerar sugestões de presentes"):
            with st.spinner("Gerando sugestões... isso pode levar alguns segundos."):
                #openai.api_key = ["OPENAI_API_KEY"]
                openai.api_key = st.secrets('openai-key-ideia-presente')

                prompt = (
                    f"Baseado nas seguintes informações, sugira uma lista de presentes: \n"
                    f"- Para quem é o presente: {destinatario}\n"
                    f"- Ocasião: {ocasiao}\n"
                    f"- Características: {', '.join(caracteristicas)}\n"
                    f"- Detalhes: {detalhes}"
                )

                try:
                    response = openai.Completion.create(
                        engine="text-davinci-003",
                        prompt=prompt,
                        max_tokens=150,
                        n=1,
                        stop=None,
                        temperature=0.7
                    )

                    sugestoes = response.choices[0].text.strip()

                    # Exibir as sugestões no app
                    st.write("### Sugestões de Presentes:")
                    st.write(sugestoes)

                except Exception as e:
                    st.error(f"Erro ao gerar sugestões: {e}")

if __name__ == "__main__":
    main()
