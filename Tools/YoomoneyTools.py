from yoomoney import Authorize, Client, Quickpay

import os
from dotenv import load_dotenv

load_dotenv(dotenv_path='../.env')


def authorize():
    Authorize(
        client_id=os.getenv("YOOMONEY_CLIENT_ID"),
        redirect_uri=os.getenv("YOOMONEY_REDIRECT_URI"),
        scope=["account-info",
               "operation-history",
               "operation-details",
               "incoming-transfers",
               "payment-p2p",
               "payment-shop",
               ]
    )


def get_info(token: str):
    client = Client(token)

    user = client.account_info()

    print("Account number:", user.account)
    print("Account balance:", user.balance)
    print("Account currency code in ISO 4217 format:", user.currency)
    print("Account status:", user.account_status)
    print("Account type:", user.account_type)

    print("Extended balance information:")
    for pair in vars(user.balance_details):
        print("\t-->", pair, ":", vars(user.balance_details).get(pair))

    print("Information about linked bank cards:")
    cards = user.cards_linked

    if len(cards) != 0:
        for card in cards:
            print(card.pan_fragment, " - ", card.type)
    else:
        print("No card is linked to the account")


def create_cheque(cost: int, receiver: str, message: str):
    quickpay = Quickpay(
        receiver=receiver,
        quickpay_form="shop",
        targets=message,
        paymentType="SB",
        sum=cost,
        label='bv5vc4xd'
    )
    # print(quickpay.base_url)
    # print(quickpay.redirected_url)
    return quickpay.redirected_url


def check_pay(token: str, label: str):
    # Вернёт данные последнего платежа
    client = Client(token)
    history = client.operation_history(label=label)
    # print("List of operations:")
    # print("Next page starts with: ", history.next_record)
    for operation in history.operations:
        data = dict()
        if operation:
            data['Operation'] = operation.operation_id
            data['Status'] = operation.status
            data['Datetime'] = operation.datetime
            data['Title'] = operation.title
            data['Pattern id'] = operation.pattern_id
            data['Direction'] = operation.direction
            data['Amount'] = operation.amount
            data['Label'] = operation.label
            data['Type'] = operation.type
        return data


# get_info(os.getenv('YOOMONEY_TOKEN'))
# print(create_cheque(receiver=os.getenv('YOOMONEY_RECEIVER'), message='Test', cost=3))
# print(check_pay(token=os.getenv('YOOMONEY_TOKEN'), label='bv5vc4xd'))
