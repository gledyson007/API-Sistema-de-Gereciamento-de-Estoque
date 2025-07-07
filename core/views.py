from django.db.models import F, Sum, DecimalField
from django.db.models.functions import Coalesce
from rest_framework.views import APIView
from django.db import transaction
from rest_framework import viewsets, status
from django.utils import timezone
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from .permissions import IsGerente 
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Categoria, Fornecedor, MovimentacaoEstoque, Produto, Armazem, EstoqueItem, PedidoCompra, Cliente, PedidoVenda, ItemPedidoVenda
from .filters import ProdutoFilter
from .serializers import CategoriaSerializer, ForncedorSerializer, ProdutoSerializer, ArmazemSerializer, EstoqueItemSerializer, RelatorioBaixoEstoqueSerializer, MovimentacaoEstoqueSerializer, PedidoCompraSerializer, ClienteSerializer, PedidoVendaSerializer
from .webhooks import enviar_webhook_baixo_estoque

class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    permission_classes = [IsAuthenticated]

class FornecedorViewSet(viewsets.ModelViewSet):
    queryset = Fornecedor.objects.all()
    serializer_class = ForncedorSerializer
    permission_classes = [IsAuthenticated]

class ProdutoViewSet(viewsets.ModelViewSet):
    queryset = Produto.objects.all()
    serializer_class = ProdutoSerializer
    filterset_class = ProdutoFilter
    search_fields = ['nome', 'sku', 'descricao', 'categoria__nome']
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAdminUser | IsGerente]
        return [permission() for permission in permission_classes]
    
    @action(detail=True, methods=['get'])
    def historico(self, request, pk=None):
        try:
            produto = self.get_object()
            movimentacoes = MovimentacaoEstoque.objects.filter(produto=produto)

            page = self.paginate_queryset(movimentacoes)
            if page is not None:
                serializer = MovimentacaoEstoqueSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = MovimentacaoEstoqueSerializer(movimentacoes, many=True)
            return Response(serializer.data)
        except Produto.DoesNotExist:
            return Response({"erro": "Produto não encontrado"}, status=status.HTTP_404_NOT_FOUND)
     
class ArmazemViewSet(viewsets.ModelViewSet):
    queryset = Armazem.objects.all()
    serializer_class = ArmazemSerializer

class EstoqueViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = EstoqueItem.objects.select_related('produto', 'armazem').all()
    serializer_class = EstoqueItemSerializer

    @action(detail=False, methods=['post'])
    def entrada(self, request):
        produto_id = request.data.get('produto_id')
        armazem_id = request.data.get('armazem_id')
        quantidade = int(request.data.get('quantidade', 0))
        motivo = request.data.get('motivo', 'Entrada manual')

        if quantidade <= 0:
            return Response({'erro': 'A quantidade deve ser positiva.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                item, created = EstoqueItem.objects.get_or_create(
                    produto_id=produto_id,
                    armazem_id=armazem_id,
                    defaults={'quantidade': 0}
                )

                item.quantidade += quantidade
                item.save()

                MovimentacaoEstoque.objects.create(
                    produto_id=produto_id,
                    armazem_id=armazem_id,
                    quantidade=quantidade,
                    responsavel=request.user,
                    tipo='ENTRADA',
                    motivo=motivo
                )
            return Response({'status': 'Entrada realizada com sucesso!', 'nova_quantidade': item.quantidade}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'erro': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    @action(detail=False, methods=['post'])
    def saida(self, request):
            produto_id = request.data.get('produto_id')
            armazem_id = request.data.get('armazem_id')
            quantidade = int(request.data.get('quantidade', 0))
            motivo = request.data.get('motivo', 'Saída manual')

            if quantidade <= 0:
                return Response({'erro': 'A quantidade deve ser positiva.'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                with transaction.atomic():
                    item = EstoqueItem.objects.get(produto_id=produto_id, armazem_id=armazem_id)

                    if item.quantidade < quantidade:
                        return Response({'erro': 'Estoque insuficiente.'}, status=status.HTTP_400_BAD_REQUEST)

                    item.quantidade -= quantidade
                    item.save()

                    MovimentacaoEstoque.objects.create(
                        produto_id=produto_id,
                        armazem_id=armazem_id,
                        quantidade=-quantidade, 
                        responsavel=request.user,
                        tipo='SAIDA',
                        motivo=motivo
                    )
                return Response({'status': 'Saída realizada com sucesso!', 'nova_quantidade': item.quantidade}, status=status.HTTP_200_OK)
            except EstoqueItem.DoesNotExist:
                return Response({'erro': 'Este produto não existe no estoque deste armazém.'}, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                return Response({'erro': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)    
            
class RelatorioBaixoEstoqueView(APIView):
    def get(self, request, format=None):
        itens_com_minimo = EstoqueItem.objects.annotate(
            estoque_minimo_produto=F('produto__estoque_minimo')
        )

        itens_baixo_estoque = itens_com_minimo.filter(
            quantidade__lte=F('estoque_minimo_produto')
        ).select_related('produto', 'armazem')

        if not itens_baixo_estoque.exists():
            return Response({"mensagem": "Nenhum produto com baixo estoque encontrado."}, status=200)

        serializer = RelatorioBaixoEstoqueSerializer(itens_baixo_estoque, many=True)
        return Response(serializer.data)
    
class PedidoCompraViewSet(viewsets.ModelViewSet):
    queryset = PedidoCompra.objects.prefetch_related('itens').all()
    serializer_class = PedidoCompraSerializer
    permission_classes = [IsGerente | IsAdminUser]

    def perform_create(self, serializer):
        serializer.save(responsavel_pedido=self.request.user)


    @action(detail=True, methods=['post'])
    def receber_pedido(self, request, pk=None):
        pedido = self.get_object()
        armazem_id = request.data.get('armazem_id')

        if pedido.status != 'APROVADO':
            return Response({'erro': 'Apenas pedidos com status "Aprovado" podem ser recebidos.'}, status=status.HTTP_400_BAD_REQUEST)
        if not armazem_id:
            return Response({'erro': 'O ID do armazem é obrigatório.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            with transaction.atomic():
                for item_pedido in pedido.itens.all():
                    item_estoque, created = EstoqueItem.objects.get_or_create(
                        produto=item_pedido.produto,
                        armazem_id=armazem_id,
                        defaults={'quantidade': 0}
                    )
                    item_estoque.quantidade += item_pedido.quantidade
                    item_estoque.save()

                    MovimentacaoEstoque.objects.create(
                        produto=item_pedido.produto,
                        armazem_id=armazem_id,
                        quantidade=item_pedido.quantidade,
                        responsavel=request.user,
                        tipo='ENTRADA',
                        motivo=f"Recebimento do Pedido de Compra #{pedido.id}"
                    )
                
                pedido.status = 'RECEBIDO'
                pedido.data_recebimento = timezone.now()
                pedido.save()
            
            return Response({'status': f'Pedido #{pedido.id} recebido com sucesso!'})
        
        except Exception as e:
            return Response({'erro': f'Ocorreu um erro: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer

class PedidoVendaViewSet(viewsets.ModelViewSet):
    queryset = PedidoVenda.objects.all()
    serializer_class = PedidoVendaSerializer

    def perform_create(self, serializer):
        serializer.save(responsavel_venda=self.request.user)

    @action(detail=True, methods=['post'])
    def despachar_pedido(self, request, pk=None):
        pedido = self.get_object()
        armazem_id = request.data.get('armazem_id')

        if pedido.status != 'PAGO':
            return Response({'erro': 'Apenas pedidos com status "pago" podem ser despachados'}, status=status.HTTP_400_BAD_REQUEST)
        if not armazem_id:
            return Response({'erro': 'O ID do armazém de saída é obrigatório.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            with transaction.atomic():
                for item_pedido in pedido.itens.all():
                    item_estoque = EstoqueItem.objects.get(
                        produto=item_pedido.produto,
                        armazem_id=armazem_id
                    )

                    if item_estoque.quantidade < item_pedido.quantidade:
                        raise Exception(f"Estoque insuficiente para o produto {item_estoque.produto.nome}.")
                    
                    item_estoque.quantidade -= item_pedido.quantidade
                    item_estoque.save()

                    print(f"DEBUG: Estoque atual do produto '{item_estoque.produto.nome}': {item_estoque.quantidade}")
                    print(f"DEBUG: Estoque mínimo definido: {item_estoque.produto.estoque_minimo}")

                    if item_estoque.quantidade <= item_estoque.produto.estoque_minimo:
                        print("DEBUG: CONDIÇÃO ATENDIDA! Enviando webhook...")
                        enviar_webhook_baixo_estoque(item_estoque.produto, item_estoque)

                    MovimentacaoEstoque.objects.create(
                        produto=item_pedido.produto,
                        armazem_id=armazem_id,
                        quantidade=-item_pedido.quantidade,
                        responsavel=request.user,
                        tipo='SAIDA',
                        motivo=f"Saída para venda #{pedido.id}"
                    )
                
                pedido.status = 'DESPACHADO'
                pedido.data_despacho = timezone.now()
                pedido.save()
            
            return Response({'status': f'Pedido #{pedido.id} despachado com sucesso!'})
        except EstoqueItem.DoesNotExist:
            return Response({'erro': 'Um dos produtos não existe no estoque do armazém informado'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'erro': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class DashboardView(APIView):
    permission_classes = [IsGerente | IsAdminUser]

    def get(self, request, format=None):

        total_vendas = PedidoVenda.objects.filter(status='DESPACHADO').aggregate(
            total=Coalesce(Sum(F('itens__quantidade') * F('itens__preco_unitario')), 0, output_field=DecimalField())
        )['total']

        total_compras = PedidoCompra.objects.filter(status='RECEBIDO').aggregate(
            total=Coalesce(Sum(F('itens__quantidade') * F('itens__preco_unitario')), 0, output_field=DecimalField())
        )['total']

        valor_inventario = EstoqueItem.objects.aggregate(
            total=Coalesce(Sum(F('quantidade') * F('produto__preco_custo')), 0, output_field=DecimalField())
        )['total']

        produtos_baixo_estoque = EstoqueItem.objects.filter(
            quantidade__lte=F('produto__estoque_minimo')
        ).count()

        top_5_produtos = ItemPedidoVenda.objects.filter(
            pedido_venda__status='DESPACHADO'
        ).values(
            'produto__nome'
        ).annotate(
            total_vendido=Sum('quantidade')
        ).order_by(
            '-total_vendido'
        )[:5]

        data = {
            'total_vendas': total_vendas,
            'total_compras': total_compras,
            'valor_total_inventario': valor_inventario,
            'produtos_com_baixo_estoque': produtos_baixo_estoque,
            'top_5_produtos_vendidos': list(top_5_produtos)
        }

        return Response(data)