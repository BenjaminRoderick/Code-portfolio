import torch
import torch.nn as nn
from transformers import AutoTokenizer
from load_embeddings import load_embedding_model
from utils import find_similar_embeddings, prompt_to_embeddings, find_similar_logits, get_token_embedding

model, tokenizer = load_embedding_model(151936, 1536, "embeddings_qwen.pth", "unembeddings_qwen.pth", "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B")

#Uniform convex combination

## Same categorie

#1
# cat = get_token_embedding(model, tokenizer, "cat")
# dog = get_token_embedding(model, tokenizer, "dog")
# mouse = get_token_embedding(model, tokenizer, "mouse")

# weighted_embedding_animal = 0.33*cat + 0.33*dog + 0.34*mouse

# print("Embedding cat: ", embedding_cat)
# print("Embedding dog: ", embedding_dog)
# print("Embedding mouse: ", embedding_mouse)
# print("Cat + Dog + Mouse embedding: ", weighted_embedding)

# most_similar_words = find_similar_embeddings(model, tokenizer, weighted_embedding, n=20)
# print(most_similar_words)

# top_words = find_similar_logits(model, tokenizer, weighted_embedding_animal, n=20)
# for w, s in top_words:
#     print(f"{w:15s}  {s:.4f}")

#The 3 words are indeed "cat", "mouse" and "dog"

#2
# grape = get_token_embedding(model, tokenizer, "grape")
# orange = get_token_embedding(model, tokenizer, "orange")
# apple = get_token_embedding(model, tokenizer, "apple")

# weighted_embedding_fruit = 0.33*grape + 0.33*orange + 0.34*apple
# top_words = find_similar_logits(model, tokenizer, weighted_embedding_fruit, n=20)

# for w, s in top_words:
#     print(f"{w:15s}  {s:.4f}")

#"orange" and "apple" are in the top 3 but not "grape"

#3
# blue = get_token_embedding(model, tokenizer, "blue") #appears
# orange = get_token_embedding(model, tokenizer, "orange") #appears
# red = get_token_embedding(model, tokenizer, "red") #appears
# yellow = get_token_embedding(model, tokenizer, "yellow") #appears
# black = get_token_embedding(model, tokenizer, "black") #appears
# white = get_token_embedding(model, tokenizer, "white") #appears
# brown = get_token_embedding(model, tokenizer, "brown") #appears
# gray = get_token_embedding(model, tokenizer, "gray") #appears
# green = get_token_embedding(model, tokenizer, "green") #appears
# purple = get_token_embedding(model, tokenizer, "purple") #appears

# weighted_embedding_color = 0.1*blue + 0.1*orange + 0.1*red + 0.1*yellow + 0.1*black + 0.1*white + 0.1*brown + 0.1*gray + 0.1*green + 0.1*purple
# top_words = find_similar_logits(model, tokenizer, weighted_embedding_color, n=20)

# for w, s in top_words:
#     print(f"{w:15s}  {s:.4f}")

#all words are in the top 15

#4
# playing = get_token_embedding(model, tokenizer, "playing")
# cooking = get_token_embedding(model, tokenizer, "cooking")
# joking = get_token_embedding(model, tokenizer, "joking")
# gambling = get_token_embedding(model, tokenizer, "gambling")
# walking = get_token_embedding(model, tokenizer, "walking")
# dancing = get_token_embedding(model, tokenizer, "dancing")
# crying = get_token_embedding(model, tokenizer, "crying")
# buying = get_token_embedding(model, tokenizer, "buying")
# working = get_token_embedding(model, tokenizer, "working")
# enjoying = get_token_embedding(model, tokenizer, "enjoying")

# weighted_embedding_verb = 0.1*playing + 0.1*cooking + 0.1*joking + 0.1*gambling + 0.1*walking + 0.1*dancing + 0.1*crying + 0.1*buying + 0.1*working + 0.1*enjoying
# top_words = find_similar_logits(model, tokenizer, weighted_embedding_verb, n=20)

# for w, s in top_words:
#     print(f"{w:15s}  {s:.4f}")

#5
# one = get_token_embedding(model, tokenizer, "one")
# two = get_token_embedding(model, tokenizer, "two") #appears
# three = get_token_embedding(model, tokenizer, "three") #appears
# four = get_token_embedding(model, tokenizer, "four") #appears
# five = get_token_embedding(model, tokenizer, "five") #appears
# six = get_token_embedding(model, tokenizer, "six") #appears
# seven = get_token_embedding(model, tokenizer, "seven") #appears
# eight = get_token_embedding(model, tokenizer, "eight") #appears
# nine = get_token_embedding(model, tokenizer, "nine") #appears
# zero = get_token_embedding(model, tokenizer, "zero")

# weighted_embedding_number = 0.1*one + 0.1*two + 0.1*three + 0.1*four + 0.1*five + 0.1*six + 0.1*seven + 0.1*eight + 0.1*nine + 0.1*zero
# top_words = find_similar_logits(model, tokenizer, weighted_embedding_number, n=20)

# for w, s in top_words:
#     print(f"{w:15s}  {s:.4f}")

# all appears in top 20 except "one" and "zero"

#Different categories
#6

# blue = get_token_embedding(model, tokenizer, "blue") #appears
# red = get_token_embedding(model, tokenizer, "red") #appears
# yellow = get_token_embedding(model, tokenizer, "yellow") #appears
# black = get_token_embedding(model, tokenizer, "black") #appears
# grape = get_token_embedding(model, tokenizer, "grape")
# orange = get_token_embedding(model, tokenizer, "orange")
# apple = get_token_embedding(model, tokenizer, "apple")
# cat = get_token_embedding(model, tokenizer, "cat")
# dog = get_token_embedding(model, tokenizer, "dog")
# mouse = get_token_embedding(model, tokenizer, "mouse")

