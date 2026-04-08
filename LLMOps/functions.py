from base64 import urlsafe_b64decode
import json
from tarfile import data_filter
import requests
from bs4 import BeautifulSoup as bs
import logging
import configparser

# Define Config Object
config = configparser.ConfigParser()
config.read('config.ini')

# Read Config Parameters
openweather_api_key = config.get('API_Keys', 'openweather_key')
serper_api_key = config.get('API_Keys', 'serper_key')

def get_geocode(city_name):
    '''
    This function returns the latitude and longitude for a given city name.

    Args:
        city_name: str
    
    Returns:
        dict: latitude and longitude
    '''
    
    api_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city_name}&appid={openweather_api_key}"
    response = requests.get(api_url)

    if response.status_code == 200:
        data = response.json()[0]

        lat, lon = data['lat'], data['lon']
        return json.dumps({'latitude': lat, 'longitude': lon})
    else:
        logging.error("Unable to fetch latitude and longitude")
        return json.dumps({"latitude": "unknown", "longitude": "unknown"})

def get_current_weather(city_name, unit='celsius'):
    '''
    This function returns the weather data for a given latitude and longitude.

    Args:
        city_name: str
        unit: str, default 'celsius'
    
    Returns:
        dict: weather data
    '''

    geocode = json.loads(get_geocode(city_name))
    latitude, longitude = geocode['latitude'], geocode['longitude']

    if latitude == "unknown" or longitude == "unknown":
        logging.error("Latitude and Longitude not found")
        return json.dumps({"forecast": "unknown"})
    else:
        api_url = f"https://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={openweather_api_key}"
        response = requests.get(api_url)

        # conversion factor to convert from kelvin to celsius or fahrenheit
        conversion_factor = 273.15 if unit == 'celsius' else 459.67

        if response.status_code == 200:
            data = response.json()
            logging.info(f'''Weather data fetched successfully for {city_name}: 
                                weather_description: {data['weather'][0]['description']}
                                temp: {int(data['main']['temp'])-conversion_factor}
                                feels_like: {int(data['main']['feels_like'])-conversion_factor}
                                temp_min: {int(data['main']['temp_min'])-conversion_factor}
                                temp_max: {int(data['main']['temp_max'])-conversion_factor}
                                humidity: {data['main']['humidity']}
                                wind_speed: {data['wind']['speed']}
                                clouds: {data['clouds']['all']}
                                visibility: {data['visibility']}
                                ''')
            return json.dumps({'weather_description': data['weather'][0]['description'], 
                    'temperature': int(data['main']['temp'])-conversion_factor, 
                    'temperature_feels_like': int(data['main']['feels_like'])-conversion_factor,
                    'termerature_minimum': int(data['main']['temp_min'])-conversion_factor,
                    'temperature_maximum': int(data['main']['temp_max'])-conversion_factor,
                    'temperature_unit': 'celsius' if unit == 'celsius' else 'fahrenheit',
                    'humidity': data['main']['humidity'], 'humidity_unit': '%',
                    'wind_speed': data['wind']['speed'], 'clouds': data['clouds']['all'], 
                    'visibility': data['visibility'], 'visibility_unit': 'meters'})
        else:
            logging.error("Unable to fetch weather data")
            return json.dumps({"weather_description": "unknown", "temperature": "unknown", "temperature_feels_like": "unknown",
                    "termerature_minimum": "unknown", "temperature_maximum": "unknown", "temperature_unit": "unknown",
                    "humidity": "unknown", "humidity_unit": "unknown", "wind_speed": "unknown", "clouds": "unknown",
                    "visibility": "unknown", "visibility_unit": "unknown"})

def get_latest_news_headlines(limit=10):
    '''
    This function returns the latest news headlines from the Google News.

    Parameters:
        limit: limit to number of headlines
            int, default 10

    Returns:
        str: latest news
    '''
    url = 'https://news.google.com/topics/CAAqKggKIiRDQkFTRlFvSUwyMHZNRGx1YlY4U0JXVnVMVWRDR2dKSlRpZ0FQAQ?hl=en-IN&gl=IN&ceid=IN%3Aen'

    sub_url = 'https://news.google.com'
    response = requests.get(url)

    if response.status_code == 200:
        soup = bs(response.text, 'html.parser')
        news_banners = soup.find_all('c-wiz', class_='PO9Zff Ccj79 kUVvS')[:limit]
        
        # Initialize an empty list to store the headlines and URLs
        headlines=[]
        urls=[]

        # Iterate through each news banner
        for i in range(len(news_banners)):
            # Find the 'a' tag with the specified class within the banner
            a_tag = news_banners[i].find('a', class_='gPFEn')
            if a_tag:
                # Extract the headline text and the href attribute
                headline = a_tag.get_text()
                url = a_tag['href']

                headlines.append(headline)
                urls.append(sub_url+url)

        result = json.dumps({'Headlines': headlines, 'Urls': urls, 'Source': 'Google News'}) if url else json.dumps({'headlines': headlines})

        return result
    else:
        return "Unable to fetch news"

