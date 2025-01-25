from typing import Iterable, List, Tuple
from src.utils.utils import get_secret, get_credentials, PROJECT_ID, REGION, DATASET, TABLE, chunk_parse
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores.utils import DistanceStrategy
from langchain_google_community import BigQueryVectorSearch
from langchain.schema.runnable import RunnablePassthrough
from langchain.prompts import ChatPromptTemplate
from langchain_core.prompts import PromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain_core.output_parsers import JsonOutputParser, PydanticOutputParser
from langchain_openai import OpenAIEmbeddings
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.messages import AIMessage, AIMessageChunk
from langchain_core.runnables import RunnableGenerator, RunnableLambda
from langfuse.callback import CallbackHandler
import time


class Recomendacao(BaseModel):
    texto_antigo: str 
    sugestao: str
    justificativa: str
    
class Response(BaseModel):
    assunto: List[Recomendacao]
    from_name: List[Recomendacao]
    pre_header: List[Recomendacao]
    corpo: List[Recomendacao]
    ctas: List[Recomendacao]
    

class Rag:
    def __init__(self):
        self.openai_llm = ChatOpenAI(model="gpt-4-turbo", temperature=0.3)
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        self.parser = JsonOutputParser(pydantic_object=Response)
        self.vectorstore = self.__setup_vector_db()
        self.template = self.__setup_template()
        self.chain = self.__setup_chain()
        self.last_response = None
        self.last_json = None
        
        
    def __setup_vector_db(self):
        return  BigQueryVectorSearch(
            project_id=PROJECT_ID,
            dataset_name=DATASET,
            table_name=TABLE,
            location=REGION,
            embedding=self.embeddings,
            distance_strategy=DistanceStrategy.EUCLIDEAN_DISTANCE,
            credentials=get_credentials()
)
    def __setup_template(self):
        return PromptTemplate( template = """
                Você é uma IA para recomendar alterações que aumente a entregabilidade em emails e que faz parte do processo de criação dos emails de uma empresa de cobrança digital de dívidas chamado Acerto.
                
                Contexto: Os textos de e-mails a seguir representam uma variedade de comunicações, incluindo notificações de cobrança, ofertas promocionais e informativos. Eles foram ajustados com base em testes de entregabilidade, focando em elementos como o assunto do e-mail, a estrutura do conteúdo e o tom da mensagem. As alterações visaram melhorar a visibilidade nos inboxes dos destinatários, evitando filtros de spam e promocionais. Cada exemplo reflete um tom específico, variando de mais agressivo a mais branda.

                Exemplos:
                {context}

                Instrução: 
                Analise o e-mail abaixo de forma crítica e, com base nas estratégias comprovadas nos exemplos fornecidos, recomende de forma extensiva ajustes focados em maximizar a entregabilidade e que as recomendações sejam coerentes e relavante para o novo email gerado, evitando reescrever o email completamente somente as frases reformuladas. Mantenha o tom original e a intenção do e-mail. As sugestões se limitam a alterações nas seguintes seções Assunto, From Name, Pre Header, Corpo do Email( Copy ), Ctas; focando na otimização do conteúdo para evitar palavras-chave sensíveis a filtros de spam. 
                - Frases motivacionais e de urgência podem aumentar a ação do destinatário, mas devem ser usadas com moderação para não parecerem spam.
                - Identifique e tente substituir termos que são comumente marcados por filtros de spam. Palavras como "exclusivo", "dívida", "garantido", "grátis", "Última chance", "Última oportunidade" entre outras, podem aumentar as chances de um e-mail ser marcado como spam.
                - Nas sugestões tome cuidado com o tamanho do texto do Assunto, do Pre-header e dos CTAs.
                - Coloque a informação mais atraente e importante no assunto, dentro dos primeiros 30 a 50 caracteres.
                - Use o pre header para complementar e expandir a mensagem do assunto, quando necessário e de forma estratégica, mantendo-o conciso e relevante dentro de 40 a 70 caracteres.
                - Cuidado para que o Assunto junto do Pre Header não exceda 100 caracteres.
                - A linguagem coloquial, memes, ditados populares entre outos são utilizados nas comunicações da Acerto de forma estratégica e se alinhados com o público alvo e objetivos específicos da campanha não trazem prejuízo à entregabilidade do e-mail. 
                - O uso de emojis, quando utilizados sem excessos não é prejudicial.
                                    
                Email:
                {email}
                
                {format_instructions}
            
            """,
            input_variables=["context", "email"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()},   
        )
    
    def __setup_chain(self):
        retriever = self.vectorstore.as_retriever(search_kwargs={"k":10})
    
        
        return (
            {"context": retriever, "email": RunnablePassthrough()}
            | self.template
            | self.openai_llm
            | self.parser
        )
        
    def run_msg(self, msg):
        return self.chain.invoke(msg)
    
    def run(self, assunto, from_name, pre_header, copy, ctas, disable_langfuse=False):
        temp = f"""
            Assunto: {assunto}

            From Name: {from_name}

            Pre Header: {pre_header}

            Copy: {copy}

            Ctas: {ctas}
        """
        
        if disable_langfuse:
            response = self.chain.stream(temp)
        
        for json in response:
            yield json
            
        self.last_response = chunk_parse(json)
        self.last_json = json
