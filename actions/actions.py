# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"
#
# class ActionHelloWorld(Action):
#     def name(self) -> Text: # [INFO]: tied with domain.yml -> actions
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]: # [INFO]: Dict[Text, Any] -> dict
#         dispatcher.utter_message(text="Hello World!")
#         return [] # [INFO]: can return events as lists


import os

from typing import Any, Text, Dict, List # [INFO]: for type hinting (optional)

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from pymongo import MongoClient

# import openai
# from openai import OpenAI

import google.generativeai as genai
from google.api_core import exceptions as google_exceptions

# from dotenv import load_dotenv # [INFO]: not needed as we are using .keys folder (temporarily)


class ActionRecommendProducts(Action):
    def name(self) -> Text:
        return "action_recommend_products"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        skin_type = tracker.get_slot("skin_type")
        skin_concern = tracker.get_slot("skin_concern")

        recommendations = self.get_product_recommendations(skin_type, skin_concern) # [INFO]: local function binded to class

        dispatcher.utter_message(text=f"Here are some recommended products for {skin_concern}: {recommendations}")
        return []

    def get_product_recommendations(self, skin_type, skin_concern): # [NOTE]: reqs. to be in sync with recommendation system
        # Replace with actual logic to fetch recommendations
        return "1. Cleanser A, 2. Moisturizer B, 3. Sunscreen C"


class ActionFetchIngredientInfo(Action):
    def name(self) -> Text:
        return "action_fetch_ingredient_info"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        ingredient = tracker.get_slot("ingredient")
        benefits, skin_types = self.get_ingredient_info(ingredient)

        dispatcher.utter_message(
            text=f"The ingredient {ingredient} is known for {benefits}. It is suitable for {skin_types} skin types."
        )
        return []

    def get_ingredient_info(self, ingredient):
        # Replace with actual logic to fetch ingredient details
        return "hydrating properties", "dry, normal, and combination"


class ActionSayPhone(Action):
    def name(self) -> Text:
        return "action_say_phone"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]):
        phone = tracker.get_slot("phone")

        if not phone :
            dispatcher.utter_message(text="Sorry i dont know your phone number ")
        else :
            dispatcher.utter_message(text=f"Your phone number is {phone} :) ")

        return []


class ActionSaySkinConcern(Action):
    def name(self) -> Text: # tied with domain.yml -> actions
        return "action_say_skin_concern"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]):
        skin_concern = tracker.get_slot("skin_concern")

        if not skin_concern :
            dispatcher.utter_message(text="Sorry i dont know your skin concern ")
        else :
            dispatcher.utter_message(text=f"Your skin concern is {skin_concern} :) ")

        return []


# class ActionFallbackToChatGPT(Action): # [ISSUE]: too many requests to OpenAI API, rate limit exceeded -> WHY?
#     def name(self):
#         return "action_fallback_to_chatgpt"

#     def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict):
#         user_message = tracker.latest_message.get("text")
#         try:
#             with open(os.path.join('.keys', 'OPENAI_KEY')) as f: # [INFO]: CWD is main project folder
#                 OPENAI_API_KEY = f.read().strip()

#             client = OpenAI(
#                  api_key=OPENAI_API_KEY,  # default method: os.environ.get("OPENAI_API_KEY")
#             )
#             response =  client.chat.completions.create(
#                 model="gpt-4o-mini", # others: "gpt-3.5-turbo", "gpt-4o-mini", "gpt-4o"
#                 messages=[ # [NOTE]: multiple messages or there structure might be the issue
#                     {"role": "system", "content": "You are a helpful assistant."},
#                     {"role": "user", "content": user_message}
#                 ]
#             )
#             chatgpt_response = response['choices'][0]['message']['content'].strip() # [NOTE]: check for exception safety
#             dispatcher.utter_message(chatgpt_response)
        
#         except openai.OpenAIError as e:
#             dispatcher.utter_message("I'm sorry, I couldn't process your request.")
#             print(f"OpenAI API error: {e}")

#         except openai.APIConnectionError as e:
#             dispatcher.utter_message("I'm sorry, I couldn't connect to the OpenAI API.")
#             print(f"API connection error: {e}")

#         except openai.InvalidRequestError as e:
#             dispatcher.utter_message("I'm sorry, there was an issue with the request to the OpenAI API.")
#             print(f"Invalid request error: {e}")

#         except openai.RateLimitError as e:
#             dispatcher.utter_message("I'm sorry, the OpenAI API rate limit has been exceeded.")
#             print(f"Rate limit error: {e}")

#         except Exception as e:
#             dispatcher.utter_message("An unexpected error occurred.")
#             print(f"Error: {e}")

#         return []


class ActionFallbackToGemini(Action):
    def name(self):
        return "action_fallback_to_gemini"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict):
        user_message = tracker.latest_message.get("text")
        try:
            with open(os.path.join('.keys', 'GEMINI_KEY')) as f:
                GEMINI_API_KEY = f.read().strip()
            
            genai.configure(api_key=GEMINI_API_KEY)
            model = genai.GenerativeModel(model_name="gemini-1.5-flash")

            safety_settings = [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
            ]
            response = model.generate_content(user_message, safety_settings=safety_settings)
            gemini_response = response.text.strip()
            dispatcher.utter_message(gemini_response)
        
        except google_exceptions.InvalidArgument as e:
            print(f"[Gemini] Invalid argument error: {e}")

        except google_exceptions.PermissionDenied as e:
            print(f"[Gemini] Permission denied: {e}")

        except google_exceptions.NotFound as e:
            print(f"[Gemini] Resource not found: {e}")

        except google_exceptions.GoogleAPICallError as e: # Fallback for other API call errors
            print(f"[Gemini] An API call error occurred: {e}")

        except Exception as e:
            dispatcher.utter_message("An unexpected error occurred.")
            print(f"[Gemini] Error: {e}")


class ActionFetchProductDetails(Action): # [ISSUE]: not connected to MongoDB, improve query (should retrieve info from product description/details if msg isn't clear)
    def name(self) -> str:
        return "action_fetch_product_details"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict):
        # Retrieve MongoDB connection string from SECRET_KEY file
        with open(os.path.join('.keys', 'MONGODB_KEY')) as f:
            MONGODB_CONNECTION_STRING = f.read().strip()

        # Connect to MongoDB Atlas
        client = MongoClient(MONGODB_CONNECTION_STRING)
        db = client.get_database('recommendation_system_database')
        collection = db['products']  # Replace with your collection name

        # Get the user query (you can extract this from the tracker)
        product_name = tracker.get_slot('product_name')  # Assuming you captured the product name in a slot

        # Query the MongoDB database
        product = collection.find_one({"ProductName": product_name})

        if product:
            # Respond with product details
            message = f"Product: {product['ProductName']}\n"
            message += f"Category: {product['Category']}\n"
            message += f"Skin Type: {product['SkinType']}\n"
            message += f"Benefits: {product['Benefits']}\n"
            message += f"Active Ingredients: {product['ActiveIngredients']}\n"
            message += f"Sentiment: {product['Sentiment']}\n"
        else:
            message = "Sorry, I couldn't find any details about that product."

        # Send the response back to the user
        dispatcher.utter_message(text=message)

        return []
