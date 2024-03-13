import streamlit as st
import os
import pandas as pd
from io import StringIO
from pypdf import PdfReader
import nest_asyncio
from llama_index.core import (VectorStoreIndex, SimpleDirectoryReader, StorageContext,
        load_index_from_storage)
from llama_index.core.tools import (QueryEngineTool, ToolMetadata)
from llama_index.core import Settings
from llama_index.core import Document
from llama_index.readers.file import PDFReader
from llama_index.agent.openai import OpenAIAssistantAgent
from openai import OpenAI

nest_asyncio.apply()

os.environ["OPENAI_API_KEY"] = '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'
client = OpenAI(api_key='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')


st.title("My Personal Lengthy Doc Reader")
st.write("Upload the doc below:")


uploaded_file = st.file_uploader("Choose a file")
if uploaded_file is not None:

    # See openAI_API_tests.ipynb

    # Upload a file with an "assistants" purpose
    file = client.files.create(
    file=uploaded_file,
    purpose='assistants'
    )

    # Add the file to the assistant
    assistant = client.beta.assistants.create(
    instructions = "You are a helpful agent. Use your knowledge base to best answer queries.",
    model="gpt-4-turbo-preview",
    tools=[{"type": "retrieval"}],
    file_ids=[file.id]
    )

    thread = client.beta.threads.create(
        messages=[
            {
            "role": "user",
            "content": "What are the main topics of the document?",
            "file_ids": [file.id]
            }
        ]
    )

    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id,
        model="gpt-4-turbo-preview",
        # instructions="New instructions that override the Assistant instructions",
        # tools=[{"type": "code_interpreter"}, {"type": "retrieval"}]
    )

    run_steps = client.beta.threads.runs.steps.list(
        thread_id=thread.id,
        run_id = run.id
    )

    #retrieve message(s) from this thread
    messages = client.beta.threads.messages.list(thread.id)

    assitant_response = messages.data[0].content[0].text.value
    st.write ( assitant_response )



    # reader = PdfReader ( uploaded_file )
    # pgs = reader.pages
    # textt = ''
    # for pg in pgs:
    #     textt = textt + pg.extract_text()
    # st.write ( textt )



    # agent = OpenAIAssistantAgent.from_new(
    # name="Fact Checker",
    # instructions="You are fact checking the articles.",
    # openai_tools=[{"type": "retrieval"}],
    # files=[textt],
    # verbose=True,
    # )




    # reader = PdfReader ( uploaded_file )
    # pgs = reader.pages
    # textt = ''
    # for pg in pgs:
    #     textt = textt + pg.extract_text()
    # st.write ( text )

    # paperr_doc = PDFReader.load_data(file = uploaded_file)

    # try:
    #     storage_context = StorageContext.from_defaults(
    #         persist_dir="./storage"
    #     )
    #     paperr_index = load_index_from_storage(storage_context)

    #     index_loaded = True
    # except:
    #     index_loaded = False

    # if not index_loaded:
        # load data
    # paperr_doc = Document( text = textt )
        # paperr_doc = SimpleDirectoryReader(
        #     input_files=[uploaded_file]
        # ).load_data()

        # build index
    # paperr_index = VectorStoreIndex.from_documents( paperr_doc )

        # persist index
        # paperr_index.storage_context.persist(persist_dir="./storage")