document.addEventListener('DOMContentLoaded', function() {
    const formPedido = document.getElementById('form-pedido');
    const precoDisplay = document.getElementById('preco-total');
    const reciboSucesso = document.getElementById('recibo-sucesso');
    const btnBaixarJson = document.getElementById('btn-baixar-json');

    // --- 1. CÁLCULO DO PREÇO EM TEMPO REAL ---
    function calcularPrecoTotal() {
        let total = 0.0;
        
        const pao = document.querySelector('input[name="pao_selecionado"]:checked');
        if (pao) {
            total += parseFloat(pao.getAttribute('data-preco'));
        }

        const ingredientes = document.querySelectorAll('input[name="ingrediente"]:checked');
        ingredientes.forEach(function(item) {
            total += parseFloat(item.getAttribute('data-preco'));
        });

        precoDisplay.textContent = 'R$ ' + total.toFixed(2);
    }

    // Monitora mudanças nos botões de rádio e caixas de seleção
    formPedido.addEventListener('change', function(e) {
        if (e.target.name === 'pao_selecionado' || e.target.name === 'ingrediente') {
            calcularPrecoTotal();
        }
    });
    
    calcularPrecoTotal();

    // --- 2. SALVAR NO HISTÓRICO LOCAL E GERAR RECIBO ---
    formPedido.addEventListener('submit', function(e) {
        e.preventDefault();

        const cliente = document.getElementById('nome-cliente').value.trim();
        const endereco = document.getElementById('endereco').value.trim();
        const pagamento = document.getElementById('pagamento').value;
        const paoNome = document.querySelector('input[name="pao_selecionado"]:checked').value;

        let itensEscolhidos = [paoNome];
        document.querySelectorAll('input[name="ingrediente"]:checked').forEach(function(item) {
            itensEscolhidos.push(item.value);
        });

        const totalFinal = parseFloat(precoDisplay.textContent.replace('R$ ', ''));

        const novoPedido = {
            id: Date.now(),
            cliente: cliente,
            itens: itensEscolhidos,
            total: totalFinal,
            forma_pagamento: pagamento,
            endereco: endereco,
            data_hora: new Date().toLocaleString('pt-BR')
        };

        let historicoPedidos = JSON.parse(localStorage.getItem('historico_pedidos_json')) || [];
        historicoPedidos.push(novoPedido);
        localStorage.setItem('historico_pedidos_json', JSON.stringify(historicoPedidos, null, 4));

        reciboSucesso.innerHTML = `
            <h3>📋 Pedido Confirmado e Salvo com Sucesso!</h3>
            <p style="margin-top: 10px;"><strong>Cliente:</strong> ${novoPedido.cliente}</p>
            <p><strong>Hambúrguer:</strong> ${novoPedido.itens.join(', ')}</p>
            <p><strong>Total Pago:</strong> R$ ${novoPedido.total.toFixed(2)}</p>
            <p><strong>Forma de Pagamento:</strong> ${novoPedido.forma_pagamento}</p>
            <p><strong>Endereço:</strong> ${novoPedido.endereco}</p>
            <p style="margin-top: 12px; font-size: 11px; color: #555; font-style: italic; border-top: 1px dashed #b5d99c; padding-top: 5px;">
                Pedido serializado e armazenado localmente na memória interna.
            </p>
        `;
        reciboSucesso.style.display = 'block';
        
        formPedido.reset();
        calcularPrecoTotal();
    });

    // --- 3. EXPORTAÇÃO DO ARQUIVO JSON ---
    btnBaixarJson.addEventListener('click', function() {
        const dadosLocais = localStorage.getItem('historico_pedidos_json');
        const jsonParaDownload = dadosLocais ? dadosLocais : "[]";
        
        const blob = new Blob([jsonParaDownload], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        
        const linkTemporario = document.createElement('a');
        linkTemporario.href = url;
        linkTemporario.download = 'pedidos.json';
        
        document.body.appendChild(linkTemporario);
        linkTemporario.click();
        document.body.removeChild(linkTemporario);
        URL.revokeObjectURL(url);
    });
});