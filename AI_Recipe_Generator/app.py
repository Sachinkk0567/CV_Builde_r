import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from google import genai
import streamlit as st  # optional fallback check if needed

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "recipe-gen-secret")

# Load Gemini API Key
api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_GEMINI_API_KEY")

client = None
if api_key:
    client = genai.Client(api_key=api_key)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/generate-recipe", methods=["POST"])
def generate_recipe():
    try:
        if not client:
            return jsonify({"error": "Gemini API Key is missing. Please check your .env file."}), 500

        data = request.get_json() or {}
        ingredients = data.get("ingredients", "").strip()
        dietary = data.get("dietary", "Any")
        cuisine = data.get("cuisine", "Any")
        spice_level = data.get("spice_level", "Medium")
        meal_type = data.get("meal_type", "Any")

        if not ingredients:
            return jsonify({"error": "Please enter at least one ingredient."}), 400

        prompt = f"""
You are a world-class professional master chef and nutritionist.
Generate a detailed, delicious, easy-to-follow recipe using the provided ingredients and options:

- Main Ingredients: {ingredients}
- Dietary Filter: {dietary}
- Cuisine Style: {cuisine}
- Spice Level: {spice_level}
- Meal Type: {meal_type}

Return a beautifully formatted Markdown response with the following exact structure:

# 🍳 [Dish Name]

> *[Short 1-2 sentence appetizing description of the dish]*

---

### ⏱️ Quick Summary
- **Prep Time:** [X mins]
- **Cook Time:** [Y mins]
- **Servings:** [Z servings]
- **Difficulty Level:** [Easy/Medium/Hard]

---

### 🥗 Ingredients
- List each required ingredient with exact measurements. (Include given ingredients plus standard pantry staples like salt, oil, water, basic spices).

---

### 👨‍🍳 Step-by-Step Instructions
1. **Preparation:** ...
2. **Cooking Step 1:** ...
3. **Cooking Step 2:** ...
4. **Plating & Serving:** ...

---

### 📊 Nutritional Breakdown (Per Serving)
- **Calories:** ~[number] kcal
- **Protein:** [grams] g
- **Carbohydrates:** [grams] g
- **Healthy Fats:** [grams] g

---

### 💡 Chef's Secret Tips & Variations
- Tip 1: Secret ingredient or technique for maximum flavor.
- Tip 2: Recommended side dish or beverage pairing.
- Tip 3: Ingredient substitution idea.
"""

        # Call Gemini Model (gemini-3.5-flash)
        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=prompt
        )

        recipe_markdown = response.text if response and response.text else "Failed to generate recipe output."
        return jsonify({"success": True, "recipe": recipe_markdown})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5005))
    print(f"Starting AI Recipe Generator on http://127.0.0.1:{port}")
    app.run(debug=True, host="127.0.0.1", port=port)