def get_news(query):
    '''
    This function returns the news for a given query from Google search engine.

    Args:
        query: str
    
    Returns:
        dict: news
    '''
    
    url = "https://google.serper.dev/news"
    payload = json.dumps({
    "q": query
    })

    headers = {
    'X-API-KEY': serper_api_key,
    'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    logging.info(f"News fetched for query: {query}")

    # return json
    return json.dumps(response.json())


def internet_search(query):
    '''
    This function returns the search results for a given query from Google search engine.

    Args:
        query: str
    
    Returns:
        dict: search results
    '''
    
    url = "https://google.serper.dev/search"
    payload = json.dumps({
    "q": query
    })

    headers = {
    'X-API-KEY': serper_api_key,
    'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    logging.info(f"Internet Search results fetched for query: {query}")

    # return json
    return json.dumps(response.json())

def set_alarm(time):
    '''
    This function sets an alarm for a given time.

    Args:
        time: str (HH:MM AM/PM)
    
    Returns:
        str: alarm set
    '''
    # to do

    logging.info(f"Alarm set for {time}")

    return f"Alarm set for {time}"

def set_timer(duration):
    '''
    This function sets a timer for a given duration.

    Args:
        duration: int (minutes)
    
    Returns:
        str: timer set
    '''
    # to do

    logging.info(f"Timer set for {duration} minutes")

    return f"Timer set for {duration} minutes"

def create_calendar_event(date, time, event, location=None):
    '''
    This function creates a calendar event for a given date, time and event.

    Args:
        date: str (YYYY-MM-DD)
        time: str (HH:MM AM/PM)
        event: str
        location: str
            default: None
    
    Returns:
        str: event created
    '''
    # to do

    logging.info(f"Event created for {date} at {time} with event: {event}")

    return f"Event created for {date} at {time} with event: {event}"

def create_reminder(time, message):
    '''
    This function creates a reminder for a given time and message.

    Args:
        time: str (HH:MM AM/PM)
        message: str
    
    Returns:
        str: reminder set
    '''
    # to do

    logging.info(f"Reminder set for {time} with message: {message}")

    return f"Reminder set for {time} with message: {message}"

def create_note(note):
    '''
    This function creates a note.

    Args:
        note: str
    
    Returns:
        str: note created
    '''
    # to do

    logging.info(f"New Note created: {note}")

    return f"Note created: {note}"

def get_calendar_events(date):
    '''
    This function returns the calendar events for the day.

    Args:
        date: str (DD-MM-YY)

    Returns:
        dict: calendar events
    '''
    # temp
    data = {
        "kind": "calendar#events",
        "etag": "\"p33j4npab3j4ad0\"",
        "summary": "John Doe's Calendar",
        "updated": "2024-06-30T10:00:00Z",
        "timeZone": "Asia/Kolkata",
        "items": [
            {
            "kind": "calendar#event",
            "etag": "\"2998802117124000\"",
            "id": "1abc2def3ghijklmno4pqrs",
            "status": "confirmed",
            "htmlLink": "https://www.google.com/calendar/event?eid=1abc2def3ghijklmno4pqrs",
            "created": "2024-06-29T16:45:00Z",
            "updated": "2024-06-29T16:45:00Z",
            "summary": "Morning Meeting with Team",
            "description": "Discuss project progress and next steps.",
            "location": "Conference Room 1",
            "creator": {
                "email": "john.doe@example.com",
                "displayName": "John Doe"
            },
            "organizer": {
                "email": "john.doe@example.com",
                "displayName": "John Doe"
            },
            "start": {
                "dateTime": "2024-06-30T09:00:00+05:30"
            },
            "end": {
                "dateTime": "2024-06-30T10:00:00+05:30"
            },
            "iCalUID": "1abc2def3ghijklmno4pqrs@google.com",
            "sequence": 0,
            "reminders": {
                "useDefault": 'true'
            }
            },
            {
            "kind": "calendar#event",
            "etag": "\"2998802117124001\"",
            "id": "2bcde3fgh4ijklmno5pqrs",
            "status": "confirmed",
            "htmlLink": "https://www.google.com/calendar/event?eid=2bcde3fgh4ijklmno5pqrs",
            "created": "2024-06-29T17:00:00Z",
            "updated": "2024-06-29T17:00:00Z",
            "summary": "Lunch with Sarah",
            "description": "Catch up with Sarah over lunch.",
            "location": "Cafe Bistro",
            "creator": {
                "email": "john.doe@example.com",
                "displayName": "John Doe"
            },
            "organizer": {
                "email": "john.doe@example.com",
                "displayName": "John Doe"
            },
            "start": {
                "dateTime": "2024-06-30T12:00:00+05:30"
            },
            "end": {
                "dateTime": "2024-06-30T13:00:00+05:30"
            },
            "iCalUID": "2bcde3fgh4ijklmno5pqrs@google.com",
            "sequence": 0,
            "reminders": {
                "useDefault": 'true'
            }
            },
            {
            "kind": "calendar#event",
            "etag": "\"2998802117124002\"",
            "id": "3cdef4ghi5jklmno6pqrs",
            "status": "confirmed",
            "htmlLink": "https://www.google.com/calendar/event?eid=3cdef4ghi5jklmno6pqrs",
            "created": "2024-06-29T17:30:00Z",
            "updated": "2024-06-29T17:30:00Z",
            "summary": "Client Call",
            "description": "Quarterly check-in with the client.",
            "location": "Online Meeting",
            "creator": {
                "email": "john.doe@example.com",
                "displayName": "John Doe"
            },
            "organizer": {
                "email": "john.doe@example.com",
                "displayName": "John Doe"
            },
            "start": {
                "dateTime": "2024-06-30T15:00:00+05:30"
            },
            "end": {
                "dateTime": "2024-06-30T16:00:00+05:30"
            },
            "iCalUID": "3cdef4ghi5jklmno6pqrs@google.com",
            "sequence": 0,
            "reminders": {
                "useDefault": 'true'
            }
            },
            {
            "kind": "calendar#event",
            "etag": "\"2998802117124003\"",
            "id": "4defg5hij6klmno7pqrs",
            "status": "confirmed",
            "htmlLink": "https://www.google.com/calendar/event?eid=4defg5hij6klmno7pqrs",
            "created": "2024-06-29T18:00:00Z",
            "updated": "2024-06-29T18:00:00Z",
            "summary": "Gym",
            "description": "Workout session.",
            "location": "Local Gym",
            "creator": {
                "email": "john.doe@example.com",
                "displayName": "John Doe"
            },
            "organizer": {
                "email": "john.doe@example.com",
                "displayName": "John Doe"
            },
            "start": {
                "dateTime": "2024-06-30T18:00:00+05:30"
            },
            "end": {
                "dateTime": "2024-06-30T19:00:00+05:30"
            },
            "iCalUID": "4defg5hij6klmno7pqrs@google.com",
            "sequence": 0,
            "reminders": {
                "useDefault": 'true'
            }
            },
            {
            "kind": "calendar#event",
            "etag": "\"2998802117124004\"",
            "id": "5efgh6ijk7lmno8pqrs",
            "status": "confirmed",
            "htmlLink": "https://www.google.com/calendar/event?eid=5efgh6ijk7lmno8pqrs",
            "created": "2024-06-29T18:30:00Z",
            "updated": "2024-06-29T18:30:00Z",
            "summary": "Dinner with Family",
            "description": "Family dinner at home.",
            "location": "Home",
            "creator": {
                "email": "john.doe@example.com",
                "displayName": "John Doe"
            },
            "organizer": {
                "email": "john.doe@example.com",
                "displayName": "John Doe"
            },
            "start": {
                "dateTime": "2024-06-30T20:00:00+05:30"
            },
            "end": {
                "dateTime": "2024-06-30T21:00:00+05:30"
            },
            "iCalUID": "5efgh6ijk7lmno8pqrs@google.com",
            "sequence": 0,
            "reminders": {
                "useDefault": 'true'
            }
            },
            {
            "kind": "calendar#event",
            "etag": "\"2998802117124005\"",
            "id": "6fghi7jkl8mno9pqrs",
            "status": "confirmed",
            "htmlLink": "https://www.google.com/calendar/event?eid=6fghi7jkl8mno9pqrs",
            "created": "2024-06-29T18:45:00Z",
            "updated": "2024-06-29T18:45:00Z",
            "summary": "Meeting with the Board",
            "description": "Quarterly board meeting.",
            "location": "Board Room",
            "creator": {
                "email": "john.doe@example.com",
                "displayName": "John Doe"
            },
            "organizer": {
                "email": "john.doe@example.com",
                "displayName": "John Doe"
            },
            "start": {
                "dateTime": "2024-06-30T10:30:00+05:30"
            },
            "end": {
                "dateTime": "2024-06-30T12:00:00+05:30"
            },
            "iCalUID": "6fghi7jkl8mno9pqrs@google.com",
            "sequence": 0,
            "reminders": {
                "useDefault": 'true'
            }
            },
            {
            "kind": "calendar#event",
            "etag": "\"2998802117124006\"",
            "id": "7ghij8klm9nopqrs",
            "status": "confirmed",
            "htmlLink": "https://www.google.com/calendar/event?eid=7ghij8klm9nopqrs",
            "created": "2024-06-29T19:00:00Z",
            "updated": "2024-06-29T19:00:00Z",
            "summary": "Pomodoro Session",
            "description": "Focus work session.",
            "location": "Home Office",
            "creator": {
                "email": "john.doe@example.com",
                "displayName": "John Doe"
            },
            "organizer": {
                "email": "john.doe@example.com",
                "displayName": "John Doe"
            },
            "start": {
                "dateTime": "2024-06-30T14:00:00+05:30"
            },
            "end": {
                "dateTime": "2024-06-30T14:25:00+05:30"
            },
            "iCalUID": "7ghij8klm9nopqrs@google.com",
            "sequence": 0,
            "reminders": {
                "useDefault": 'true'
            }
            },
            {
            "kind": "calendar#event",
            "etag": "\"2998802117124007\"",
            "id": "8hijk9lmno0pqrs",
            "status": "confirmed",
            "htmlLink": "https://www.google.com/calendar/event?eid=8hijk9lmno0pqrs",
            "created": "2024-06-29T19:15:00Z",
            "updated": "2024-06-29T19:15:00Z",
            "summary": "Meeting with the Design Team",
            "description": "Discuss design updates and feedback.",
            "location": "Design Studio",
            "creator": {
                "email": "john.doe@example.com",
                "displayName": "John Doe"
            },
            "organizer": {
                "email": "john.doe@example.com",
                "displayName": "John Doe"
            },
            "start": {
                "dateTime": "2024-06-30T11:00:00+05:30"
            },
            "end": {
                "dateTime": "2024-06-30T12:00:00+05:30"
            },
            "iCalUID": "8hijk9lmno0pqrs@google.com",
            "sequence": 0,
            "reminders": {
                "useDefault": 'true'
            }
            },
            {
            "kind": "calendar#event",
            "etag": "\"2998802117124008\"",
            "id": "9ijkl0mnpqrspqs",
            "status": "confirmed",
            "htmlLink": "https://www.google.com/calendar/event?eid=9ijkl0mnpqrspqs",
            "created": "2024-06-29T19:30:00Z",
            "updated": "2024-06-29T19:30:00Z",
            "summary": "Lunch",
            "description": "Quick lunch break.",
            "location": "Office Cafeteria",
            "creator": {
                "email": "john.doe@example.com",
                "displayName": "John Doe"
            },
            "organizer": {
                "email": "john.doe@example.com",
                "displayName": "John Doe"
            },
            "start": {
                "dateTime": "2024-06-30T13:00:00+05:30"
            },
            "end": {
                "dateTime": "2024-06-30T13:30:00+05:30"
            },
            "iCalUID": "9ijkl0mnpqrspqs@google.com",
            "sequence": 0,
            "reminders": {
                "useDefault": 'true'
            }
            },
            {
            "kind": "calendar#event",
            "etag": "\"2998802117124009\"",
            "id": "0jklmnpqrstpqs",
            "status": "confirmed",
            "htmlLink": "https://www.google.com/calendar/event?eid=0jklmnpqrstpqs",
            "created": "2024-06-29T19:45:00Z",
            "updated": "2024-06-29T19:45:00Z",
            "summary": "Brainstorming Session",
            "description": "Generate new ideas for the upcoming project.",
            "location": "Meeting Room B",
            "creator": {
                "email": "john.doe@example.com",
                "displayName": "John Doe"
            },
            "organizer": {
                "email": "john.doe@example.com",
                "displayName": "John Doe"
            },
            "start": {
                "dateTime": "2024-06-30T16:30:00+05:30"
            },
            "end": {
                "dateTime": "2024-06-30T17:30:00+05:30"
            },
            "iCalUID": "0jklmnpqrstpqs@google.com",
            "sequence": 0,
            "reminders": {
                "useDefault": 'true'
            }
            },
            {
            "kind": "calendar#event",
            "etag": "\"2998802117124010\"",
            "id": "1klmnpqrstupqs",
            "status": "confirmed",
            "htmlLink": "https://www.google.com/calendar/event?eid=1klmnpqrstupqs",
            "created": "2024-06-29T20:00:00Z",
            "updated": "2024-06-29T20:00:00Z",
            "summary": "Pomodoro Session",
            "description": "Focus work session.",
            "location": "Home Office",
            "creator": {
                "email": "john.doe@example.com",
                "displayName": "John Doe"
            },
            "organizer": {
                "email": "john.doe@example.com",
                "displayName": "John Doe"
            },
            "start": {
                "dateTime": "2024-06-30T18:30:00+05:30"
            },
            "end": {
                "dateTime": "2024-06-30T18:55:00+05:30"
            },
            "iCalUID": "1klmnpqrstupqs@google.com",
            "sequence": 0,
            "reminders": {
                "useDefault": 'true'
            }
            },
            {
            "kind": "calendar#event",
            "etag": "\"2998802117124011\"",
            "id": "2lmnpqrstupqs",
            "status": "confirmed",
            "htmlLink": "https://www.google.com/calendar/event?eid=2lmnpqrstupqs",
            "created": "2024-06-29T20:15:00Z",
            "updated": "2024-06-29T20:15:00Z",
            "summary": "Pomodoro Session",
            "description": "Focus work session.",
            "location": "Home Office",
            "creator": {
                "email": "john.doe@example.com",
                "displayName": "John Doe"
            },
            "organizer": {
                "email": "john.doe@example.com",
                "displayName": "John Doe"
            },
            "start": {
                "dateTime": "2024-06-30T19:00:00+05:30"
            },
            "end": {
                "dateTime": "2024-06-30T19:25:00+05:30"
            },
            "iCalUID": "2lmnpqrstupqs@google.com",
            "sequence": 0,
            "reminders": {
                "useDefault": 'true'
            }
            }
        ]
    }

    logging.info("Calendar events fetched")

    return json.dumps(data)

def get_reminders(date):
    '''
    This function returns the reminders for the day.

    Args:
        date: str (DD-MM-YY)

    Returns:
        dict: reminders
    '''
    # temp
    data = {
        "kind": "tasks#tasks",
        "etag": "\"b12345abcd34efg5678\"",
        "items": [
            {
            "kind": "tasks#task",
            "id": "1abc2def3ghijklmno4pqrs",
            "etag": "\"2998802117124000\"",
            "title": "Buy gifts for Jenny's birthday",
            "updated": "2024-06-30T10:00:00Z",
            "selfLink": "https://www.googleapis.com/tasks/v1/lists/@default/tasks/1abc2def3ghijklmno4pqrs",
            "position": "00000000000000000000",
            "notes": "Don't forget to buy a card as well.",
            "status": "needsAction",
            "due": "2024-07-01T00:00:00.000Z"
            },
            {
            "kind": "tasks#task",
            "id": "2bcde3fgh4ijklmno5pqrs",
            "etag": "\"2998802117124001\"",
            "title": "Congratulate Jason on his anniversary",
            "updated": "2024-06-30T11:00:00Z",
            "selfLink": "https://www.googleapis.com/tasks/v1/lists/@default/tasks/2bcde3fgh4ijklmno5pqrs",
            "position": "00000000000000000001",
            "notes": "Send a message or call him.",
            "status": "needsAction",
            "due": "2024-06-30T12:00:00.000Z"
            }
        ]
    }

    logging.info("Reminders fetched")

    return json.dumps(data)