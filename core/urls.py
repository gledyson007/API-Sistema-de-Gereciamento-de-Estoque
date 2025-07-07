from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoriaViewSet, FornecedorViewSet, ProdutoViewSet, ArmazemViewSet, EstoqueViewSet, RelatorioBaixoEstoqueView, PedidoCompraViewSet, ClienteViewSet, PedidoVendaViewSet, DashboardView

router = DefaultRouter()

router.register(r'categorias', CategoriaViewSet, basename='categoria')
router.register(r'fornecedores', FornecedorViewSet, basename='fornecedor')
router.register(r'produtos', ProdutoViewSet, basename='produto')
router.register(r'armazens', ArmazemViewSet, basename='armazem')
router.register(r'estoque', EstoqueViewSet, basename='estoque')
router.register(r'pedidos/compra', PedidoCompraViewSet, basename='pedido-compra')
router.register(r'clientes', ClienteViewSet, basename='cliente')
router.register(r'pedidos/venda', PedidoVendaViewSet, basename='pedido-venda')

urlpatterns = [
    path('', include(router.urls)),
    path('relatorios/baixo-estoque/', RelatorioBaixoEstoqueView.as_view(), name='relatorio-baixo-estoque'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
]
