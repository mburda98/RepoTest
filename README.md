# RepoTest

## General info
Solution for qualifying task. Project is created with Python FastAPI. 
View DEMO at: https://test-kanye-app.herokuapp.com/

App fetches quotes of Kanye West and calculate their polarity through public open REST API: https://sentim-api.herokuapp.com/

Then app finds the most extreme quote (polarity the closest to negative or positive 1).
## Setup
To run it on local machine:
```
$ pip install -r /path/to/requirements.txt
$ uvicorn main:app
```