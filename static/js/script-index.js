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
//modal excluir produto
function Abrir_ModalExcluir(id) {
    document.getElementById('modal_excluir_' + id).style.display = 'flex';
}

function Fechar_ModalExcluir(id) {
    document.getElementById('modal_excluir_' + id).style.display = 'none';
}

function Abrir_ModalEditar(id) {
    document.getElementById('modal_editar_' + id).style.display = 'flex';
}

function Fechar_ModalEditar(id) {
    document.getElementById('modal_editar_' + id).style.display = 'none';
}
function Abrir_ModalSaibaMais(id) {
    document.getElementById('modal-saiba-mais-' + id).style.display = 'flex';
}

function Fechar_ModalSaibaMais(id) {
    document.getElementById('modal-saiba-mais-' + id).style.display = 'none';
}
// Fechar se clicar fora da caixa branca
window.onclick = function(event) {
    if (event.target.className === 'modais') {
        event.target.style.display = 'none';
    }
}