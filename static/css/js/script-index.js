let contador = 1

setInterval(function(){
    document.getElementById('slide' + contador).checked = true
    contador ++;

    if(contador > 5) {
        contador = 1
    }

}, 3000 )


//navbar resposivo abaixo
const toggleButton = document.querySelector('.botao');
const navbarLinks = document.querySelector('.navbar-links');

toggleButton.addEventListener('click', () => {

navbarLinks.classList.toggle('active');
});