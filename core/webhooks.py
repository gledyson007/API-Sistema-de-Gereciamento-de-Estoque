import requests
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def enviar_webhook_baixo_estoque(produto, estoque_item):
    url = settings.WEBHOOK_BAIXO_ESTOQUE_URL
    if not url:
        logger.warning("URL de webhook para baixo estoque não configurada")
        return
    
    payload = {
        "alerta": "Estoque Baixo",
        "produto_id": produto.id,
        "produto_nome": produto.nome,
        "produto_sku": produto.sku,
        "quantidade_atual": estoque_item.quantidade,
        "estoque_minimo": produto.estoque_minimo,
        "armazem_id": estoque_item.armazem.id,
        "armazem_nome": estoque_item.armazem.nome
    }

    try:
        resposta = requests.post(url, json=payload, timeout=10)
        resposta.raise_for_status()
        logger.info(f"Webhook de baixo de estoque enviado com sucesso para o produto {produto.sku}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Falha ao enviar webhook de baixo estoque para o produto {produto.sku}: {e}")