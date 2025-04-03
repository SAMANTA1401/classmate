from langchain_community.utilities import GoogleSerperAPIWrapper

import os
from dotenv import load_dotenv
load_dotenv()
os.environ["SERPER_API_KEY"] = os.environ["SERPER_API_KEY"]




class SearchToolMasterBot:
    def __init__(self):
        self.url = "https://google.serper.dev/search"
        self.headers = {
            "X-API-KEY": os.environ["SERPER_API_KEY"],
            "Content-Type": "application/json"
        }

    def run(self, query):
        return self.search.run(query)