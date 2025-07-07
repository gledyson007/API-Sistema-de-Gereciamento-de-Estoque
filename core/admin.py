# Em core/admin.py
from django.contrib import admin
from .models import Categoria, Fornecedor, Produto
from .models import Armazem, EstoqueItem, MovimentacaoEstoque

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'descricao')
    search_fields = ('nome',)

@admin.register(Fornecedor)
class FornecedorAdmin(admin.ModelAdmin):
    list_display = ('nome_fantasia', 'cnpj', 'email', 'telefone')
    search_fields = ('nome_fantasia', 'cnpj')

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'sku', 'categoria', 'preco_venda', 'estoque_minimo')
    list_filter = ('categoria', 'fornecedor')
    search_fields = ('nome', 'sku', 'descricao')

@admin.register(Armazem)
class ArmazemAdmin(admin.ModelAdmin):
    list_display = ('nome', 'localizacao')
    search_fields = ('nome',)

@admin.register(EstoqueItem)
class EstoqueItemAdmin(admin.ModelAdmin):
    list_display = ('produto', 'armazem', 'quantidade')
    list_filter = ('armazem', 'produto__categoria')
    search_fields = ('produto__nome', 'produto__sku')

    readonly_fields = ('quantidade',)

@admin.register(MovimentacaoEstoque)
class MovimentacaoEstoqueAdmin(admin.ModelAdmin):
    list_display = ('data_movimentacao', 'produto', 'tipo', 'quantidade', 'armazem', 'responsavel')
    list_filter = ('tipo', 'armazem', 'data_movimentacao')
    search_fields = ('produto__nome', 'produto__sku', 'motivo')

    def has_change_permission(self, request, obj=None):
        return False
    def has_delete_permission(self, request, obj=None):
        return False