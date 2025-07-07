from rest_framework import serializers
from .models import Categoria, Fornecedor, Produto, Armazem, EstoqueItem, MovimentacaoEstoque, PedidoCompra, ItemPedidoCompra, Cliente, PedidoVenda, ItemPedidoVenda

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id', 'nome', 'descricao']

class ForncedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fornecedor
        fields = '__all__'

class ProdutoSerializer(serializers.ModelSerializer):
    categoria = serializers.StringRelatedField(read_only=True)
    categoria_id = serializers.PrimaryKeyRelatedField(
        queryset=Categoria.objects.all(), source='categoria', write_only=True
    )

    fornecedor = serializers.StringRelatedField(read_only=True)
    fornecedor_id = serializers.PrimaryKeyRelatedField(
        queryset=Fornecedor.objects.all(), source='fornecedor', write_only=True, required=False
    )

    class Meta:
        model = Produto
        fields = [
            'id',
            'nome',
            'sku',
            'descricao',
            'categoria',
            'categoria_id',
            'fornecedor',
            'fornecedor_id',
            'preco_custo',
            'preco_venda',
            'unidade_medida',
            'estoque_minimo',
            'data_criacao'
        ]
        read_only_fields = ['data_criacao']

class ArmazemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Armazem
        fields = '__all__'

class EstoqueItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstoqueItem
        fields = '__all__'
        depth = 1

class MovimentacaoEstoqueSerializer(serializers.ModelSerializer):
    responsavel = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = MovimentacaoEstoque
        fields = '__all__'

class RelatorioBaixoEstoqueSerializer(serializers.Serializer):
    produto_id = serializers.IntegerField()
    produto_nome = serializers.CharField(source='produto.nome')
    produto_sku = serializers.CharField(source='produto.sku') 
    estoque_minimo = serializers.IntegerField(source='produto.estoque_minimo')
    quantidade_atual = serializers.IntegerField(source='quantidade')
    armazem_nome = serializers.CharField(source='armazem.nome')

class ItemPedidoCompraSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemPedidoCompra
        fields = ['produto', 'quantidade', 'preco_unitario']

class PedidoCompraSerializer(serializers.ModelSerializer):
    itens = ItemPedidoCompraSerializer(many=True)
    fornecedor_nome = serializers.CharField(source='fornecedor.nome_fantasia', read_only=True)
    responsavel_nome = serializers.CharField(source='responsavel_pedido.username', read_only=True)

    class Meta:
        model = PedidoCompra
        fields = ['id', 'fornecedor', 'fornecedor_nome', 'status', 'data_pedido', 'data_recebimento', 'responsavel_pedido', 'responsavel_nome', 'itens']
        read_only_fields = ['responsavel_pedido']

    def create(self, validated_data):
        itens_data = validated_data.pop('itens')
        pedido = PedidoCompra.objects.create(**validated_data)
        for item_data in itens_data:
            ItemPedidoCompra.objects.create(pedido_compra=pedido, **item_data)
        return pedido
    
class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = '__all__'

class ItemPedidoVendaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemPedidoVenda
        fields = ['produto', 'quantidade', 'preco_unitario']

class PedidoVendaSerializer(serializers.ModelSerializer):
    itens = ItemPedidoVendaSerializer(many=True, read_only=True)
    itens_para_criar = ItemPedidoVendaSerializer(many=True, write_only=True)
    cliente_nome = serializers.CharField(source='cliente.nome', read_only=True)
    responsavel_nome = serializers.CharField(source='responsavel_venda.username', read_only=True)
    
    class Meta:
        model = PedidoVenda
        fields = [
            'id', 'cliente', 'cliente_nome', 'status', 'data_pedido', 'data_despacho',
            'responsavel_venda', 'responsavel_nome',
            'itens',
            'itens_para_criar'
        ]
        read_only_fields = ['responsavel_venda']

    def create(self, validated_data):
        itens_data = validated_data.pop('itens_para_criar')
        pedido = PedidoVenda.objects.create(**validated_data)

        for item_data in itens_data:
            ItemPedidoVenda.objects.create(pedido_venda=pedido, **item_data)

        return pedido

