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

    url_destino = request.build_absolute_uri()
    link_kw = {
        "api_key": settings.STRIPE_SECRET,
        "stripe_account": fundacion.stripe_id,
        "after_completion": {"type": "redirect", "redirect": {"url": url_destino}},
    }

    product = stripe.Product.create(
        api_key=settings.STRIPE_SECRET,
        name="Subscription",
        stripe_account=fundacion.stripe_id,
    )
    price = stripe.Price.create(
        api_key=settings.STRIPE_SECRET,
        currency="usd",
        product=product.id,
        stripe_account=fundacion.stripe_id,
        unit_amount=5000,
        recurring={
            "interval": "month",
        },
    )
    link_subscription = stripe.PaymentLink.create(
        line_items=[
            {
                "price": price.id,
                "quantity": 1,
            },
        ],
        **link_kw
    )

    product = stripe.Product.create(
        api_key=settings.STRIPE_SECRET,
        name="Donación 25$",
        stripe_account=fundacion.stripe_id,
    )
    price = stripe.Price.create(
        api_key=settings.STRIPE_SECRET,
        unit_amount=2500,
        currency="usd",
        product=product.id,
        # custom_unit_amount={"enabled": True},
        stripe_account=fundacion.stripe_id,
    )
    link_25 = stripe.PaymentLink.create(
        line_items=[
            {
                "price": price.id,
                "quantity": 1,
            },
        ],
        **link_kw
    )

    product = stripe.Product.create(
        api_key=settings.STRIPE_SECRET,
        name="Donación 100$",
        stripe_account=fundacion.stripe_id,
    )
    price = stripe.Price.create(
        api_key=settings.STRIPE_SECRET,
        unit_amount=10000,
        currency="usd",
        product=product.id,
        # custom_unit_amount={"enabled": True},
        stripe_account=fundacion.stripe_id,
    )
    link_100 = stripe.PaymentLink.create(
        line_items=[
            {
                "price": price.id,
                "quantity": 1,
            },
        ],
        **link_kw
    )

    product = stripe.Product.create(
        api_key=settings.STRIPE_SECRET,
        name="Donación 120$",
        stripe_account=fundacion.stripe_id,
    )
    price = stripe.Price.create(
        api_key=settings.STRIPE_SECRET,
        unit_amount=12000,
        currency="usd",
        product=product.id,
        # custom_unit_amount={"enabled": True},
        stripe_account=fundacion.stripe_id,
    )
    link_120 = stripe.PaymentLink.create(
        line_items=[
            {
                "price": price.id,
                "quantity": 1,
            },
        ],
        **link_kw
    )

    product = stripe.Product.create(
        api_key=settings.STRIPE_SECRET,
        name="Other Amount",
        stripe_account=fundacion.stripe_id,
    )
    price = stripe.Price.create(
        api_key=settings.STRIPE_SECRET,
        currency="usd",
        product=product.id,
        custom_unit_amount={"enabled": True},
        stripe_account=fundacion.stripe_id,
    )
    link_custom = stripe.PaymentLink.create(
        line_items=[
            {
                "price": price.id,
                "quantity": 1,
            },
        ],
        **link_kw
    )

    return render(
        request,
        "donar.html",
        {
            "fundacion": fundacion,
            "STRIPE_KEY": settings.STRIPE_KEY,
            "link_25": link_25,
            "link_100": link_100,
            "link_120": link_120,
            "link_custom": link_custom,
            "link_subscription": link_subscription,
        },
    )
