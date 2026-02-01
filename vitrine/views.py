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
import jwt
from jwt import InvalidTokenError
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
            order.prix = form.cleaned_data['prix']
            ok, meta = verify_payment(order)
            
            if ok:
                order.statut = 'PAID'
                order.meta = meta
                order.save()  # ici code_commande est généré automatiquement

                send_mail(
                    subject="Confirmation de commande",
                    message=(
                        f"Bonjour {order.nom},\n\n"
                        f"Votre commande pour : {order.get_produit_display()} a été validée.\n"
                        f"Montant payé : {order.prix} FCFA via {order.mode}.\n"
                        f"Transaction : {order.transaction}\n"
                        f"Code commande : {order.code_commande}\n\n"
                        "Merci pour votre confiance !"
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[order.email],
                    fail_silently=False,
                )

                messages.success(request, "Commande validée avec succès.")
                return render(request, 'vitrine/commande.html', {
                    'form': OrderForm(),
                    'confirmation': True,
                    'produit': order.get_produit_display(),
                    'prix': order.prix,
                    'mode': order.mode,
                    'numero': order.transaction,
                    'nom': order.nom,
                    'telephone': order.telephone,
                    'email': order.email,
                    'code_commande': order.code_commande,
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

import json, hmac, hashlib, re
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

@csrf_exempt
def sms_webhook(request):
    print(f"[+] Reçu {request.method} sur /sms-webhook/")

    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    # 1. Signature HTTP SMS (HMAC SHA256 sur le RAW BODY)
    signature = request.headers.get("X-HTTPSMS-SIGNATURE")
    if not signature:
        return JsonResponse({"error": "Missing HTTPSMS signature"}, status=401)

    raw_body = request.body

    expected_signature = hmac.new(
        settings.HTTPSMS_SIGNING_KEY.encode(),
        raw_body,
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(signature, expected_signature):
        return JsonResponse({"error": "Invalid HTTPSMS signature"}, status=401)

    # 2. JSON STRICT uniquement
    if request.content_type != "application/json":
        return JsonResponse({"error": "Invalid content type"}, status=400)

    try:
        data = json.loads(raw_body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON payload"}, status=400)

    print("[PAYLOAD HTTPSMS]", data)

    # 3. Champs contractuels HTTP SMS
    message_id = data.get("id")
    sender = data.get("from")
    message = data.get("message")

    if not message_id or not sender or not message:
        return JsonResponse({"error": "Missing required fields"}, status=400)

    # 4. Anti-replay (obligatoire)
    if TransactionsValide.objects.filter(message_id=message_id).exists():
        return JsonResponse({"status": "duplicate"}, status=200)

    sender_norm = sender.lower().strip()

    operateur = montant = numero_transaction = None

    # 5. MTN Mobile Money
    if sender_norm in ["mobilemoney", "mtn"]:
        match = re.search(
            r"recu\s+(\d+(?:[.,]\d{1,2})?)\s*(?:xaf|cfa).*?id[:\s]*([0-9]+)",
            message,
            re.IGNORECASE
        )
        if not match:
            return JsonResponse({"error": "Unrecognized MTN SMS"}, status=400)

        montant = int(float(match.group(1).replace(",", ".")))
        numero_transaction = match.group(2)
        operateur = "MTN"

    # 6. Airtel Money
    elif sender_norm == "161":
        match = re.search(
            r"id[:\s]*([A-Z0-9.]+).*?recu\s+(\d+(?:[.,]\d{1,2})?)",
            message,
            re.IGNORECASE
        )
        if not match:
            return JsonResponse({"error": "Unrecognized Airtel SMS"}, status=400)

        numero_transaction = match.group(1)
        montant = int(float(match.group(2).replace(",", ".")))
        operateur = "AIRTEL"

    else:
        return JsonResponse(
            {"error": f"Unauthorized sender: {sender}"},
            status=403
        )

    # 7. Enregistrement
    TransactionsValide.objects.create(
        message_id=message_id,
        numero_transaction=numero_transaction,
        montant=montant,
        operateur=operateur
    )

    return JsonResponse({"status": "ok"}, status=200)
    
# Pages statiques
def politique_confidentialite(request):
    return render(request, 'vitrine/politique.html')

def mentions_legales(request):
    return render(request, 'vitrine/mentions.html')