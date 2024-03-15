import streamlit as st
import pandas as pd
import time
from openai import OpenAI



def myquery ( ffile, promptt , placeholderr):

    client = OpenAI()

    # Upload a file with an "assistants" purpose
    file = client.files.create(
    file=ffile,
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
            "content": promptt,
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
    my_bar = placeholderr.progress(0, text="Query submitted. Please wait.")
    i=0
    while (run.status != "completed") & (i<20):
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id)
    
        time.sleep(3)
        i=i+1
        my_bar.progress(round(i*5), text=f"Current state ({i*3} sec): {run.status}")

    #retrieve message(s) from this thread
    messages = client.beta.threads.messages.list(thread_id=thread.id)

    my_bar.empty()

    mess = messages.data[0]

    #clean up: delete file, assistant
    client.beta.assistants.files.delete(assistant_id=assistant.id,file_id=file.id)
    client.beta.assistants.delete(assistant_id=assistant.id)
    client.files.delete(file_id=file.id)


    return mess.content[0].text.value



#####  MAIN ###########

st.title("My Personal Doc Reader")

option = st.selectbox(
    "Pick a question from the FAQ list:",
    ("What are the main topics of the document1?", 
     "What are users not allowed to do?",
     "What are clauses for automated (robotic) access to content (content scraping)?", 
     "How can user's personal information be used?"))


#upload a file:
uploaded_file = st.file_uploader("Choose a document file (.pdf):")

placeholder = st.empty()

if (uploaded_file is not None) :
    tt = myquery ( uploaded_file, str(option) , placeholder )
    placeholder.markdown(tt)
    st.balloons()

