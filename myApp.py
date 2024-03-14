import streamlit as st
import os
import pandas as pd
# import nest_asyncio
import openai
from openai import OpenAI
import time

# nest_asyncio.apply()

client = OpenAI()


st.title("My Personal Doc Reader")
st.write("Upload the doc below:")


uploaded_file = st.file_uploader("Choose a document pdf file")
if uploaded_file is not None:

    # Upload a file with an "assistants" purpose
    file = client.files.create(
    file=uploaded_file,
    purpose='assistants'
    )

    # Add the file to the assistant
    assistant = client.beta.assistants.create(
    instructions = "You are a customer support chatbot. Use your knowledge base to best answer queries.",
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

    # this places the thread in retrieval status
    run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id)



    #wait for query to complete
    i=0
    while (run.status != "completed") & (i<20):
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id)
    
        time.sleep(3)
        i=i+1
        st.write(f"Current state ({i*3} sec): {run.status}")

    #retrieve message(s) from this thread
    messages = client.beta.threads.messages.list(thread_id=thread.id)

    mess = messages.data[0]
    st.write(mess.content[0].text.value)


#clean up: delete file, assistant
try:
    file_deletion_status = client.beta.assistants.files.delete(
    assistant_id=assistant.id,
    file_id=file.id
    )
except:
    pass
