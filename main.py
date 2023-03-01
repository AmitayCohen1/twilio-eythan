
# Summary of the changes:
# 1. Moved the logic to get news articles into a separate function get_news().
# 2. Moved the logic to get stock data into a separate function get_stock_data().
# 3. Created a new function send_sms() to handle sending SMS messages via Twilio.
# 4. Used if __name__ == "__main__": to ensure that the code in the if block is only executed when the script is run directly, and not when it is imported as a module.
# 5. Changed the names of some variables to be more descriptive.
# 6. Replaced hard-coded values with variables where appropriate.
# 7. Removed unnecessary dotenv variables and imports.

import os
from datetime import date, timedelta
import requests
from twilio.rest import Client
from dotenv import load_dotenv
from constants import STOCK, COMPANY_NAME, TWILIO_PHONE_NUMBER

load_dotenv()


NEWS_API_KEY = os.getenv("NEWS_API_KEY")
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
MY_PHONE_NUMBER = os.getenv("MY_PHONE_NUMBER")


def get_news():
    
    yesterday = str(date.today() - timedelta(days=1))
    news_api_key = NEWS_API_KEY
    news_url = "https://newsapi.org/v2/everything"
    news_parameters = {
        "q": COMPANY_NAME,
        "from": yesterday,
        "to": yesterday,
        "sortBy": "popularity",
        "apiKey": news_api_key,
    }
    news_response = requests.get(news_url, params=news_parameters)
    news_response.raise_for_status()
    articles = news_response.json()["articles"]
    three_articles = articles[:3]
    return [f"title: {num['title']}  description: {num['description']}" for num in three_articles]


def get_stock_data():
    yesterday = str(date.today() - timedelta(days=1))
    day_before_yesterday = str(date.today() - timedelta(days=2))
    stock_api_key = ALPHA_VANTAGE_API_KEY
    stock_url = "https://www.alphavantage.co/query"
    stock_parameters = {
        "function": "TIME_SERIES_DAILY_ADJUSTED",
        "symbol": STOCK,
        "apikey": stock_api_key,
    }
    stock_response = requests.get(stock_url, params=stock_parameters)
    stock_response.raise_for_status()
    data = stock_response.json()
    y_close = float(data["Time Series (Daily)"][yesterday]["4. close"])
    b_close = float(data["Time Series (Daily)"]
                    [day_before_yesterday]["4. close"])
    return abs(y_close - b_close) / y_close * 100


def send_sms(messages):
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    for message in messages:
        sms = client.messages.create(
            body=message,
            from_=TWILIO_PHONE_NUMBER,
            to=MY_PHONE_NUMBER
        )
        print(sms.sid)


if __name__ == "__main__":
    percent_change = get_stock_data()
    if percent_change > 1:
        messages = get_news()
        send_sms(messages)
