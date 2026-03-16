import google.generativeai as genai

genai.configure(api_key="AIzaSyCaYTvjkvyyK3SZ4lUcy3XsxU3-qYidbGg")

for model in genai.list_models():
    print(model.name)