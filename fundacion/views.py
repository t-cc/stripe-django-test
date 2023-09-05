import stripe
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from fundacion.models import Fundacion


def home(request):
    fundacion = Fundacion.objects.filter(user_id=request.user.id).first()
    fundacion_id = fundacion.pk if fundacion else None
    return render(
        request,
        "home.html",
        {
            "fundacion": fundacion,
            "fundacion_list": Fundacion.objects.exclude(id=fundacion_id),
        },
    )


@login_required
def conectar(request):
    try:
        fundacion = Fundacion.objects.get(user=request.user)
    except Fundacion.DoesNotExist:
        data = stripe.Account.create(
            api_key=settings.STRIPE_SECRET,
            country="ES",
            type="express",
            email=request.user.email,
            # requested_capabilities=["card_payments", "transfers"],
        )
        fundacion = Fundacion(user=request.user, stripe_id=data.get("id"))
        fundacion.save()
    if fundacion and fundacion.stripe_id:
        url_destino = request.build_absolute_uri().replace(request.path, "")
        data = stripe.AccountLink.create(
            api_key=settings.STRIPE_SECRET,
            account=fundacion.stripe_id,
            refresh_url=url_destino,
            return_url=url_destino,
            type="account_onboarding",
        )
        return redirect(data.get("url"))
    else:
        raise Exception("No existe stripe_id")


def donar(request, fundacion_id):
    fundacion = get_object_or_404(Fundacion, pk=fundacion_id)
    # print(fundacion.stripe_account)
    indent = None
    link = None
    indent = stripe.PaymentIntent.create(
        api_key=settings.STRIPE_SECRET,
        payment_method_types=["card"],
        amount=18000,
        currency="eur",
        application_fee_amount=0,
        stripe_account=fundacion.stripe_id,
    )
    print(indent)
    product = stripe.Product.create(
        api_key=settings.STRIPE_SECRET,
        name="Donación",
        stripe_account=fundacion.stripe_id,
    )
    price = stripe.Price.create(
        api_key=settings.STRIPE_SECRET,
        unit_amount=1200,
        currency="usd",
        product=product.id,
        # custom_unit_amount={"enabled": True},
        stripe_account=fundacion.stripe_id,
    )
    # print(price)
    link = stripe.PaymentLink.create(
        api_key=settings.STRIPE_SECRET,
        line_items=[
            {
                "price": price.id,
                "quantity": 1,
            },
        ],
        stripe_account=fundacion.stripe_id,
    )
    print(link)
    return render(
        request,
        "donar.html",
        {
            "fundacion": fundacion,
            "indent": indent,
            "STRIPE_KEY": settings.STRIPE_KEY,
            "link": link,
        },
    )
