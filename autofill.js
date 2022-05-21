let searchCocktails = [
  "bourbon",
  "margarita",
  "espresso",
  "tequila",
  "whiskey",
  "amaretto",
  "vodka",
  "martini",
  "manhattan",
  "old fashion",
  "sour",
  "rum",
  "gin",
  "lemon",
];

function autofill(input) {
  if (input == "") {
    return [];
  }
  let reg = new RegExp(input);
  return searchCocktails.filter(function (cocktail) {
    if (cocktail.match(reg)) {
      return cocktail;
    }
  });
}

function showResults(val) {
  res = document.getElementById("result");
  res.innerHTML = "";
  let list = "";
  let cocktails = autofill(val);
  for (let i = 0; i < cocktails.length; i++) {
    list += "<li>" + terms[i] + "</li>";
  }
  res.innerHTML = "<ul>" + list + "</ul>";
}
