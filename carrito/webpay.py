from transbank.common.integration_api_keys import IntegrationApiKeys
from transbank.common.integration_commerce_codes import IntegrationCommerceCodes
from transbank.common.integration_type import IntegrationType
from transbank.common.options import WebpayOptions
from transbank.webpay.webpay_plus.transaction import Transaction


def _transaccion():
    # Ambiente de integración con credenciales públicas de prueba de Transbank.
    # En producción se usarían las credenciales reales desde variables de entorno.
    opciones = WebpayOptions(
        IntegrationCommerceCodes.WEBPAY_PLUS,
        IntegrationApiKeys.WEBPAY,
        IntegrationType.TEST,
    )
    return Transaction(opciones)


def crear_transaccion(orden, return_url):
    return _transaccion().create(
        orden.buy_order, f'usuario-{orden.user_id}', orden.total, return_url
    )


def confirmar(token):
    return _transaccion().commit(token)
