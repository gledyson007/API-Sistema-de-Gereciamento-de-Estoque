import django_filters
from .models import Produto

class ProdutoFilter(django_filters.FilterSet):
    preco_maior_que = django_filters.NumberFilter(field_name="preco_venda", lookup_expr="gt")
    preco_menor_que = django_filters.NumberFilter(field_name="preco_venda", lookup_expr='lt')

    class Meta:
        model = Produto
        fields = ['categoria', 'fornecedor']