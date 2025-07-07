from django.db import models
from django.contrib.auth.models import User

class Categoria(models.Model):
    nome = models.CharField(max_length=100, unique=True, help_text='Nome único para a categoria.')
    descricao = models.TextField(blank=True, null=True, help_text='Descrição opcional da categoria.')

    class Meta:
        verbose_name = "Categoria",
        verbose_name_plural = "Categorias"
        ordering = ['nome']

    def __str__(self):
        return self.nome

class Fornecedor(models.Model):
    nome_fantasia = models.CharField(max_length=255)
    razao_social = models.CharField(max_length=255, blank=True, null=True)
    cnpj = models.CharField(max_length=18, unique=True, blank=True, null=True, help_text="Formato: XX.XXX.XXX/XXXX-XX")
    email = models.EmailField(blank=True, null=True)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    endereco = models.CharField(max_length=255, blank=True, null=True)
    data_criacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Fornecedor"
        verbose_name_plural = "Fornecedores"
        ordering = ['nome_fantasia']

    def __str__(self):
        return self.nome_fantasia
    
class Produto(models.Model):
    nome = models.CharField(max_length=255)
    sku = models.CharField(max_length=100, unique=True, help_text="SKU (Stock Keeping Unit) - Código de Barras ou código único do produto.")
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, blank=True, null=True, related_name='produtos')
    descricao = models.TextField(blank=True, null=True)
    fornecedor = models.ForeignKey(Fornecedor, on_delete=models.SET_NULL, null=True, blank=True, related_name='produtos')

    preco_custo = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    preco_venda = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    unidade_medida = models.CharField(max_length=20, default='unidade', help_text='Ex: unidade, kg, litro, metro.')
    estoque_minimo = models.PositiveIntegerField(default=0, help_text="Quantidade mínima em estoque para gerar um alerta.")
    unididade_minimo = models.PositiveIntegerField(default=0, help_text='Quantidade mínima em estoque para gerar um alerta.')

    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizaçao = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"
        ordering = ['nome']

    def __str__(self):
        return f"{self.nome} ({self.sku})"
    
class Armazem(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    localizacao = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = "Armazém"
        verbose_name_plural = "Armazéns"
        ordering = ['nome']

    def __str__(self):
        return self.nome
    
class EstoqueItem(models.Model):
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name='itens_de_estoque')
    armazem = models.ForeignKey(Armazem, on_delete=models.CASCADE, related_name='itens_de_estoque')
    quantidade = models.IntegerField(default=0)

    class Meta:
        unique_together = ('produto', 'armazem')
        verbose_name = "Item de Estoque"
        verbose_name_plural = "Itens de Estoques"

    def __str__(self):
        return f"{self.produto.sku} em {self.armazem.nome}: {self.quantidade}"

class MovimentacaoEstoque(models.Model):
    TIPO_MOVIMENTACAO = (
        ('ENTRADA', 'Entrada'),
        ('SAIDA', 'Saida'),
        ('AJUSTE', 'Ajuste'),
    )

    produto = models.ForeignKey(Produto, on_delete=models.PROTECT)
    armazem = models.ForeignKey(Armazem, on_delete=models.PROTECT)
    quantidade = models.IntegerField()
    data_movimentacao = models.DateTimeField(auto_now_add=True)
    responsavel = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    tipo = models.CharField(max_length=20, choices=TIPO_MOVIMENTACAO)
    motivo = models.CharField(max_length=255, blank=True, help_text='Ex: Venda #123, Compra do fornecedor X, Ajuste de inventário')

    class Meta:
        verbose_name = 'Movimentação de Estoque'
        verbose_name_plural = 'Movimentações de Estoque'
        ordering = ['-data_movimentacao']

    def __str__(self):
        return f"{self.tipo} de {self.quantidade} x {self.produto.sku}"
    
class PedidoCompra(models.Model):
    STATUS_PEDIDO = (
        ('PENDENTE', 'Pendente'),
        ('APROVADO', 'Aprovado'),
        ('RECEBIDO', 'Recebido'),
        ('CANCELADO', 'Cancelado'),
    )
    fornecedor = models.ForeignKey(Fornecedor, on_delete=models.PROTECT, related_name='pedidos_compra')
    status = models.CharField(max_length=20, choices=STATUS_PEDIDO, default='PENDENTE')
    data_pedido = models.DateTimeField(auto_now_add=True)
    data_recebimento = models.DateTimeField(null=True, blank=True)
    responsavel_pedido = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='pedidos_criados')

    class Meta:
        ordering = ['-data_pedido']
        verbose_name = 'Pedido de Compra'
        verbose_name_plural = 'Pedidos de Compra'

    def __str__(self):
        return f"Pedido #{self.id} - {self.fornecedor.nome_fantasia}"
    
class ItemPedidoCompra(models.Model):
    pedido_compra = models.ForeignKey(PedidoCompra, on_delete=models.CASCADE, related_name='itens')
    produto = models.ForeignKey(Produto, on_delete=models.PROTECT)
    quantidade = models.PositiveBigIntegerField()
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2, help_text="Preço de custo do produto no momento da compra.")

    def __str__(self):
        return f"{self.quantidade} x {self.produto.nome} no Pedido #{self.pedido_compra.id}"

class Cliente(models.Model):
    nome = models.CharField(max_length=255)
    cpf = models.CharField(max_length=14, unique=True, blank=True, null=True)
    email = models.EmailField(unique=True)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    data_cadastro = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['nome']
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"

    def __str__(self):
        return self.nome
    
class PedidoVenda(models.Model):
    STATUS_PEDIDO = (
        ('CARRINHO', 'Carrinho'),
        ('AGUARDANDO_PAGAMENTO', 'Aguardando Pagamento'),
        ('PAGO', 'Pago'),
        ('DESPACHADO', 'Despachado'),
        ('CANCELADO', 'Cancelado'),
    )
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name='pedido')
    status = models.CharField(max_length=30, choices=STATUS_PEDIDO, default='AGUARDANDO_PAGAMENTO')
    data_pedido = models.DateTimeField(auto_now_add=True)
    data_despacho = models.DateTimeField(null=True, blank=True)
    responsavel_venda = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='vendas_realizadas')
    
    class Meta:
        ordering = ['-data_pedido']
        verbose_name = 'Pedido de Venda'
        verbose_name_plural = "Pedidos de venda"

    def __str__(self):
        return f"Venda #{self.id} - {self.cliente.nome}"
    
class ItemPedidoVenda(models.Model):
    pedido_venda = models.ForeignKey(PedidoVenda, on_delete=models.CASCADE, related_name='itens')
    produto = models.ForeignKey(Produto, on_delete=models.PROTECT)
    quantidade = models.PositiveBigIntegerField()
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2, help_text="Preço de venda do produto no momento da venda.")

    def __str__(self):
        return f"{self.quantidade} x {self.produto.nome} na Venda #{self.pedido_venda.id}"