# Final Year Project NYT Crawler
## Setup
Make sure python 3.6 and virtualenv are installed and that the URL pointing to the common repository is replaced by your own URL.

Run the following:
```sh
python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt
```

## Files Required
Please add all these files to your folder with the missing parts filled in.
### set_env.sh
```sh
source ./venv/bin/activate
export PYTHON_ENV="DEVELOPMENT" # DEVELOPMENT / PRODUCTION

# Secrets (Add your keys)
export NYT_API_KEY=""
export NYT_API_SECRET=""

# Celery
export BROKER_URL="amqp://guest:guest@localhost:5672"
```
