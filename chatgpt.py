import base64
import csv
import os
import subprocess
import sys
import threading
import time
import warnings
import wave
from langdetect import detect
import openai
from langchain.chains import ConversationalRetrievalChain
from langchain_community.chat_models import ChatOpenAI
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.indexes import VectorstoreIndexCreator
from langchain.indexes.vectorstore import VectorStoreIndexWrapper
import requests
import speech_recognition as sr

# Suppress warnings about deprecations
warnings.filterwarnings("ignore", category=UserWarning, module="langchain_community")
# Set OpenAI API key
os.environ["OPENAI_API_KEY"] = "AORy9VtQ7d92QpxIjObRT3BlbkFJdE15QzG0F6roDzyFeo1Y"

# Enable to save to disk & reuse the model (for repeated queries on the same data)
PERSIST = False
on_off = "chaton"
query = None
def change_db():
       
        API_KEY = 'hL_UnJalHJE_LJ_JuP_NHi-z8g0tAaGWrwx8znvsGByfcD-DN9NQ'
        # The owner of the database to query
        DB_OWNER = 'moayadanjjar8'
        # The name of the database
        DB_NAME = 'library.db'  # Ensure the exact case of the database name

        sql = 'SELECT * FROM nao6_db;'  # Corrected SQL query
        base64_sql = base64.b64encode(sql.encode('ascii')).decode('ascii')  # Encode and convert to string

        files = {
            'apikey': (None, API_KEY),
            'dbowner': (None, DB_OWNER),
            'dbname': (None, DB_NAME),
            'sql': (None, base64_sql),
        }

        response = requests.post('https://api.dbhub.io/v1/query', files=files)
        response.raise_for_status()  # Raise an exception for bad response status
        data = response.json()

            
        csv_file = 'data/books.csv'

            # Write data to CSV file with ';' as the delimiter
        with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file, delimiter=';')
                writer.writerow(['Title', 'Author', 'Genre', 'SubGenre', 'Height', 'Publisher', 'Location', 'Availability',"publication_year"])  # Write header
                for item in data:
                    row = [next((detail['Value'] for detail in item if detail['Name'] == field), '') for field in ['Title', 'Author', 'Genre', 'SubGenre', 'Height', 'Publisher', 'Location', 'Availability',"publication_year"]]
                    writer.writerow(row) 
    

def custom_response(query):
    identity_phrases = [
        "who are you", "what are you", "tell me about yourself", 
        "your identity", "what is your name", "identify yourself", "what is your identity"
    ]
    for phrase in identity_phrases:
        if phrase in query.lower():
            return "I am humanoid librarian robot NAO6. I am here today to assist you."
    return False

def add_instruction(query):
    instruction = "Please do not provide any code in python or any programming language or snippet or programming-related answers and if anyone asks about it, say you don't have that ability and you act like a humanoid robot NAO6, not an AI and dont get any book out form oyr collecetion just anwser from out collection"
    return instruction + query

def enforce_no_code(query):
    identity_phrases = [
        "give me code in python", "python code", "python snippet", 
        "```", "c code", "c++ code", "java code","give me code","give me snippet code"
    ]
    for phrase in identity_phrases:
        if phrase in query.lower() :
            return "I don't have the ability to provide any code snippet."
    return False

if len(sys.argv) > 1:
    query = sys.argv[1]

# Load the documents
loader = DirectoryLoader("data/")
documents = loader.load()

# Create the embeddings
embeddings = OpenAIEmbeddings()

if PERSIST and os.path.exists("persist"):
    print("Reusing index...\n")
    vectorstore = Chroma(persist_directory="persist", embedding_function=embeddings)
else:
    vectorstore = Chroma.from_documents(documents, embeddings)
    if PERSIST:
        vectorstore.persist(persist_directory="persist")

chain = ConversationalRetrievalChain.from_llm(
    llm=ChatOpenAI(model="gpt-3.5-turbo"),
    retriever=vectorstore.as_retriever(search_kwargs={"k": 1}),
)

