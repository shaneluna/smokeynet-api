# smokeynet-api

## Getting Started

1. Ensure dependencies installed:
- python3
- make
- docker

2. With git installed, clone project:
   ```
   git clone git@github.com:shaneluna/smokeynet-api.git
   ```

   _Note: You may need to setup an ssh key if first time using git_

3. Change directory into cloned repo:
   ```
   cd smokeynet-api
   ```

4. Create a virtual environment:
   ```
   python -m venv venv
   ```

5. Start virutal environment:<br>
   Linux & Mac:<br>
   ```
   source venv/bin/activate
   ```
   Windows:
   ```
   ./venv/Scripts/activate
   ```

6. Install requirements:
   ```
   pip install -r requirements.txt
   ```

7. Copy `.env.example`, rename to `.env`, and add the API token.<br>

8. Start API for development:
   ```
   make dev

   # the following commands can also be used
   export SYNOPTIC_TOKEN=token
   uvicorn main:app --reload --host=0.0.0.0 --port=8000
   ```

9. API should be accessible by default at:<br>
`http://127.0.0.1:8000/`<br>
`http://127.0.0.1:8000/docs`

## Docker
Build:
```
docker build -t wifire/smokeynet-api .
```

Run:
```
docker run -p 8000:8000 --env-file .env wifire/smokeynet-api
```

API should be accessible by default at `http://127.0.0.1:8000/docs` for the docs.

## Makefile
```
make dev       # Runs local
make build     # Builds docker image
make run       # Runs docker image
```