from django.shortcuts import render, redirect,get_object_or_404
from django.http import HttpResponse
from django.core.mail import EmailMessage
from django.conf import settings
from decimal import Decimal
from django.core.mail import send_mail
from .models import Feedback, ReponseFeedback
from .form import FeedbackForm, ReponseFeedbackForm
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.views import View
import unicodedata
from .models import Order
import re
from .form import OrderForm 
import os, uuid, requests
from .models import TransactionsValide
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from django.utils.dateparse import parse_datetime
import logging
from .models import TransactionsValide
logger = logging.getLogger(__name__)

def index(request):
    return render(request, 'vitrine/index.html')

def cv(request):
    return render(request, 'vitrine/cv.html')

def coiffeuse(request):
    return render(request, 'vitrine/coiffeuse.html')

def portfolio(request):
    return render(request, 'vitrine/portfolio.html')

# 🔍 Filtrage éthique simple
def est_ethique(message):
    mots_interdits = ['insulte', 'haine', 'spam']
    return not any(mot in message.lower() for mot in mots_interdits)


# Feedbacks
def feedback(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            message = form.cleaned_data['message']
            if est_ethique(message):
                form.save()
                return render(request, 'vitrine/merci.html')
            else:
                form.add_error('message', "Message inapproprié détecté.")
    else:
        form = FeedbackForm()
    return render(request, 'vitrine/feedback.html', {'form': form})


def liste_feedbacks(request):
    feedbacks = Feedback.objects.order_by('-date')
    feedbacks = Feedback.objects.exclude(id__isnull=True)
    return render(request, 'vitrine/liste_feedbacks.html', {'feedbacks': feedbacks})

@staff_member_required
def repondre_feedback(request, feedback_id): 
    feedback = get_object_or_404(Feedback, id=feedback_id)

    if request.method == 'POST':
        message = request.POST.get('message')

        try:
            send_mail(
                subject="Réponse à votre feedback",
                message=message,
                from_email="divin3448@gmail.com",
                recipient_list=[feedback.email],
                fail_silently=False,
            )
            ReponseFeedback.objects.create(feedback=feedback, message=message)
            messages.success(request, "Réponse envoyée et enregistrée avec succès.")
            return redirect('liste_feedbacks')

        except Exception as e:
            messages.error(request, f"Erreur lors de l'envoi : {e}")

    form = ReponseFeedbackForm()
    return render(request, 'vitrine/repondre_feedback.html', {
        'feedback': feedback,
        'form': form
    })
    
# ===== Fonctions de vérification =====

# vitrine/views.py ou où tu fais la vérification
from .models import TransactionsValide

# -------------------------  COMMANDE  ------------------------- #
def verify_payment(order: Order):
    numero = order.transaction.strip().upper()
    op = order.mode.strip().upper()
    operateur = 'MTN' if op.startswith('MTN') else 'AIRTEL'
    montant = int(order.prix)

    try:
        paiement = TransactionsValide.objects.get(
            numero_transaction=numero,
            operateur=operateur,
        )
        if paiement.montant == montant:
            return True, {"montant": paiement.montant}
        return False, "Montant incorrect"
    except TransactionsValide.DoesNotExist:
        return False, "Transaction introuvable"

def commande(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            # Récupérer le prix validé côté serveur dans le form.cleaned_data
            order.prix = form.cleaned_data['prix']
            ok, meta = verify_payment(order)
            if ok:
                order.statut = 'PAID'
                order.meta = meta
                order.save()

                send_mail(
                subject="Confirmation de commande",
                message=(
                    f"Bonjour {order.nom},\n\n"
                    f"Nous avons bien reçu votre commande pour : {order.get_produit_display()}.\n"
                    f"Montant payé : {order.prix} FCFA via {order.mode}.\n"
                    f"Transaction : {order.transaction}\n\n"
                    f"Merci pour votre confiance !"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[order.email],
                fail_silently=False,
            )


                messages.success(request, "Commande validée avec succès.")
                return render(request, 'vitrine/commande.html', {
                    'form': OrderForm(),  # Nouveau formulaire vide pour réafficher après succès
                    'confirmation': True,
                    'produit': order.get_produit_display(),
                    'prix': order.prix,
                    'mode': order.mode,
                    'numero': order.transaction,
                    'nom': order.nom,
                    'telephone': order.telephone,
                    'email': order.email,
                })

            else:
                form.add_error('transaction', meta)

        # formulaire invalide ou paiement non valide
        return render(request, 'vitrine/commande.html', {'form': form, 'confirmation': False})

    else:
        form = OrderForm()
        return render(request, 'vitrine/commande.html', {'form': form, 'confirmation': False})

import json
import re
import unicodedata
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from .models import TransactionsValide

# 🔐 Clé secrète partagée (à mettre aussi dans l'app SMS Forwarder)

def normalize_text(text):
    text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('utf-8')
    text = re.sub(r'\s+', ' ', text)
    return text.strip().lower()

@csrf_exempt
def sms_webhook(request):
    print(f"[+] Reçu {request.method} sur /sms-webhook/")

    if request.method != 'POST':
        print("[!] Méthode non autorisée")
        return JsonResponse({'status': 'error', 'message': 'Méthode non autorisée'}, status=405)

    try:
        data = json.loads(request.body)
        print(f"[Données brutes reçues] {data}")

        received_secret = data.get('secret')
        print(f"[DEBUG] Clé reçue : {received_secret}")
        print(f"[DEBUG] Clé attendue : {settings.SHARED_SECRET}")

        if received_secret != settings.SHARED_SECRET:
            print("[!] Clé secrète invalide")
            return JsonResponse({'status': 'unauthorized', 'message': 'Clé secrète invalide'}, status=401)

        key_value = data.get('key') or ''
        message_original = data.get('message') or data.get('Message') or key_value or ''
        message_normalized = normalize_text(message_original)

        # Extraire proprement l’expéditeur
        sender_match = re.search(r'De\s*:\s*([^\n]+)', key_value)
        if sender_match:
            raw_sender = sender_match.group(1).strip()
            sender = re.sub(r'[^\w\d]', '', raw_sender).lower()
        else:
            sender = re.sub(r'\W+', '', key_value.split()[0]).lower() if key_value else ''

        print(f"[DEBUG] Sender extrait de 'key' : '{sender}'")
        print(f"[Message original] {message_original}")
        print(f"[Message normalisé] {message_normalized}")

        operateur = None
        montant = None
        numero_transaction = None

        # Traitement MTN
        if sender == 'mobilemoney':
            match_mtn = re.search(
                r'Vous avez recu\s+(\d+(?:[.,]\d{1,2})?)\s*(?:XAF|CFA).*?ID[:\s.]*([0-9]+)',
                message_original,
                re.IGNORECASE
            )
            if match_mtn:
                montant = int(float(match_mtn.group(1).replace(',', '.')))
                numero_transaction = match_mtn.group(2)
                operateur = 'MTN'
                print(f"[✔] MTN: montant={montant}, transaction={numero_transaction}")

        # Traitement Airtel
        elif sender == '161':
            match_airtel = re.search(
                r'Trans[\.:]?\s*ID[:\s\.]*([A-Z]{2}\d{6}\.\d{4}\.[A-Z0-9]+)\.?.*?Vous avez recu\s+(\d+(?:[.,]\d{1,2})?)\s*(?:XAF|CFA)',
                message_original,
                re.IGNORECASE
            )
            if match_airtel:
                numero_transaction = match_airtel.group(1).rstrip('.')
                montant = int(float(match_airtel.group(2).replace(',', '.')))
                operateur = 'AIRTEL'
                print(f"[✔] AIRTEL : montant={montant}, transaction={numero_transaction}")

        else:
            print(f"[✘] Expéditeur inconnu ou non autorisé : {sender}")
            return JsonResponse({'status': 'rejected', 'message': f'Expéditeur non autorisé : {sender}'}, status=403)

        if numero_transaction and montant:
            transaction, created = TransactionsValide.objects.get_or_create(
                numero_transaction=numero_transaction,
                defaults={
                    'montant': montant,
                    'operateur': operateur
                }
            )
            if created:
                print(f"[💾] Nouvelle transaction ajoutée : {numero_transaction}")
                return JsonResponse({'status': 'success', 'message': 'Transaction ajoutée'})
            else:
                print(f"[↩] Transaction déjà enregistrée : {numero_transaction}")
                return JsonResponse({'status': 'exists', 'message': 'Transaction déjà enregistrée'})

        print("[❌] Aucun motif valide trouvé dans le message")
        return JsonResponse({
            'status': 'error',
            'message': 'SMS non reconnu',
            'contenu_nettoye': message_normalized
        }, status=400)

    except Exception as e:
        print(f"[💥 Exception] {str(e)}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
# Pages statiques
def politique_confidentialite(request):
    return render(request, 'vitrine/politique.html')

def mentions_legales(request):
    return render(request, 'vitrine/mentions.html')