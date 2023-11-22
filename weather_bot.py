import requests

import spacy
import requests
from chatbot import chatbot

# return str(chatbot.get_response(userText))
nlp = spacy.load("en_core_web_md")

api_key = "648d829da30c83491b16a67402c54fc4"

def get_weather(city_name):
	api_url = "http://api.openweathermap.org/data/2.5/weather?q={}&appid={}".format(city_name, api_key)
	response = requests.get(api_url)
	response_dict = response.json()
	weather = response_dict["weather"][0]["description"]

	if response.status_code == 200:
		return weather
	else:
		print('[!] HTTP {0} calling [{1}]'.format(response.status_code, api_url))
		return None

#weather = get_weather("London")
#print(weather)


def chatbot(statement):
  weather = nlp("Current weather in a city")
  statement = nlp(statement)
  min_similarity = 0.5
  simil = weather.similarity(statement)
  print ("similarity " + str(simil) )
  if simil >= min_similarity:
    for ent in statement.ents:
      if ent.label_ == "GPE": # GeoPolitical Entity
        city = ent.text
        break
      else:
        return "You need to tell me a city to check."

    city_weather = get_weather(city)
    if city_weather is not None:
      return "In " + city + ", the current weather is: " + city_weather
    else:
      return "Something went wrong."
  else:
    return str(chatbot.get_response(statement))
    #return "Sorry I don't understand that. Please rephrase your statement."
	

response = chatbot("Is it going to rain in Rome today?")
print(response)