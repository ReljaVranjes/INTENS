import pandas as pd
import re
from collections import defaultdict
import csv

def process_tarrifs():

    for i in range(len(TariffNumber)):
        if len(TariffNumber[i]) == 9:
            TariffNumber[i] = "0" + TariffNumber[i]

    #arrange
    Chapter,Heading,Subheading,DutyRate = [],[],[],[]
    for num in TariffNumber:
        Chapter.append(num[:2])
        Heading.append(num[:4])
        Subheading.append(num[:6])
        DutyRate.append(num[:8])
    
    return Chapter,Heading,Subheading,DutyRate

def get_words_and_counts(dict):

    UniqueWords = [] #list of words that appear in all descriptions
    TotalCount = defaultdict(int) #count of how many times word has occured across all descriptions
    IDs = defaultdict(str)
    
    for i in range(len(dict)):
        
        Description[i] = Description[i].lower()
        res = re.findall(r'\w+', Description[i])
        Description[i] = res
        for word in Description[i]:
            TotalCount[word] += 1
            if word not in UniqueWords:
                UniqueWords.append(word)

    for i in range(1,len(UniqueWords)+1):
        IDs[UniqueWords[i-1]] = i
    return UniqueWords,TotalCount,IDs

def store_data(dict_of_excel):
    data = []
    for i in range(len(dict_of_excel)):
        data.append({
                    'TariffNumber': TariffNumber[i],
                    'Chapter': Chapter[i],
                    'Heading': Heading[i],
                    'Subheading': Subheading[i],
                    'DutyRate': DutyRate[i],
                    'Tariff': TariffNumber[i],
                    'Words': Description[i]
                })
    return data

def count_word_occurrences(data, word):
    chapter_max_counts = defaultdict(int)
    heading_max_counts = defaultdict(int)
    subheading_max_counts = defaultdict(int)
    duty_rate_max_counts = defaultdict(int)
    tariff_max_counts = defaultdict(int)
    for row in data:
        chapter = row['Chapter']
        heading = row['Heading']
        subheading = row['Subheading']
        duty_rate = row['DutyRate']
        tariff = row['Tariff']
        words = row['Words']
        if word in words:
            chapter_max_counts[chapter] += 1
            heading_max_counts[heading] += 1
            subheading_max_counts[subheading] += 1
            duty_rate_max_counts[duty_rate] += 1
            tariff_max_counts[tariff] += 1
    
    return chapter_max_counts, heading_max_counts, subheading_max_counts, duty_rate_max_counts, tariff_max_counts

def summary(data,word):

    chapter_max_counts, heading_max_counts, subheading_max_counts, duty_rate_max_counts, tariff_max_counts = count_word_occurrences(data,word)

    unique_chapter_counts = len(chapter_max_counts)
    chapter_max_counts = max(chapter_max_counts.values())

    unique_heading_counts = len(heading_max_counts)
    heading_max_counts = max(heading_max_counts.values())
    
    unique_subheading_counts = len(subheading_max_counts)
    subheading_max_counts = max(subheading_max_counts.values())
    
    unique_duty_rate_counts = len(duty_rate_max_counts)
    duty_rate_max_counts = max(duty_rate_max_counts.values())
   
    unique_tariff_counts = len(tariff_max_counts)
    tariff_max_counts = max(tariff_max_counts.values())

    return [IDs[word],word,TotalCount[word],chapter_max_counts,unique_chapter_counts,heading_max_counts,unique_heading_counts,subheading_max_counts,unique_subheading_counts,duty_rate_max_counts,unique_duty_rate_counts,tariff_max_counts,unique_tariff_counts]

def write_to_file(UniqueWords):

    header = ['Id', 'Word', 'Total Count', 'Single Chapter Max-Count','Unique Chapter Count','Single Heading Max-Count','Unique Heading Count','Single Sub Heading Max-Count', 'Unique Sub Heading Count','Single Duty Rate Max Count', 'Unique Duty Rate Count', 'Single Tariff Max Count', 'Unique Tariff Count']
    data_to_write = []

    for i in range(len(UniqueWords)):
        data_to_write.append(summary(data,UniqueWords[i]))

    with open('word_statistics.csv', 'w', encoding='UTF8',newline = '') as f:
        writer = csv.writer(f)

        # write the header
        writer.writerow(header)

        # write the data
        writer.writerows(data_to_write)

excel_file = pd.read_excel(r"C:\\Users\\User\\Desktop\\INTENS\\WSC_Python\\WSC_Python\\WSC Input.xlsx")

dict_of_excel = excel_file.to_dict()
Description = list(dict_of_excel["Description"].values())
TariffNumber = list((dict_of_excel["TariffNumber"].values()))
TariffNumber = [str(x) for x in TariffNumber]

#convert numbers to strings and if not set them to length 10,arrange in Chapters,Subheadings..
Chapter,Heading,Subheading,DutyRate = process_tarrifs()

#get unique words, total count and custom id for each
UniqueWords,TotalCount,IDs = get_words_and_counts(dict_of_excel)

#store data from excel
data = store_data(dict_of_excel)

#write data in word_statistics.csv
write_to_file(UniqueWords)
