import requests
import json

if __name__ == "__main__":
    posts_dict = json.loads(requests.get("http://127.0.0.1:8000/post/?all=True").text)
    print(posts_dict)