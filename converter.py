import requests
import json

class JSON_converter:

    cocktail = {}

    url = "https://www.thecocktaildb.com/api/json/v1/1/search.php?s="

    def search(self, term):
        response = requests.get(f'{self.url}{term}')

        drinks = response.json()['drinks']

        return drinks

    def convert(self, drinks):
        out = []
        for drink in drinks:

            ingredients = []
            measures = []
            combined = []

            for i in range(1, 15):
                if drink[f'strIngredient{i}'] != None:
                    ingredients.append(drink[f'strIngredient{i}'])

                if drink[f'strMeasure{i}'] != None:
                    measures.append(drink[f'strMeasure{i}'])
            
            for index, val in enumerate(ingredients):
                combined.append(f'{measures[index]} {ingredients[index]}')

            out.append({'name': drink['strDrink'], 'id': drink['idDrink'], 'image': drink['strDrinkThumb'], 'instructions': drink['strInstructions'], 'ingredients': combined})

        return out



