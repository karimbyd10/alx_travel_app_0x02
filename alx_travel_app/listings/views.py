import requests
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Payment

@api_view(['POST'])
def initiate_payment(request):
    """
    Initiates payment using Chapa API
    """
    booking_reference = request.data.get('booking_reference')
    amount = request.data.get('amount')
    customer_email = request.data.get('email')
    
    payload = {
        "amount": amount,
        "currency": "ETB",  # adjust if needed
        "email": customer_email,
        "tx_ref": booking_reference,
        "callback_url": "http://localhost:8000/api/verify_payment/"  # Change to production URL
    }

    headers = {
        "Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}"
    }

    response = requests.post(f"{settings.CHAPA_BASE_URL}/initialize", json=payload, headers=headers)
    data = response.json()

    if data.get("status") == "success":
        transaction_id = data["data"]["id"]
        Payment.objects.create(
            booking_reference=booking_reference,
            transaction_id=transaction_id,
            amount=amount,
            status="Pending"
        )
        return Response({"payment_link": data["data"]["checkout_url"]})
    
    return Response({"error": "Payment initiation failed"}, status=400)

