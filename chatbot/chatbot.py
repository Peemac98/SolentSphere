"""
SolentSphere Chatbot - Implementation Script

This script implements the chatbot functionality using the trained model.
It loads the trained model and necessary files, then provides functions
to process user input and generate appropriate responses.

Key components:
1. Loading the trained model and necessary files
2. Processing user input
3. Predicting the intent of user messages
4. Generating appropriate responses
5. Providing a simple command-line interface for testing
"""

import random
import json
import pickle
import numpy as np
import os
import time
from datetime import datetime

# Natural Language Processing libraries
import nltk
from nltk.stem import WordNetLemmatizer

# TensorFlow for loading the model
import tensorflow as tf
from tensorflow.keras.models import load_model

# Initialize the lemmatizer
lemmatizer = WordNetLemmatizer()

# Display welcome message
print("=" * 50)
print("SOLENTSPHERE CHATBOT - STARTING UP")
print("=" * 50)
print(f"Initialization started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("-" * 50)

# Step 1: Load the necessary files for the chatbot
try:
    # Load intents
    intents = json.loads(open('data/intents.json').read())
    print("✓ Loaded intents.json")
    
    # Load words (vocabulary)
    words = pickle.load(open('models/words.pkl', 'rb'))
    print(f"✓ Loaded vocabulary ({len(words)} words)")
    
    # Load classes (intent categories)
    classes = pickle.load(open('models/classes.pkl', 'rb'))
    print(f"✓ Loaded intent classes ({len(classes)} categories)")
    
    # Load the trained model
    model = load_model('models/chatbot_model.keras')
    print("✓ Loaded trained neural network model")
    
except Exception as e:
    print(f"Error loading necessary files: {e}")
    print("Make sure you've run training.py successfully before running this script.")
    exit(1)

# Step 2: Define function to clean up and tokenize user sentences
def clean_up_sentence(sentence):
    """
    Process a user's input sentence:
    1. Tokenize - split into individual words
    2. Lemmatize - convert words to their base form
    
    Args:
        sentence (str): User's input sentence
        
    Returns:
        list: List of processed words
    """
    # Tokenize the sentence
    sentence_words = nltk.word_tokenize(sentence.lower())
    # Lemmatize each word to get its base form
    sentence_words = [lemmatizer.lemmatize(word) for word in sentence_words]
    return sentence_words

# Step 3: Define function to convert a sentence into a bag of words
def bag_of_words(sentence):
    """
    Convert a sentence into a bag of words representation:
    - A list of 0s and 1s indicating the presence or absence of words in our vocabulary
    
    Args:
        sentence (str): User's input sentence
        
    Returns:
        numpy.array: Bag of words representation of the sentence
    """
    # Clean up and tokenize the sentence
    sentence_words = clean_up_sentence(sentence)
    # Create a bag of words - all 0s initially
    bag = [0] * len(words)
    # For each word in the sentence
    for w in sentence_words:
        # Check if the word is in our vocabulary
        for i, word in enumerate(words):
            # If the word matches, set the corresponding bag entry to 1
            if word == w:
                bag[i] = 1
    # Return the bag of words as a numpy array
    return np.array(bag)

# Step 4: Define function to predict the intent of a sentence
def predict_class(sentence, error_threshold=0.25):
    """
    Predict the intent of a user's sentence using the trained model.
    
    Args:
        sentence (str): User's input sentence
        error_threshold (float): Confidence threshold for predictions
        
    Returns:
        list: List of dictionaries containing intents and their probabilities
    """
    # Get the bag of words representation of the sentence
    bow = bag_of_words(sentence)
    
    # Get prediction from the model
    # The model returns probabilities for each intent class
    try:
        res = model.predict(np.array([bow]))[0]
    except Exception as e:
        print(f"Error during prediction: {e}")
        return [{'intent': 'default', 'probability': '1.0'}]
    
    # Filter out predictions below the error threshold
    results = [[i, r] for i, r in enumerate(res) if r > error_threshold]
    
    # Sort results by probability (highest first)
    results.sort(key=lambda x: x[1], reverse=True)
    
    # Create a list of intents and their probabilities
    return_list = []
    for r in results:
        intent_index = r[0]
        if intent_index < len(classes):
            return_list.append({'intent': classes[intent_index], 'probability': str(r[1])})
    
    # If no intent was predicted with sufficient probability, return the default intent
    if not return_list:
        return_list.append({'intent': 'default', 'probability': '1.0'})
    
    return return_list

# Step 5: Define function to get a response based on the predicted intent
def get_response(intents_list, intents_json):
    """
    Get a response based on the predicted intent.
    
    Args:
        intents_list (list): List of predicted intents and their probabilities
        intents_json (dict): JSON object containing all intents and responses
        
    Returns:
        str: Chatbot's response
    """
    # Get the tag of the top predicted intent
    tag = intents_list[0]['intent']
    
    # Get all intents from the intents file
    list_of_intents = intents_json['intents']
    
    # Find the matching intent
    for i in list_of_intents:
        if i['tag'] == tag:
            # Randomly select one of the responses for this intent
            result = random.choice(i['responses'])
            break
    else:
        # If no matching intent is found, use default response
        for i in list_of_intents:
            if i['tag'] == 'default':
                result = random.choice(i['responses'])
                break
        else:
            # If no default intent is found, use a generic response
            result = "I'm not sure I understand. Could you please rephrase?"
    
    return result

# Step 6: Define function to get chatbot response for a given message
def chatbot_response(message):
    """
    Generate a chatbot response for a given user message.
    This is the main function that combines all steps.
    
    Args:
        message (str): User's message
        
    Returns:
        str: Chatbot's response
    """
    # Predict the intent of the message
    ints = predict_class(message)
    
    # Log the prediction (for debugging)
    if ints:
        confidence = float(ints[0]['probability'])
        print(f"Predicted intent: {ints[0]['intent']} (confidence: {confidence:.2f})")
    
    # Get a response based on the predicted intent
    res = get_response(ints, intents)
    
    return res

# Step 7: Implement a simple command-line interface for testing
def chatbot_cli():
    """
    Simple command-line interface for testing the chatbot.
    """
    print("\n" + "=" * 50)
    print("SOLENTSPHERE CHATBOT - READY")
    print("=" * 50)
    print("Type 'quit' to exit")
    print("-" * 50)
    
    # Chat loop
    while True:
        # Get user input
        message = input("You: ")
        
        # Check if user wants to quit
        if message.lower() in ['quit', 'exit', 'bye']:
            print("SolentSphere: Goodbye! Have a great day!")
            break
        
        # Get chatbot response
        response = chatbot_response(message)
        
        # Display the response
        print(f"SolentSphere: {response}")
        print("-" * 50)

# Step 8: Run the CLI if this script is executed directly
if __name__ == "__main__":
    # Run the command-line interface
    chatbot_cli()