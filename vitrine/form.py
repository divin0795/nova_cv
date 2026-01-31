# vitrine/forms.py
from django import forms
from .models import Feedback
from .models import ReponseFeedback
from .models import Order
from .models import TransactionsValide

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['nom', 'email', 'message']

class ReponseFeedbackForm(forms.ModelForm):
    class Meta:
        model = ReponseFeedback
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Votre réponse ici...'})
        }
        
class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['produit', 'nom', 'telephone', 'email', 'mode', 'transaction']

    def clean_transaction(self):
        numero = self.cleaned_data['transaction']
        if Order.objects.filter(transaction=numero).exists():
            raise forms.ValidationError("Ce numéro de transaction est déjà utilisé.")
        if not TransactionsValide.objects.filter(numero_transaction=numero).exists():
            raise forms.ValidationError("Numéro de transaction invalide ou non trouvé.")
        return numero

    def clean(self):
        cleaned_data = super().clean()
        produit = cleaned_data.get('produit')
        prix_reel = {
            'CV_SIMPLE': 3000,
            'CV_BASIQUE': 5000,
            'CV_AVANCE': 8000,
            'CV_SITE': 12000,
        }.get(produit)
        cleaned_data['prix'] = prix_reel
        return cleaned_data
