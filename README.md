# [leo.might-be.gay](https://leo.might-be.gay)

This repo contains the source code for that website. Suggestions for improvements are very welcome! 
Open an issue or reach out somewhere, my socials are listed in this very site.

# Running this site.

1. Create a virtual environment (optional, but highly recommended) and activate it.

2. Install the `requirements.txt`.

3. Rreate a `config.py` file and fill in the blanks:

```py
LASTFM_USERNAME = "LeoCx1000"

#  Leave empty if you don't want the website to say what you are listening to.
LASTFM_API_KEY = ""

#  Secret from creating a github webhook in your fork settings.
#  Leave empty if you don't want automatic updates via gh webhook.
GITHUB_SECRET = ""  
```

4. Run via `uvicorn run app:app --port 8000 --timeout-graceful-shutdown 1`.