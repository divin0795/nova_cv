import requests
import json

# === URL de ton webhook (modifie-la si besoin) ===
url = "https://nova-cv.onrender.com/sms-webhook/"

# === Données simulées ===
payload = {
    "key": "De : 161()\nTrans. ID : PP250609.0916.A76749. Vous avez reçu 14500.00 CFA du 053584351 de ENARQUE PRINCIA. Votre vendu est de 14552.50 CFA",
    "time": "09/06 09:16 AM",
    "secret": "smswebhookdepot",
    "sender": "161"  # ← C'est ça qui manque
}


# === En-têtes pour indiquer qu'on envoie du JSON ===
headers = {
    "Content-Type": "application/json"
}

# === Requête POST simulée ===
response = requests.post(url, headers=headers, data=json.dumps(payload))

# === Affichage du résultat ===
print("Statut :", response.status_code)
print("Réponse :", response.text)
