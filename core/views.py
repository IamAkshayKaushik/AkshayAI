from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse
# from datetime import datetime, timedelta
from .models import TokenPurchase, UserAction, Subscription, Usage, UserStripeRecord

import stripe
from social_django.utils import psa


stripe.api_key = settings.STRIPE_SECRET_KEY

@psa('social:complete')
def google_login(request):
    return request.backend.do_auth(request.backend, redirect_name='home')

@psa('social:complete')
def twitter_login(request):
    return request.backend.do_auth(request.backend, redirect_name='home')





@login_required
def dashboard(request):
    user = request.user
    subscription = Subscription.objects.filter(user=user)

    # Get the user's usage history
    usage_history = Usage.objects.filter(user=user).order_by('-timestamp')
    token_purchase = TokenPurchase.objects.filter(user=user)

    context = {
        'user': user,
        'subscription': subscription,
        'user_actions': usage_history,
        'token_transactions': token_purchase,
    }
    return render(request, 'core/dashboard.html', context)


@login_required
def buy_tokens(request):
    if request.method == 'POST':
        user = request.user
        customer = UserStripeRecord.objects.filter(user=user).first()
        token_required = int(request.POST.get('token_required'))

        if token_required < 10000:
            return redirect('home')

        token_cost = round(int(token_required) * settings.TOKEN_PRICE, 2)
        # customer_search = stripe.Customer.search(query=f"name:'{user.username}' AND metadata['user_id']:'{user.id}'",).data

        # print(customer_search)
        if not customer:
            customer_object = stripe.Customer.create(
                email=user.email,
                name=user.username,
                # address= {
                # "city": "San Francisco",
                # "country": "US",
                # "line1": "1 Hacker Way",
                # "line2": "Ste 2",
                # "postal_code": "35214",
                # "state": "California"
                # }
                metadata={'user_id': user.id},
                )
            customer = UserStripeRecord.objects.create(user=user, stripe_customer_id=customer_object['id'])

        # Create a Stripe payment intent
        intent = stripe.PaymentIntent.create(
            customer=customer.stripe_customer_id,
            # setup_future_usage='off_session',
            amount= int(token_cost * 100),
            currency='usd',
            description=f"{token_required} Tokens Purchase by {user.username}",
            automatic_payment_methods={
                'enabled': True,
            },
            metadata={'user_id': user.id},
        )

        context = {
            'clientSecret': intent['client_secret'],
            'customer_id': customer.stripe_customer_id,
            # 'client_secret': payment_intent.client_secret,
            # 'payment_intent_id': payment_intent.id,
            'token_required': token_required,
            'token_cost': token_cost,
            'STRIPE_PUBLIC_KEY':settings.STRIPE_PUBLIC_KEY
        }

        return render(request, 'core/confirm_payment.html', context)

    return render(request, 'core/buy_tokens.html')



@login_required
@csrf_exempt
def process_payment(request):
    user = request.user
    client_secret = request.GET.get('payment_intent')
    token_cost = float(request.GET.get('token_cost',0))

    stripe.api_key = settings.STRIPE_SECRET_KEY
    payment_intent = stripe.PaymentIntent.retrieve(client_secret)
    # try:
    #     payment_intent.confirm(payment_method=payment_method)
    # except stripe.error.CardError as e:
    #     # Handle payment error
    #     return HttpResponseBadRequest(e.error.message)
    # except stripe.error.StripeError as e:
    #     # Handle other Stripe errors
    #     return HttpResponseBadRequest(e.error.message)

    if payment_intent.status == 'succeeded':
        token_required = int(token_cost / settings.TOKEN_PRICE)

        # Update user's token balance
        user.tokens += token_required
        user.save()

        # Record token purchase
        token_purchase = TokenPurchase(user=user, amount=token_required, total_cost=token_cost)
        token_purchase.save()

        # Record user action
        action = f"Purchased {token_required} tokens for ${token_cost:.5f}"
        user_action = UserAction(user=user, action=action)
        user_action.save()

        return redirect('dashboard')
    else:
        # Handle payment failure
        return redirect('buy_tokens')




@csrf_exempt
def convert_text_to_audio(request):
    if request.method == 'POST':
        user = request.user
        text = request.POST.get('text')
        token_amount = int(request.POST.get('token_amount'))

        # Check if the user has sufficient tokens
        if user.tokens < token_amount:
            return JsonResponse({'success': False, 'message': 'Insufficient tokens.'})

        # Deduct tokens from the user's balance
        user.tokens -= token_amount
        user.save()

        # Perform the conversion using the elevenlabs.io API (implementation not provided)

        # Record user action
        action = f"Converted text to audio: {text}"
        user_action = UserAction(user=user, action=action)
        user_action.save()

        # Record usage
        usage = Usage(user=user, action=action)
        usage.save()

        return JsonResponse({'success': True, 'message': 'Text converted to audio.'})

    return JsonResponse({'success': False, 'message': 'Invalid request.'})
