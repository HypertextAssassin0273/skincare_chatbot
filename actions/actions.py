# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

# from typing import Any, Text, Dict, List
#
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
#
#
# class ActionHelloWorld(Action):

#     def name(self) -> Text:
#         return "action_hello_world"

#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]: # [param -> return_type for func 'run']

#         dispatcher.utter_message(text="Hello World!") # [dispatcher relationship with domain ??]

#         return [] # [can return events as lists]


from openai import OpenAI
import os
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from pymongo import MongoClient
# from dotenv import load_dotenv


class ActionRecommendProducts(Action):
    def name(self) -> Text: # tied with domain.yml -> actions
        return "action_recommend_products"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        skin_type = tracker.get_slot("skin_type")
        skin_concern = tracker.get_slot("skin_concern")

        recommendations = self.get_product_recommendations(skin_type, skin_concern) # [local function binded to class]

        dispatcher.utter_message(text=f"Here are some recommended products for {skin_concern}: {recommendations}")
        return []

    def get_product_recommendations(self, skin_type, skin_concern): # [reqs. to be in sync with recommendation system]
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
    def name(self) -> Text: # tied with domain.yml -> actions
        return "action_say_phone"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]): # Dict[Text, Any] or dict, -> List[Dict[Text, Any]]
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


class ActionFallbackToChatGPT(Action):
    def name(self):
        return "action_fallback_to_chatgpt"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict):
        user_message = tracker.latest_message.get("text")
        try:
            client = OpenAI(
                 api_key=os.environ.get("OPENAI_API_KEY"),  # this is also the default, it can be omitted
            )
            response =  client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": user_message}
                ]
            )
            chatgpt_response = response['choices'][0]['message']['content'].strip()
            dispatcher.utter_message(chatgpt_response)

        except client.error.OpenAIError as e:
            dispatcher.utter_message("I'm sorry, I couldn't process your request.")
            print(f"OpenAI API error: {e}")

        except Exception as e:
            dispatcher.utter_message("An unexpected error occurred.")
            print(f"Error: {e}")

        return []


class ActionFetchProductDetails(Action): # [NEW]
    def name(self) -> str:
        return "action_fetch_product_details"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict):
        # Connect to MongoDB Atlas
        client = MongoClient("mongodb+srv://skincare14:skincarerecommender@clusterskincare.6sapl.mongodb.net/")
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
