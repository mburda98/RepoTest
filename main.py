import requests
from fastapi import FastAPI
from fastapi.templating import Jinja2Templates

kanyeUrl = "https://api.kanye.rest/"

sentimUrl = "https://sentim-api.herokuapp.com/api/v1/"
headersSentim = {"Accept": "application/json", "Content-Type": "application/json"}

app = FastAPI()


def fetch_quotes(number):
    quotes = []
    while len(quotes) != number:
        try:
            res = requests.get(kanyeUrl).json()
            if not res["quote"]:
                return 0
        except:
            print("Server could not get Kanye quote correctly")
            return 0
        # Check if quote is unique
        if not (res["quote"] in quotes):
            quotes.append(res["quote"])
    return quotes


def analyse_quotes(quotes):
    analyzed_quotes = []
    for quote in quotes:
        try:
            res = requests.post(sentimUrl, headers=headersSentim, json={"text": quote}).json()
            if not res["result"] or not res["sentences"]:
                return 0
        except:
            print("Server could not analyse quote")
            return 0
        analyzed_quotes.append({"quote": quote, "result": res["result"]})
    return analyzed_quotes


def find_extreme_quote(quotes):
    extreme = ""
    extreme_val = -1
    for quote in quotes:
        if abs(quote["result"]["polarity"]) > extreme_val:
            extreme = quote["quote"]
            extreme_val = quote["result"]["polarity"]
    return {"quote": extreme, "value": extreme_val}


@app.get("/")
def root():
    return {"message": "Hello World"}


@app.get("/post/{number}")
async def test(number: int):
    if number < 5 or number > 20:
        return {"Error": "Inserted number must be between 5 and 20"}
    quotes = fetch_quotes(number)
    if quotes == 0:
        return {"Error": "Server could not get Kanye quote"}
    analyzed = analyse_quotes(quotes)
    if analyzed == 0:
        return {"Error": "Server could not analyse quotes"}
    extreme_quote = find_extreme_quote(analyzed)
    return {"quotes": analyzed, "extreme": extreme_quote}
