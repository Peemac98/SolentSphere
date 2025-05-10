"""
SolentSphere Chatbot - Training Script

This script trains a neural network model to classify user intents based on the patterns 
provided in the intents.json file. The trained model will be used by the chatbot to 
understand and respond to international student inquiries.

"""

import random
import json
import pickle
import numpy as np
import os
from datetime import datetime

# Natural Language Processing libraries
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords

# Machine Learning libraries
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.optimizers import SGD

nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('wordnet')
nltk.download('stopwords')

# Display training information
print("=" * 50)
print("SOLENTSPHERE CHATBOT - TRAINING STARTED")
print("=" * 50)
print(f"TensorFlow version: {tf.__version__}")
print(f"Training started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("-" * 50)

# Step 1: Initialize the WordNet Lemmatizer
# The lemmatizer reduces words to their base form (e.g., "running" -> "run")
lemmatizer = WordNetLemmatizer()

# Step 2: Load the intents from the JSON file
try:
    if not os.path.exists('data'):
        os.makedirs('data')
        print("Created 'data' directory")
    
    intents_file_path = 'data/intents.json'
    with open(intents_file_path, 'r') as file:
        intents = json.load(file)
    print(f"Successfully loaded intents file with {len(intents['intents'])} intent categories")
except Exception as e:
    print(f"Error loading intents file: {e}")
    exit(1)

# Step 3: Initialize lists to store processed data
words = []           
classes = []         
documents = []       
ignore_letters = ['?', '!', '.', ',', ';', ':', '/', '@', '#', '$', '%', '^', '&', '*', '(', ')']

# Step 4: Process each intent and its patterns
print("\nProcessing intents and patterns...")
for intent in intents['intents']:
    tag = intent['tag']
    if tag not in classes:
        classes.append(tag)
        print(f"  Added new intent category: {tag}")
    
    for pattern in intent['patterns']:
        word_list = nltk.word_tokenize(pattern.lower())
        words.extend(word_list)
        documents.append((word_list, tag))

print(f"Processed {len(documents)} training patterns across {len(classes)} intent categories")

# Step 5: Filter and lemmatize the words
stop_words = set(stopwords.words('english'))

print("\nLemmatizing and filtering words...")
words = [lemmatizer.lemmatize(word) for word in words if word not in ignore_letters]

words = sorted(set(words))
classes = sorted(set(classes))

print(f"Vocabulary size: {len(words)} unique words")
print(f"Intent categories: {len(classes)} classes")

# Step 6: Save the processed words and classes to files
if not os.path.exists('models'):
    os.makedirs('models')
    print("Created 'models' directory")

pickle.dump(words, open('models/words.pkl', 'wb'))
pickle.dump(classes, open('models/classes.pkl', 'wb'))
print("\nSaved vocabulary and intent classes to pickle files")

# Step 7: Prepare training data
print("\nPreparing training data...")
training = []
output_empty = [0] * len(classes)

for document in documents:
    bag = []
    word_patterns = document[0]
    word_patterns = [lemmatizer.lemmatize(word.lower()) for word in word_patterns]
    
    for word in words:
        bag.append(1) if word in word_patterns else bag.append(0)
    
    output_row = list(output_empty)
    output_row[classes.index(document[1])] = 1
    
    training.append([bag, output_row])

# Step 8: Shuffle the training data to prevent any learning bias
print("Shuffling training data...")
random.shuffle(training)

# Step 9: Convert the training data to NumPy arrays for Tensorflow
try:
    training = np.array(training, dtype=object)
    train_x = list(training[:, 0])  
    train_y = list(training[:, 1])  
    
    train_x = np.array(train_x)
    train_y = np.array(train_y)
    
    print(f"Training data shape: X={train_x.shape}, Y={train_y.shape}")
except Exception as e:
    print(f"Error preparing training data: {e}")
    exit(1)

# Step 10: Define and build the neural network model
print("\nBuilding neural network model...")
model = Sequential()

model.add(Dense(128, input_shape=(len(train_x[0]),), activation='relu'))
model.add(Dropout(0.5))

model.add(Dense(64, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(len(train_y[0]), activation='softmax'))


model.summary()

# Step 11: Compile the model with optimizer and loss function
print("\nCompiling the model...")
sgd = SGD(learning_rate=0.01, momentum=0.9, nesterov=True)
model.compile(loss='categorical_crossentropy', optimizer=sgd, metrics=['accuracy'])

# Step 12: Train the model
print("\nTraining the model...")
BATCH_SIZE = 5
EPOCHS = 200
VERBOSE = 1

history = model.fit(
    np.array(train_x),  
    np.array(train_y), 
    batch_size=BATCH_SIZE,
    epochs=EPOCHS,
    verbose=VERBOSE
)

# Step 13: Save the model
print("\nSaving the trained model...")
model_filename = 'models/chatbot_model.keras'
model.save(model_filename)
print(f"Model saved to {model_filename}")

# Step 14: Print training summary
print("\n" + "=" * 50)
print("SOLENTSPHERE CHATBOT - TRAINING COMPLETED")
print("=" * 50)
print(f"Vocabulary size: {len(words)} words")
print(f"Intent categories: {len(classes)} intents")
print(f"Training patterns: {len(documents)} examples")
print(f"Final training accuracy: {history.history['accuracy'][-1]:.4f}")
print(f"Training completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 50)
print("\nTraining artifacts saved:")
print("- models/words.pkl (vocabulary)")
print("- models/classes.pkl (intent classes)")
print("- 'models/chatbot_model.keras' (trained neural network)")
print("\nYou can now run the chatbot using these trained models.")
print("=" * 50)