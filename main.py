import requests
from fastapi import FastAPI

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


@app.get("/")
def root():
    return {"message": "Hello World"}


@app.get("/post")
def test():
    quotes = fetch_quotes(5)
    if quotes == 0:
        return {"Error": "Server could not get Kanye quote"}
    return {"quotes": quotes}
