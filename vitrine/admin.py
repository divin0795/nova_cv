from django.contrib import admin
from .models import Feedback,Order,TransactionsValide

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("produit", "prix", "nom", "statut", "transaction", "created_at")
    search_fields = ("transaction", "nom", "telephone")

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ("nom", "email", "date")
    search_fields = ("nom", "email")
    
@admin.register(TransactionsValide)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('numero_transaction', 'montant', 'operateur', 'date_ajout')
    search_fields = ('numero_transaction', 'operateur')
    list_filter = ('operateur', 'date_ajout')
    ordering = ('-date_ajout',)  # Tri décroissant par date_ajout
    readonly_fields = ('date_ajout',)
