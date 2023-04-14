from collections import defaultdict
import pandas as pd
import numpy as np
import csv
import json
import spacy
import random
from tqdm import tqdm
import re
import heapq
import matplotlib.pyplot as plt
import requests

file1 = 'C:\\Users\\User\\Desktop\\INTENS\\Zadatak\\Zadatak\\descriptive_attributes.csv'
file2 = 'C:\\Users\\User\\Desktop\\INTENS\\Zadatak\\Zadatak\\numeric_atributes.csv'

def merge_2_files(file1,file2):

    print("Merging files.")
    df1 = pd.read_csv(file1, dtype = {'movieID': str, 'titleType': str, 'primaryTitle': str, 'originalTitle': str, 'genres': str})
    df2 = pd.read_csv(file2, dtype = {'movieID': str, 'isAdult': int, 'startYear': int,'endYear': object, 'runtimeMinutes': int, 'averageRating': float, 'numVotes': float, 'isGood': object})

    # Merge the two dataframes based on the common ID field
    merged_df = pd.merge(df1, df2, on='movieID', how = "inner")

    # Save the merged dataframe to a new CSV file
    merged_df.to_csv('merged_file.csv', index=False)
    merged_file = 'merged_file.csv'
    print("Merged 2 files into merged_file.csv")
    return merged_file

def store_data(merged_file):
    with open(merged_file,"r",encoding="utf8") as csvfile:
        reader = csv.reader(csvfile)
        next(reader)
        data = []
        for row in reader:
            data.append({'movieID': row[0],
                        'titleType': row[1], 
                        'primaryTitle': row[2], 
                        'originalTitle': row[3],
                        'genres': row[4], 
                        'isAdult': int(row[5]), 
                        'startYear': int(row[6]),
                        'endYear': int(row[7]) if isinstance(row[7],int) else np.nan, 
                        'runtimeMinutes': int(row[8]),
                        'averageRating': float(row[9]) if row[9] else None, 
                        'numVotes': float(row[10]) if row[10] else None, 
                        'isGood': bool(row[11]) if row[11] else None})
    print("Stored data.")
    return data

def process_data(data):
    emptyIsGoodFields = 0
    selected_movies = [["movieID","titleType","primaryTitle","originalTitle","genres","isAdult","startYear","endYear","runtimeMinutes","averageRating","num Votes","isGood"]]
    averageRatings = []
    for field in data:
        if field['isGood'] == None:
            emptyIsGoodFields += 1
        if field['averageRating'] == None:
            field['averageRating'] = random.uniform(0, 10)
        if field['startYear'] > 2000 and field['averageRating'] > 3:
            selected_movies.append(list(field.values()))
        averageRatings.append(field['averageRating'])
    print("Added values in empty averageRating fields.")
    return selected_movies,averageRatings,emptyIsGoodFields

def draw_histogram(averageRatings):
    plt.hist(averageRatings,10,facecolor='#2ab0ff', edgecolor='#e0e0e0',linewidth=0.5, alpha=0.7)
    plt.title('Average Rating', fontsize=12)
    plt.xlabel('Distribution', fontsize=10)
    plt.ylabel('Frequency', fontsize=10)
    plt.savefig("histogram.png")
    #plt.show()
    print("Histogram saved as histogram.png.")
    return

def write_selected_movies(selected_movies):  
    with open("movies.csv","w",encoding='utf-8',newline = '') as file:

        print(f"Writing movies made after year 2000 with rating above 3 in movies.txt. (Count : {len(selected_movies)}) ")
        writer = csv.writer(file)
        file.write("There are " + str(len(selected_movies)) + " of movies that were made after year 2000. and with average rating above 3.\n")
        for row in tqdm(selected_movies):
            writer.writerow(row)
        file.close()

def calculate_and_write_average_by_title(data):
    titleTypesRatings = defaultdict(list)
    writer_data = [["title","rating"]]
    for row in data:
        if row['titleType'] not in titleTypesRatings:
            titleTypesRatings[row['titleType']] = [1,row['averageRating']]
        else:
            titleTypesRatings[row['titleType']][0] += 1
            titleTypesRatings[row['titleType']][1] += row['averageRating']

    for type in titleTypesRatings:
        titleTypesRatings[type] = round(titleTypesRatings[type][1] / titleTypesRatings[type][0], 2)


    print("Calculated average ratings for movie types.")
    for title in titleTypesRatings:
        writer_data.append([title,titleTypesRatings[title]])
    
    with open('titles_ratings.csv', 'w',encoding="utf-8", newline='') as f:
        writer = csv.writer(f)
        print("Writing titles and their average ratings into titles_ratings.csv.")
        for row in tqdm(writer_data):
            writer.writerow(row)

