import requests
import re
import os
import pandas as pd
import tiktoken
import openai
from openai.embeddings_utils import distances_from_embeddings
import numpy as np
from openai.embeddings_utils import distances_from_embeddings, \
    cosine_similarity

openai.api_key = "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"
max_tokens = 500


def get_prompt(id=0, age="university student", prompt="", word_count=200):
    if id == 0:
        return f"Generate 5 questions based on the given text for a {age}. Please provide deatiled answers to the questions as well."
    elif id == 1:
        return f"Generate a {word_count} word summary of the text for a {age}."
    elif id == 2:
        return f"Based the text above, {prompt}"
    return f"As a teacher, evaluate each of the below answers by a {age} for the given questions according to the text provided above. Also, give a score of 1-10 to each of the answers one by one and provide feedback. The questions are denoted as Q followed by the question. Each question is followed by the answer given by the student. As a teacher you should evaluate these answers against the text given above. :\n {prompt}"


def remove_newlines(serie):
    serie = serie.str.replace('\n', ' ')
    serie = serie.str.replace('\\n', ' ')
    serie = serie.str.replace('  ', ' ')
    serie = serie.str.replace('  ', ' ')
    return serie


def read_textfile(file_name):
    with open(file_name, "r", encoding="UTF-8") as f:
        text = f.read()
        text = text[6000:15000]
        return text


def text_to_df(texts):
    texts = texts.replace('-', ' ').replace('_', ' ')
    texts = re.sub(' {2,}', ' ', texts)
    df = pd.DataFrame([("", texts)], columns=['fname', 'text'])
    df['text'] = df.fname + ". " + remove_newlines(df.text)
    return df


def split_into_many(text, tokenizer, max_tokens=max_tokens):
    sentences = text.split('. ')

    # Get the number of tokens for each sentence
    n_tokens = [len(tokenizer.encode(" " + sentence)) for sentence in
                sentences]
    chunks = []
    tokens_so_far = 0
    chunk = []

    for sentence, token in zip(sentences, n_tokens):
        if tokens_so_far + token > max_tokens:
            chunks.append(". ".join(chunk) + ".")
            chunk = []
            tokens_so_far = 0

        if token > max_tokens:
            continue
        chunk.append(sentence)
        tokens_so_far += token + 1

    return chunks


def get_context_encoding(df):
    tokenizer = tiktoken.get_encoding("cl100k_base")
    df.columns = ['title', 'text']
    df['n_tokens'] = df.text.apply(lambda x: len(tokenizer.encode(x)))
    shortened = []

    for row in df.iterrows():

        if row[1]['text'] is None:
            continue

        if row[1]['n_tokens'] > max_tokens:
            shortened += split_into_many(row[1]['text'], tokenizer)

        else:
            shortened.append(row[1]['text'])

    df = pd.DataFrame(shortened, columns=['text'])
    df['n_tokens'] = df.text.apply(lambda x: len(tokenizer.encode(x)))
    df['embeddings'] = df.text.apply(lambda x: openai.Embedding.create(input=x,
                                                                       engine='text-embedding-ada-002')[
        'data'][0]['embedding'])
    # df['embeddings'] = df['embeddings'].apply(eval).apply(np.array)
    return df


def get_existing_context(file_name):
    df = pd.read_csv('processed/embeddings.csv', index_col=0)
    df['embeddings'] = df['embeddings'].apply(eval).apply(np.array)
    return df


def create_context(question, df, max_len=1800, size="ada"):
    q_embeddings = \
    openai.Embedding.create(input=question, engine='text-embedding-ada-002')[
        'data'][0]['embedding']
    df['distances'] = distances_from_embeddings(q_embeddings,
                                                df['embeddings'].values,
                                                distance_metric='cosine')
    returns = []
    cur_len = 0
    for i, row in df.sort_values('distances', ascending=True).iterrows():
        cur_len += row['n_tokens'] + 4
        if cur_len > max_len:
            break
        returns.append(row["text"])

    return "\n\n###\n\n".join(returns)


def answer_question(
        df,
        model="text-davinci-003",
        question="Am I allowed to publish model outputs to Twitter, without a human review?",
        max_len=4000,
        size="ada",
        debug=False,
        max_tokens=max_tokens,
        stop_sequence=None
):
    context = create_context(
        question,
        df,
        max_len=max_len,
        size=size,
    )
    # If debug, print the raw model response
    if debug:
        print("Context:\n" + context)
        print("\n\n")

    try:
        # Create a completions using the questin and context
        response = openai.Completion.create(
            prompt=f"\nContext: {context}\n\n---\n\nQuestion: {question}\nAnswer:",
            temperature=0,
            max_tokens=max_tokens,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            stop=stop_sequence,
            model=model,
        )
        return response["choices"][0]["text"].strip()
    except Exception as e:
        print(e)
        return ""


def execute(context, id, age, prompt):
    prompt = get_prompt(id=id, age=age, prompt=prompt)
    answer = answer_question(context, question=prompt, debug=False)
    return answer


if __name__ == '__main__':
    # context = get_existing_context("processed/embeddings.csv")
    z = """
    Q1. What is the significance of the tuberculin test in determining the presence of tuberculosis?
    Answer 1: The moon is the biggest planet.
    
    Q2. What is the percentage of animals reacting tso the tuberculin test in the Vogelsberg cattle breed?
    Answer 2: 5%
    
    Q3. What is the etiological factor of the various manifestations of tuberculosis?
    Answer 3: tubercle bacilli.

    Q4. What are the three factors necessary for the development of tuberculosis?
    Answer 4: water, fire and air
    
    Q5. What is the importance of the age of the individual in the analysis of a tubercular infection?
    Answer 5: Individual's age
    """
    file_name = "text/tuberculosis.txt"
    texts = read_textfile(file_name)
    df = text_to_df(texts)
    context = get_context_encoding(df)
    answer = execute(context, id=3, age="university student", prompt=z)
    print(answer)
