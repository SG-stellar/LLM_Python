import streamlit as st
import time
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core.node_parser import SentenceSplitter
from llama_index.llms.openai import OpenAI
from llama_index.core import Document, VectorStoreIndex, get_response_synthesizer, Settings
from llama_index.core.query_engine import RetrieverQueryEngine
import tiktoken
from pypdf import PdfReader
from llama_index.llms.anthropic import Anthropic

# Include into the "requirements.txt" file:
# "openai" 
# "llama_index" 
# "pypdf" 
# llama-index-llms-anthropic


def myquery ( ffile, promptt, modelll, chunkkk, placeholderr, oaswitch, ret_mode):

    #ectract text from pdf
    reader = PdfReader(ffile)
    number_of_pages = len(reader.pages)
    textt = " "
    for i in range(number_of_pages):
        textt = textt + reader.pages[i].extract_text()

    documents = [Document(text=textt)]
 
    if oaswitch == "OpenAI":
        Settings.llm = OpenAI(model=modelll, temperature=0.0)
        Settings.tokenizer = tiktoken.encoding_for_model(modelll).encode
        Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small") 
        # Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-large") 
        # Open AI: text-embedding-3-large is our new next generation larger embedding model and creates embeddings with up to 3072 dimensions.
        # Stronger performance. text-embedding-3-large is our new best performing model. 
        # Comparing text-embedding-ada-002 to text-embedding-3-large: on MIRACL, the average score has increased from 31.4% to 54.9%, 
        # while on MTEB, the average score has increased from 61.0% to 64.6%.
        Settings.node_parser = SentenceSplitter(chunk_size=chunkkk, chunk_overlap=20)
        Settings.text_splitter = SentenceSplitter(chunk_size=chunkkk, chunk_overlap=20)
        # Settings.transformations = [SentenceSplitter(chunk_size=chunkkk)]  # overrides node_parser/text_spltter settings
        Settings.num_output = 4096 
        # Settings.context_window = 16385 (GPT3) 128000 (GPT4)
    else:
        Settings.llm = Anthropic(model="claude-3-opus-20240229", temperature=0.0)
        try:
            tokenizer = Anthropic().tokenizer
            Settings.tokenizer = tokenizer
        except:
            pass
        
    # build index
    placeholderr.markdown("Indexing the file...")
    index = VectorStoreIndex.from_documents(documents, show_progress=False)

    #A quick way to build a query engine:
    query_engine = index.as_query_engine( 
        response_mode=ret_mode, 
        similarity_top_k=2,
        verbose=False,)

    with st.spinner("Query submitted..."):
        response = query_engine.query(promptt)
    
    return response



#####  MAIN ###########

st.title("My Personal Doc Reader")

option = st.selectbox(
    "Pick a question from the FAQ list:",
    ("What are the main topics of the document (in the list form)?", 
     "What are users not allowed to do (in the list form)?",
     "What are the limitations for automated access (e.g., content scraping)?", 
     "How can be user's personal information used?",
     "What can be user's liabilities?",
     "What are the user's rights?"))

oaswitch = st.sidebar.radio(
    "Model Provider:",
    ["OpenAI", "Anthropic"],
    captions=["GPT","Claude-3"])

modell = st.sidebar.selectbox(
    "Select an OpenAI model:",
    ("gpt-4-turbo-preview", 
     "gpt-3.5-turbo"))


chunk = st.sidebar.selectbox(
    "Select chunk size:",
    (1024,256,512,2048))

ret_mode = st.sidebar.selectbox(
    "Select retrieval mode:",
    ("compact",  #default
     "tree_summarize",
    "accumulate") #produces the most detailed response, at a cost (tokens and latency)
    )


#upload a file:
uploaded_file = st.file_uploader("Choose a document file (.pdf):")

placeholder = st.empty()


if (uploaded_file is not None) :
    tt = myquery ( uploaded_file, str(option), modell, chunk, placeholder, oaswitch, ret_mode)
    placeholder.markdown(tt)