def calculate_similarity(data):

    nlp = spacy.load('en_core_web_lg')
    nlp.disable_pipes(*[pipe for pipe in nlp.pipe_names if pipe != "tagger" and pipe != "parser"])

    cmp = nlp("The French Connection")
    movienames = [row['primaryTitle'] for row in data]
    movienames_nlp = []
    similarities = []
    
    SimilarityDict = defaultdict(float)

    print("Adding nlp to list")
    for doc in tqdm(nlp.pipe(movienames)):
        movienames_nlp.append(doc)

    print("Calculating simularities")
    for i in tqdm(range(len(movienames_nlp))):
        if(movienames_nlp[i].has_vector):
            similarities.append(max(round(movienames_nlp[i].similarity(cmp)*100,1),0))
        else:
            similarities.append(0)

    print("Storing simularities in data")
    for i in tqdm(range(len(data))):
        data[i]['similarities'] = similarities[i]      

    for i in range(len(movienames)):
        SimilarityDict[movienames[i]] = similarities[i]
    
    ten_most_similar = heapq.nlargest(10, SimilarityDict.items(), key=lambda x: x[1])

    return SimilarityDict,ten_most_similar,similarities

def count_and_write_words(data):

    uniqueWords = defaultdict(int)
    write_data = [["Word","Count"]]
    for row in data:
        primary_title = re.findall(r'\w+', row['primaryTitle'])
        original_title = re.findall(r'\w+', row['originalTitle'])

        for word in primary_title:
            uniqueWords[word] += 1
        for word in original_title:
            uniqueWords[word] += 1
    
    for word in uniqueWords:
        write_data.append([word,uniqueWords[word]])

    with open('words.csv', 'w',encoding="utf-8", newline='') as f:
        writer = csv.writer(f)
        print("Writing words and their counts into words.csv.")
        for row in tqdm(write_data):
            writer.writerow(row)

def add_similar_and_extract_10(filename,similarities,ten_most_similar):
    
    df = pd.read_csv(filename)
    print("Writing similarities to with_similarities.csv.")
    df['similarity %'] = tqdm(similarities)
    df.to_csv('with_similarities.csv', index=False)
    
    
    write_data = [["primaryTitle","similarity %"]]
    for i in range(len(ten_most_similar)):
        write_data.append([ten_most_similar[i][0],ten_most_similar[i][1]])
    
    print("Writing 10 most similar into most_similar.csv.")
    with open("most_similar.csv","w",newline='') as file:
        writer = csv.writer(file)
        for row in tqdm(write_data):
            writer.writerow(row)

def find_usd_rate_float():
    
    response = requests.get("https://api.coindesk.com/v1/bpi/currentprice.json")
    usd_rf = response.json()["bpi"]["USD"]["rate_float"]
    print("Rate float of USD is",usd_rf)

    return usd_rf

#merging 2 files
merged_file = merge_2_files(file1,file2)

#extracting data
data = store_data('merged_file.csv')

#processing data
selected_movies,averageRatings,emptyIsGoodFields = process_data(data)
print("IsGood does not have value in", emptyIsGoodFields, "rows.")

#writing selected movies to movies.txt
write_selected_movies(selected_movies)

#drawing histogram
draw_histogram(averageRatings)

#calculating average rating based on title of movie
calculate_and_write_average_by_title(data)

#calculating simularity of primaryTitles with "The French Connection"
SimilarityDict,ten_most_similar,similarities = calculate_similarity(data)

#adding similarities on merged file in with_simularities.csv and creating new file with 10 with most simularity in most_simular.csv
add_similar_and_extract_10("merged_file.csv",similarities,ten_most_similar)

#counting and writing words in words.csv
count_and_write_words(data)

#find usd rate float from adress "https://api.coindesk.com/v1/bpi/currentprice.json"
find_usd_rate_float()