chat_history = []
ctn=0
duration=0.0
lang="eng"
work=False
python_executable = r"C:\Users\anjja\AppData\Local\Programs\Python\Python312\python.exe"
while True:
    # change_db()
    if os.path.exists("recorded_audio.wav"):
        os.remove("recorded_audio.wav")

    if not query:
        # Run the voice handling script to record audio
        # process = subprocess.Popen(
        #     ["C:/Python27/python.exe", "D:/myproject/naov6/chatproject/handlevoice.py"],
        #     creationflags=subprocess.CREATE_NEW_CONSOLE,
        #     stdin=subprocess.PIPE,
        #     stdout=subprocess.PIPE,
        #     stderr=subprocess.PIPE
        # )
        process = subprocess.Popen(
            [python_executable, "D:/myproject/naov6/chatproject/test.py"],
            creationflags=subprocess.CREATE_NEW_CONSOLE,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        # Wait for the process to complete
        stdout, stderr = process.communicate()
        file_path = "recorded_audio.wav"

        r = sr.Recognizer()
        audio_file_path = 'recorded_audio.wav'



        try:
            with sr.AudioFile(audio_file_path) as source:
                audio = r.record(source)
                if lang=="eng":
                 input = r.recognize_google(audio, language='en')
                elif lang=="arb":
                 input = r.recognize_google(audio, language='ar')
                print("human :",input)

                if input =="الى الانجليزي":
                    lang="eng"
                elif input =="to arabic":
                    lang="arb"    

                

                if "chatoff" in input or "shut off" in input or "chat of" in input or "chat off" in input :
                    with open("on_off.txt", "w", encoding="utf-8") as file:
                        file.write("chatoff")
                        work = True
                elif "chaton" in input or "chat on" in input or "shut on" in input:
                    with open("on_off.txt", "w", encoding="utf-8") as file:
                        file.write("chaton")
                        work = False
                elif on_off == 'chaton' and input != "chaton" and input != "chatoff":
                    query = input
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand the audio")
            with open("chatAI.txt", "w", encoding="utf-8") as file:
                query = ""
                work=True
                ctn=ctn+1
                file.write("Sorry, I could not understand what you said")
        except Exception as e:
            print(f"Exception: {e}")  # Catch other exceptions for debugging
            with open("chatAI.txt", "w", encoding="utf-8") as file:
                query = ""
                work=True
                ctn=ctn+1
                file.write("Sorry, I could not understand what you said")

    if query == "stopchat" or query =="stop chat":
        with open("chatAI.txt", "w", encoding="utf-8") as file:
                file.write("Think you , Have nice day")
        process = subprocess.Popen(
            ["C:/Python27/python.exe", "D:/myproject/naov6/chatproject/nao.py"],
            creationflags=subprocess.CREATE_NEW_CONSOLE,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )        
        stdout, stderr = process.communicate()
        time.sleep(3)
        sys.exit()

    with open("on_off.txt", "r", encoding="utf-8") as file:
        on_off = file.read()
        print("User:", query)
    if query and on_off != "chatoff" and query != "chaton":
        idt = custom_response(query)
        en=enforce_no_code(query)
        if idt and query!="" :
            print("idt:")
            response_text = idt
            with open("chatAI.txt", "w", encoding="utf-8") as file:
                file.write(response_text)
            print("AI:", response_text)
            time.sleep(3)
            process = subprocess.Popen(
            ["C:/Python27/python.exe", "D:/myproject/naov6/chatproject/nao.py"],
            creationflags=subprocess.CREATE_NEW_CONSOLE,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )        
            stdout, stderr = process.communicate()
            ctn=0 
            query = None
        elif en and query!="":
            print("en:")
            response_text = en
            with open("chatAI.txt", "w", encoding="utf-8") as file:
                file.write(response_text)
            print("AI:", response_text)
            time.sleep(3)
            process = subprocess.Popen(
            ["C:/Python27/python.exe", "D:/myproject/naov6/chatproject/nao.py"],
            creationflags=subprocess.CREATE_NEW_CONSOLE,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )        
            stdout, stderr = process.communicate()
            ctn=0 
            query = None

        elif not en and not idt and query!="":
            
            modified_query = add_instruction(query)
            result = chain({"question": modified_query, "chat_history": chat_history})
            response_text = result['answer']
            chat_history.append((query, response_text))
            print("AI:", response_text)

            with open("chatAI.txt", "w", encoding="utf-8") as file:
                file.write(response_text)

        
            process = subprocess.Popen(
            ["C:/Python27/python.exe", "D:/myproject/naov6/chatproject/nao.py"],
            creationflags=subprocess.CREATE_NEW_CONSOLE,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

            # Wait for the process to complete
            stdout, stderr = process.communicate()
            time.sleep(3)
            ctn=0 
            query = None
    if ctn==5:
       with open("on_off.txt", "w", encoding="utf-8") as file:
                        file.write("chatoff") 
                        on_off = "chatoff" 
       ctn=0                

    if  query == "" and work :
        print("qeuer:",query)  
        process = subprocess.Popen(
            ["C:/Python27/python.exe", "D:/myproject/naov6/chatproject/nao.py"],
            creationflags=subprocess.CREATE_NEW_CONSOLE,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        # Wait for the process to complete
        stdout, stderr = process.communicate()
        time.sleep(1)
        work=False
    if query=="chaton":
        pass      
    if on_off == "chatoff":
        time.sleep(30)
