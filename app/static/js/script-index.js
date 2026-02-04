//navbar resposivo abaixo
const toggleButton = document.querySelector('.botao');
const navbarLinks = document.querySelector('.navbar-links');

toggleButton.addEventListener('click', () => {

navbarLinks.classList.toggle('active');
});
//modais
function AbrirModal(idModal) {
    const modal = document.getElementById(idModal);
    if (modal) {
        modal.style.display = 'flex';
    }
}

function FecharModal(idModal) {
    const modal = document.getElementById(idModal);
    if (modal) {
        modal.style.display = 'none';
    }
}

// Função para pegar os produtos do usuário e usar no modal

function abrirProdutos(username) {
    fetch(`/vendedor/${username}/produtos`)
        .then(response => response.json())
        .then(produtos => {
            const tabela = document.getElementById("corpo-tabela-produtos");
            tabela.innerHTML = "";

            produtos.forEach(produto => {
                tabela.innerHTML += `
                    <tr>
                        <td>${produto.nome}</td>
                        <td>R$ ${produto.preco}</td>
                        <td>${produto.descricao}</td>
                    </tr>
                `;
            });

            AbrirModal("modal_produtos");
        });
}


// Fechar se clicar fora da caixa branca
window.onclick = function(event) {
    if (event.target.className === 'modais') {
        event.target.style.display = 'none';
    }
}
window.addEventListener("scroll", function() {
    let header = document.querySelector("header");
    // Se o scroll passar de 50px, adiciona a classe, senão remove
    header.classList.toggle("rolagem", window.scrollY > 5);
})