# weighted_embedding_mixed_cat = 0.1*blue + 0.1*red + 0.1*yellow + 0.1*black + 0.1*grape + 0.1*orange + 0.1*apple + 0.1*cat + 0.1*dog + 0.1*mouse
# top_words = find_similar_logits(model, tokenizer, weighted_embedding_mixed_cat, n=20)

# for w, s in top_words:
#     print(f"{w:15s}  {s:.4f}")

#7

# car = get_token_embedding(model, tokenizer, "car")
# today = get_token_embedding(model, tokenizer, "today")
# infinity = get_token_embedding(model, tokenizer, "infinity")

# weighted_embedding_mixed_cat2 = 0.33*car + 0.33*today + 0.33*infinity

# top_words = find_similar_logits(model, tokenizer, weighted_embedding_mixed_cat2, n=20)

# for w, s in top_words:
#     print(f"{w:15s}  {s:.4f}")

#the three words are in the top 3

#8

# car = get_token_embedding(model, tokenizer, "car")
# today = get_token_embedding(model, tokenizer, "today")
# infinity = get_token_embedding(model, tokenizer, "infinity")
# playing = get_token_embedding(model, tokenizer, "playing")
# canada = get_token_embedding(model, tokenizer, "canada")

# weighted_embedding_mixed_cat3 = 0.2*car + 0.2*today + 0.2*infinity + 0.2*playing + 0.2*canada

# top_words = find_similar_logits(model, tokenizer, weighted_embedding_mixed_cat3, n=20)

# for w, s in top_words:
#     print(f"{w:15s}  {s:.4f}")

#all words in the top 5 except "canada"

#9.

# car = get_token_embedding(model, tokenizer, "car")
# today = get_token_embedding(model, tokenizer, "today")
# infinity = get_token_embedding(model, tokenizer, "infinity")
# playing = get_token_embedding(model, tokenizer, "playing")
# canada = get_token_embedding(model, tokenizer, "canada")
# sky = get_token_embedding(model, tokenizer, "sky")
# heart = get_token_embedding(model, tokenizer, "heart")
# ball = get_token_embedding(model, tokenizer, "ball")
# time = get_token_embedding(model, tokenizer, "time")
# funny = get_token_embedding(model, tokenizer, "funny")

# weighted_embedding_mixed_cat4 = 0.1*car + 0.1*today + 0.1*infinity + 0.1*playing + 0.1*canada + 0.1*sky + 0.1*heart + 0.1*ball + 0.1*time + 0.1*funny

# top_words = find_similar_logits(model, tokenizer, weighted_embedding_mixed_cat4, n=20)

# for w, s in top_words:
#     print(f"{w:15s}  {s:.4f}")

#no words in the top 20

#10.

# car = get_token_embedding(model, tokenizer, "car")
# today = get_token_embedding(model, tokenizer, "today")
# infinity = get_token_embedding(model, tokenizer, "infinity")
# playing = get_token_embedding(model, tokenizer, "playing")
# canada = get_token_embedding(model, tokenizer, "canada")
# sky = get_token_embedding(model, tokenizer, "sky")

# weighted_embedding_mixed_cat5 = (1.0/6.0)*car + (1.0/6.0)*today + (1.0/6.0)*infinity + (1.0/6.0)*playing + (1.0/6.0)*canada + (1.0/6.0)*sky

# top_words = find_similar_logits(model, tokenizer, weighted_embedding_mixed_cat5, n=20)

# for w, s in top_words:
#     print(f"{w:15s}  {s:.4f}")

#not very good

#11.

# camping = get_token_embedding(model, tokenizer, "camping")
# canada = get_token_embedding(model, tokenizer, "canada")
# vacation = get_token_embedding(model, tokenizer, "vacation")
# zoo = get_token_embedding(model, tokenizer, "zoo")
# apple = get_token_embedding(model, tokenizer, "apple")
# morning = get_token_embedding(model, tokenizer, "morning")

# weighted_embedding_mixed_cat6 = (1.0/6.0)*camping + (1.0/6.0)*canada + (1.0/6.0)*vacation + (1.0/6.0)*zoo + (1.0/6.0)*apple + (1.0/6.0)*morning

# top_words = find_similar_logits(model, tokenizer, weighted_embedding_mixed_cat6, n=20)

# for w, s in top_words:
#     print(f"{w:15s}  {s:.4f}")

#not very good, decompose the words. only "apple" in top 20

11. #Short words

one = get_token_embedding(model, tokenizer, "one")
apple = get_token_embedding(model, tokenizer, "apple") #appears
cow = get_token_embedding(model, tokenizer, "cow") #appears
zoo = get_token_embedding(model, tokenizer, "zoo")
gym = get_token_embedding(model, tokenizer, "gym")
job = get_token_embedding(model, tokenizer, "job") #appears

weighted_embedding_mixed_cat7 = (1.0/6.0)*one + (1.0/6.0)*apple + (1.0/6.0)*cow + (1.0/6.0)*zoo + (1.0/6.0)*gym + (1.0/6.0)*job

top_words = find_similar_logits(model, tokenizer, weighted_embedding_mixed_cat7, n=20)

for w, s in top_words:
    print(f"{w:15s}  {s:.4f}")
