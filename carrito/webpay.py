from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from transbank.common.integration_type import IntegrationType
from transbank.common.options import WebpayOptions
from transbank.webpay.webpay_plus.transaction import Transaction


def _transaccion():
    # Si falta alguna credencial, se avisa antes de llamar a Webpay
    if not settings.WEBPAY_COMMERCE_CODE or not settings.WEBPAY_API_KEY:
        raise ImproperlyConfigured('Faltan WEBPAY_COMMERCE_CODE o WEBPAY_API_KEY en el .env')
    # El ambiente se elige según la variable del .env
    ambiente = IntegrationType.LIVE if settings.WEBPAY_ENV == 'LIVE' else IntegrationType.TEST
    opciones = WebpayOptions(
        commerce_code=settings.WEBPAY_COMMERCE_CODE,
        api_key=settings.WEBPAY_API_KEY,
        integration_type=ambiente,
    )
    return Transaction(opciones)


def crear_transaccion(orden, return_url):
    return _transaccion().create(
        orden.buy_order, f'usuario-{orden.user_id}', orden.total, return_url
    )


def confirmar(token):
    return _transaccion().commit(token)
