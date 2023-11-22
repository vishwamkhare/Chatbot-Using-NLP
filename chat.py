import random
import json

import torch
import requests

import spacy
import requests
from coronachatbot import coronachatbot

from model import NeuralNet
from nltk_utils import bag_of_words, tokenize

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

with open('intents.json', 'r') as json_data:
    intents = json.load(json_data)

FILE = "data.pth"
data = torch.load(FILE)

input_size = data["input_size"]
hidden_size = data["hidden_size"]
output_size = data["output_size"]
all_words = data['all_words']
tags = data['tags']
model_state = data["model_state"]

model = NeuralNet(input_size, hidden_size, output_size).to(device)
model.load_state_dict(model_state)
model.eval()

bot_name = "BOT"


def local_get_response(msg):
    sentence = tokenize(msg)
    X = bag_of_words(sentence, all_words)
    X = X.reshape(1, X.shape[0])
    X = torch.from_numpy(X).to(device)

    output = model(X)
    _, predicted = torch.max(output, dim=1)

    tag = tags[predicted.item()]

    probs = torch.softmax(output, dim=1)
    prob = probs[0][predicted.item()]
    if prob.item() > 0.75:
        for intent in intents['intents']:
            if tag == intent["tag"]:
                return random.choice(intent['responses'])

    return "I do not understand..."


nlp = spacy.load("en_core_web_md")

api_key = "648d829da30c83491b16a67402c54fc4"


def get_weather(city_name):
    api_url = "http://api.openweathermap.org/data/2.5/weather?q={}&appid={}".format(
        city_name, api_key)
    response = requests.get(api_url)
    response_dict = response.json()
    weather = response_dict["weather"][0]["description"]
    #print (response_dict)
    if response.status_code == 200:
        degKTemp = response_dict["main"]["temp"]
        degCTemp = degKTemp - 273.15
        degCTemp = round(degCTemp, 1)
        prediction = "In " + city_name + ", the current weather is: " + \
            weather + ".\nThe current Temperature is " + str(degCTemp)
        return prediction
    # weather
    else:
        print('[!] HTTP {0} calling [{1}]'.format(
            response.status_code, api_url))
        return None

#weather = get_weather("London")
# print(weather)


def get_covid_stats(statement):
    covid_country = nlp("Covid stats in a country")
    covid_statement = nlp(statement)
    min_similarity = 0.7
    simil = covid_country.similarity(covid_statement)
    print("similarity " + str(simil))
    country = ''
    if simil >= min_similarity:
        for ent in covid_statement.ents:
            if ent.label_ == "GPE":  # GeoPolitical Entity
                country = ent.text
                break
            else:
                return None
    else:
        return None
    req_url = 'https://covid-19.dataflowkit.com/v1/'+country
    response = requests.get(req_url)
    response_dict = response.json()
    # print(response_dict)
    #print ("country is " +country)
    return "Last Updated:"+response_dict["Last Update"]+"\nTotal Cases:"+response_dict["Total Cases_text"] + "\nTotal Deaths:"+response_dict["Total Deaths_text"]+"\nTotal Recovered:"+response_dict["Total Recovered_text"]


def chatbot(statement):
    # return str(coronachatbot.get_response(statement))

    raw_statement = statement
    weather = nlp("Current weather in a city")
    statement = nlp(statement)
    min_similarity = 0.75
    simil = weather.similarity(statement)
    print("similarity " + str(simil))
    if simil >= min_similarity:
        for ent in statement.ents:
            if ent.label_ == "GPE":  # GeoPolitical Entity
                city = ent.text
                break
            else:
                return "You need to tell me a city to check."

        city_weather = get_weather(city)
        if city_weather is not None:
            # return "In " + city + ", the current weather is: " + city_weather
            return city_weather
        else:
            covid_resp = get_covid_stats(raw_statement)
            if covid_resp is not None:
                return str(covid_resp)
            else:
                # return str(coronachatbot.get_response(raw_statement))
                return str(local_get_response(raw_statement))
        # return "Something went wrong."
    else:
        covid_resp = get_covid_stats(raw_statement)
        if covid_resp is not None:
            return str(covid_resp)
        else:
            # return str(coronachatbot.get_response(raw_statement))
            return str(local_get_response(raw_statement))


def get_response(msg):
    return chatbot(msg)
