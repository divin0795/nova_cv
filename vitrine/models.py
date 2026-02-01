import uuid
from django.db import models
    
class Feedback(models.Model):
    nom = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nom} - {self.email}"

class ReponseFeedback(models.Model):
    feedback = models.ForeignKey(Feedback, on_delete=models.CASCADE, related_name='reponses')
    message = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Réponse à {self.feedback.email} le {self.date.strftime('%d/%m/%Y')}"
    
class Order(models.Model):
    PRODUCTS = [
        ('CV_SIMPLE',  'CV Simple'),
        ('CV_BASIQUE', 'CV Numérique Basique'),
        ('CV_AVANCE',  'CV Numérique Avancé'),
        ('CV_SITE',    'CV + Site Vitrine'),
    ]
    STATUTS = [
        ('PENDING', 'En attente'),
        ('PAID',    'Payé'),
        ('FAILED',  'Échoué'),
    ]
    MODES = [
        ('AIRTEL', 'Airtel Money'),
        ('MTN',    'MTN Money'),
    ]

    produit     = models.CharField(max_length=20, choices=PRODUCTS)
    prix        = models.PositiveIntegerField()
    nom         = models.CharField(max_length=100)
    telephone   = models.CharField(max_length=20)
    email       = models.EmailField()
    mode        = models.CharField(max_length=15, choices=MODES)  # sécurisation ici
    transaction = models.CharField(max_length=100, unique=True)
    statut      = models.CharField(max_length=10, choices=STATUTS, default='PENDING')
    meta        = models.JSONField(blank=True, null=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_produit_display()} – {self.transaction}"
    
    code_commande = models.CharField(
        max_length=12, unique=True, blank=True, null=True, editable=False
    )
    
    def save(self, *args, **kwargs):
        if not self.code_commande:
            self.code_commande = f"CMD-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)


class TransactionsValide(models.Model):
    message_id = models.CharField(max_length=100, unique=True, default="")  # Default ajouté
    numero_transaction = models.CharField(max_length=100, unique=True)
    montant = models.FloatField()
    operateur = models.CharField(max_length=20)
    date_ajout = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.operateur} - {self.numero_transaction}"
