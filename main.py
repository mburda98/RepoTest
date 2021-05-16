import requests
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
import re

from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

kanyeUrl = "https://api.kanye.rest/"

sentimUrl = "https://sentim-api.herokuapp.com/api/v1/"
headersSentim = {"Accept": "application/json", "Content-Type": "application/json"}

app = FastAPI()

app.mount("/static", StaticFiles(directory="client"), name="client")
templates = Jinja2Templates(directory="client")


# Function to fetch quotes from kanye.rest API
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


# Function to send quotes through sentim API and make custom array quotes
def analyse_quotes(quotes):
    merged = ""
    # Remember how many sentences was in every quote
    nr_sentences = []
    for i in range(0, len(quotes)):
        nr_sentences.append(len(re.split(r"(?<=[^A-Z].[.?]) +(?=[A-Z])", quotes[i])))
    # Merging all quotes into one paragraph to avoid multiple requests to sentim API
    for quote in quotes:
        if quote.endswith("."):
            merged += quote + " "
        else:
            merged += quote + ". "
    analyzed_quotes = []
    try:
        res = requests.post(sentimUrl, headers=headersSentim, json={"text": merged}).json()
        if not res["result"] or not res["sentences"]:
            return 0
    except:
        print("Server could not analyse quote")
        return 0
    # Splitting response into single quotes and calculating average polarity for each quote
    current = 0
    for nr in nr_sentences:
        merged_quote = ""
        sum_polarity = 0
        for i in range(current, current + nr):
            merged_quote += " " + res["sentences"][i]["sentence"]
            sum_polarity += res["sentences"][i]["sentiment"]["polarity"]
        analyzed_quotes.append({"quote": merged_quote, "result": round(sum_polarity/nr, 2)})
        current += nr
    return analyzed_quotes


# Function to find the most positive or negative quote
def find_extreme_quote(quotes):
    extreme = ""
    extreme_val = 0
    for quote in quotes:
        if abs(quote["result"]) >= abs(extreme_val):
            extreme = quote["quote"]
            extreme_val = quote["result"]
    return {"quote": extreme, "value": extreme_val}


# Home page
@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


# Route to fetch set of random quotes
@app.get("/post/{number}")
async def test(number: str):
    try:
        number = int(number)
    except:
        raise HTTPException(status_code=404, detail="It's not a number")
    if number < 5 or number > 20:
        raise HTTPException(status_code=404, detail="Inserted number must be between 5 and 20")
    quotes = fetch_quotes(number)
    if quotes == 0:
        raise HTTPException(status_code=500, detail="Server could not get Kanye quote")
    analyzed = analyse_quotes(quotes)
    if analyzed == 0:
        raise HTTPException(status_code=500, detail="Server could not analyse quotes")
    extreme_quote = find_extreme_quote(analyzed)
    return {"quotes": analyzed, "extreme": extreme_quote}

