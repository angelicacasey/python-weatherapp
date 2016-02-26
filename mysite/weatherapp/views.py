from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse
import requests
import datetime

class CurrentWeather:
    def __init__(self, temp, condition, humidity, city):
        self.temp = temp
        self.condition = condition
        self.humidity = humidity
        self.foundCity = city

class DailyForecast:
    def __init__(self, date, condition, highTemp, lowTemp):
        self.date = date
        self.condition = condition
        self.highTemp = highTemp
        self.lowTemp = lowTemp

# Create your views here.
def index(request):
	template = loader.get_template('weatherapp/index.html')
	context = {
	    'current_city': '',
        'message': '',
	    'todayWeather': ''
	}

	return HttpResponse(template.render(context, request))

def getWeather(request):
    city = request.POST['searchCity']
    cityWeather = retrieveWeatherData(city)
    context = {
        'current_city': city,
        'message': '',
	    'todayWeather': cityWeather['currentWeather'],
	    'fiveDayForecast': cityWeather['fiveDayForecast']
    }
    if (request.META.get('CONTENT_TYPE') == 'application/json'):
        return HttpResponse(context)
    else:
        return render(request, 'weatherapp/index.html', context)
    
def retrieveWeatherData(city):
    currentWeather = getTodaysWeather(city)
    forecastList = getFiveDayForecast(city)
    cityWeather = {
        'currentWeather': currentWeather,
        'fiveDayForecast': forecastList[0:5]
    }
    return cityWeather
    
def getTodaysWeather(city):
    currentWeather = ''
    url = "http://api.openweathermap.org/data/2.5/weather"
    cityInUs = city + ',us'
    payload = {'q':cityInUs, 'units': 'imperial', 'APPID': '505dd7f99bd3bc4b9b1cd29c13ff4dad'}
    response = requests.get(url, payload)
    foundCity = ''
    if (response.ok):
        data = response.json()
        # if the city returned is not the city passed in, then save off
        # the city name to display what was found
        if (data['name'] != city):
            foundCity = data['name']
        condition = data['weather'][0]['main']
        temp = data['main']['temp']
        tempstr = str(int(temp))
        humidity = str(data['main']['humidity']) + '% Humidity'
        currentWeather = CurrentWeather(tempstr, condition, humidity, foundCity)    
    return currentWeather
    
def getFiveDayForecast(city):
    forecastList = []
    url = "http://api.openweathermap.org/data/2.5/forecast"
    iconUrl = "http://openweathermap.org/img/w/"
    cityInUs = city + ',us'
    payload = {'q':cityInUs, 'units': 'imperial', 'APPID': '505dd7f99bd3bc4b9b1cd29c13ff4dad'}
    response = requests.get(url, payload)
    if (response.ok):
        data = response.json()
        dataLst = data['list']
        currentDateStr = ''
        highTemp = 0
        lowTemp = 999
        condition = ''
        # loop through all the three hour forecasts.  Keep track of the
        # high and low temps.  Find the condition at 3pm. (Note: the condition
        # at noon will be a 'night' icon so look at the 3pm which is the first 
        # day icon)
        for fcast in dataLst:
            currentDate = datetime.datetime.fromtimestamp(fcast['dt'])
            if (currentDate.time().hour > 12 and currentDate.time().hour < 18):
                condition = iconUrl + fcast['weather'][0]['icon'] + '.png'
            dateStr = currentDate.strftime('%b-%d')
            if (currentDateStr == ''):
                currentDateStr = dateStr
            if (currentDateStr != dateStr):
                if (condition != ''):
                    forecast = DailyForecast(currentDateStr, condition, str(int(highTemp)), str(int(lowTemp)))
                    forecastList.append(forecast)
                currentDateStr = dateStr
                highTemp = 0
                lowTemp = 999
            else:
                temp = fcast['main']['temp']
                if (temp < lowTemp):
                    lowTemp = temp
                if (temp > highTemp):
                    highTemp = temp

    forecast = DailyForecast(currentDateStr, condition, str(int(highTemp)), str(int(lowTemp)))
    forecastList.append(forecast)
       
    return forecastList        
