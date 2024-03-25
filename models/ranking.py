from concurrent.futures import ThreadPoolExecutor
from sentence_transformers import SentenceTransformer, util
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

import mysql.connector


def sql_data_push(df):
    global fixed_id

    connection = mysql.connector.connect(
        user="root",
        host="localhost",
        database="talent_db",
        password="root@123",
        port="3306"
    )
       
    cursor = connection.cursor()
    table_name = 'login_1'
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        ID INT,
        LINK VARCHAR(255),
        Name VARCHAR(5000),
        Email VARCHAR(255),
        Similarity FLOAT
    )
    """
    cursor.execute(create_table_query)
   
    cursor.execute(f"SELECT MAX(ID) FROM {table_name}")
    result = cursor.fetchone()
    if result[0] is not None:
        fixed_id = result[0] + 1 
    else:
        fixed_id = 1  

    for index, row in df.iterrows():
        insert_query = f"""
            INSERT INTO {table_name} (ID, LINK, Name, Email, Similarity)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (fixed_id, row['Link'], row['Name'], row['Email'], row['Similarity']))
   
    connection.commit()

    cursor.close()
    connection.close()
    return fixed_id

def DB_retrieve(Job_ID):
    try:
        connection = mysql.connector.connect(
            user="root",
            host="localhost",
            database="talent_db",
            password="root@123",
            port="3306"
        )
       
        cursor = connection.cursor()
        table_name = 'login_1'
        create_table_query = f"""
        SELECT Link, Name, Email, Similarity FROM {table_name} 
        WHERE ID = {Job_ID}
        """
        cursor.execute(create_table_query)
        result_DB = cursor.fetchall()  # Fetch all rows matching the query
        connection.close()
        
        # Convert the result into a DataFrame
        df = pd.DataFrame(result_DB, columns=['Link', 'Name', 'Email', 'Similarity'])

        return df
    except mysql.connector.Error as error:
        print("Error while connecting to MySQL", error)
        return None


def extract_content_postjobfree(link):
    response = requests.get(link)
    soup = BeautifulSoup(response.content, 'html.parser')
    content_tags = soup.find_all('div', class_='normalText')
    return " ".join([tag.get_text() for tag in content_tags])

def extract_content_jobspider(link):
    response = requests.get(link)
    soup = BeautifulSoup(response.content, 'html.parser')
    content_tags = soup.find_all('td', width='100%')
    return " ".join([tag.get_text() for tag in content_tags])

def extract_name(content):

    lines = content.split('\n')
   
    # Check if the first line contains a name
    first_line = lines[0].strip()
    if first_line:
        return first_line
   
    # If the first line doesn't contain a name, check the second line
    if len(lines) > 1:
        second_line = lines[1].strip()
        if second_line:
            return second_line
   
    # If no name is found, return None
    return None

def extract_email(content):
    emails=re.findall(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",content)
    return emails[0] if emails else None

def process_resume_link(link):
    if 'postjobfree' in link:
        content = extract_content_postjobfree(link)
    elif 'jobspider' in link:
        content = extract_content_jobspider(link)
    else:
        content = ""
   
    name = extract_name(content)
    email=extract_email(content)
   
    return name, content, email

def rank_resumes(query_path, resume_links_df):
    model = SentenceTransformer("paraphrase-MiniLM-L6-v2")

    with open(query_path, encoding='utf-8') as f:
        query = f.read()
        print(f"Received Text")

    query_embedding = model.encode(query, convert_to_tensor=True)

    resume_contents = []

    with ThreadPoolExecutor() as executor:
        processed_resumes = list(executor.map(lambda link: process_resume_link(link), resume_links_df['links']))

    names, contents, emails = zip(*processed_resumes)
    resume_embeddings = model.encode(contents, convert_to_tensor=True)

    cosine_scores = util.pytorch_cos_sim(query_embedding, resume_embeddings)[0]

    if len(resume_links_df) == len(cosine_scores):
        result_df = pd.DataFrame({'Link': resume_links_df['links'], 'Name': names, 'Email': emails, 'Similarity': cosine_scores.tolist()})
        result_df = result_df.sort_values(by='Similarity', ascending=False).reset_index(drop=True)
    else:
        result_df = pd.DataFrame(columns=['Link', 'Name', 'Email', 'Similarity'])

   
    # data = pd.read_csv("demo.csv")
    df=sql_data_push(result_df)
    return [result_df, df]
  