from enum import Enum
M_LOGIN = "freelance_user_5dcfe1e724186"
M_KEY = "afc202c8990df4dcb92c08edb427c4da1e7563fd"


class TransactionType(str, Enum):
    PURCHASE = 'PURCHASE'
    SETTLE = 'SETTLE'
    CHARGE = 'CHARGE'
    REFUND = 'REFUND'
    CHECK_STATUS = 'CHECK_STATUS'
    P2P_CREDIT = 'P2P_CREDIT'
    CREATE_INVOICE = 'CREATE_INVOICE'
    P2_PHONE = 'P2_PHONE'
    TRANSACTION_LIST = 'TRANSACTION_LIST'
    WEBHOOK = 'WEBHOOK'


SIGNATURE_FIELDS = {
    TransactionType.PURCHASE: [
        'merchantAccount',
        'merchantDomainName',
        'orderReference',
        'orderDate',
        'amount',
        'currency',
        'productName',
        'productCount',
        'productPrice',
    ],
    TransactionType.WEBHOOK: [
        'orderReference',
        'status',
        'time'
    ],
    TransactionType.REFUND: [
        'merchantAccount',
        'orderReference',
        'amount',
        'currency',
    ],
    TransactionType.CHECK_STATUS: [
        'merchantAccount',
        'orderReference',
    ],
    TransactionType.SETTLE: [
        'merchantAccount',
        'orderReference',
        'amount',
        'currency',
    ],
    TransactionType.P2P_CREDIT: [
        'merchantAccount',
        'orderReference',
        'amount',
        'currency',
        'cardBeneficiary',
        'rec2Token',
    ],
    TransactionType.P2_PHONE: [
        'merchantAccount',
        'orderReference',
        'amount',
        'currency',
        'phone',
    ],
    TransactionType.TRANSACTION_LIST: [
        'merchantAccount',
        'dateBegin',
        'dateEnd',
    ],
}


SIGNATURE_FIELDS[TransactionType.CHARGE] = SIGNATURE_FIELDS[TransactionType.CREATE_INVOICE] = SIGNATURE_FIELDS[TransactionType.PURCHASE]

