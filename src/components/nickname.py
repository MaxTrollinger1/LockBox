import random

# Lists for nickname generation
adjectives = ["Swift", "Brave", "Mighty", "Cunning", "Lone", "Shadow", "Fierce", "Thunder", "Silent", "Stormy", "Golden", "Crimson", "Eternal"]
animals = ["Wolf", "Tiger", "Hawk", "Dragon", "Fox", "Raven", "Panther", "Eagle", "Serpent", "Lion", "Bear", "Griffin"]
titles = ["Warrior", "Nomad", "Seeker", "Guardian", "Wanderer", "Knight", "Sorcerer", "Hunter", "Champion", "Slayer", "Sentinel"]
numbers = [str(i) for i in range(10, 100)]

# Function to generate a random nickname
def generate_nickname():
    return f"{random.choice(adjectives)}{random.choice(animals)}{random.choice(titles)}{random.choice(numbers)}"