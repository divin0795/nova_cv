import requests

ngrok_url = 'https://dfb7-102-129-92-93.ngrok-free.app/sms-webhook/'

# Message Airtel — format avec nom
message = (
    "Trans.ID:CI250424.1537.B29278 Vous avez recu 5200.00 CFA du 057916806 de 9350003. Solde actuel: 5225.00 CFA."
)

headers = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Linux; Android 11; Pixel 4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Mobile Safari/537.36",
    "Accept": "*/*",
}

payload = {
    "message": message
}

try:
    response = requests.post(ngrok_url, json=payload, headers=headers, timeout=10)
    print(f"✅ Statut : {response.status_code}")
    print(f"✅ Réponse : {response.text}")
except requests.exceptions.RequestException as e:
    print(f"❌ Erreur lors de la requête : {e}")
