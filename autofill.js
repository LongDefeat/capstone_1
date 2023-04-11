
function autofill(input){
    if (input == ''){
        return []
    }
    let reg = new RegExp(input)
    return searchCocktails.filter(function(cocktail){
        if (cocktail.match(reg)){
            return cocktail;
        }
    })
}

function showResults(val){
    res = document.getElementById("result");
    res.innerHTML = '';
    if (val == ''){
        return; 
    };
    let list = '';
    fetch('/suggest?q=' + val).then(
        function (res){
            return res.json();
        }).then(function (data){
            for (let i=0; i < data.length; i++){
                list += '<li>' + data[i] + '</li>'
            }
            res.innerHTML = '<ul>'  + list + '</ul>';
            return true;
        }).catch(function(err){
            console.warn('Something went wrong.', err);
            return false;
        })
}