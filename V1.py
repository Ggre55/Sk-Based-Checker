import stripe
import requests
import logging

secret = "put key   here"
stripe.api_key = secret
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36'
def lookup_bin(cc):
    cctwo = cc[:6]
    headers = {
        'User-Agent': user_agent,
        'Host': 'lookup.binlist.net',
        'Cookie': '_ga=GA1.2.549903363.1545240628; _gid=GA1.2.82939664.1545240628',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    }

    url = f'https://lookup.binlist.net/{cctwo}'
    response = requests.get(url, headers=headers)

    fim = response.json()
    bank = fim['bank']['name']
    country = fim['country']['alpha2']
    if 'type' in fim:
        type = fim['type']
        if type == 'credit':
            type = 'Credit'
            return bank, country, type
        else:
            type = 'Debit'
            return bank, country, type

def check_stripe_secret_key(secret_key):
    try:
        stripe.api_key = secret_key
        account = stripe.Account.retrieve()
        print(f"The secret key is valid for the Stripe account {account.id}.")
        return True
    except stripe.error.AuthenticationError as e:
        logging.error(f"The secret key {secret_key} is invalid or doesn't have the necessary permissions: {e}")
        return False
    except Exception as e:
        logging.error(f"An error occurred while testing the secret key {secret_key}: {e}")
        return False

def get_random_user():
    response = requests.get("https://randomuser.me/api/?nat=us").json()
    user = response['results'][0]['name']
    phone = response['results'][0]['phone']
    address = response['results'][0]['location']
    email = response['results'][0]['email']
    
    first_name = user['first']
    last_name = user['last']
    city = address['city']
    state = address['state'].upper()
    zip_code = address['postcode']
    phone_number = phone.replace('(', '').replace(')', '').replace('-', '').replace(' ', '')
    
    return {
        "first_name": first_name,
        "last_name": last_name,
        "phone_number": phone_number,
        "city": city,
        "state": state,
        "zip_code": zip_code,
        "email": email
    }

def create_stripe_customer(token):
    user = get_random_user()
    customer = stripe.Customer.create(
        source=token,
        email=user['email'],
        description='Test customer'
    )
    logging.info(f"Customer created: {customer}")
    return customer

def create_stripe_charge(customer_id):
    charge = stripe.Charge.create(
        customer=customer_id,
        amount=100,  # $5000 is 50 USD in cents
        currency='usd',
        description='Test charge'
    )
    logging.info(f"Charge created: {charge}")
    return charge

def refund_stripe_charge(charge_id):
    refund = stripe.Refund.create(
        charge=charge_id,
        amount=100  # $50 USD in cents
    )
    logging.info(f"Refund created: {refund}")
    return refund

def charge_credit_card(cc, mm, yyyy, cvv):
    bank, country, type = lookup_bin(cc)
    
    try:
        token = stripe.Token.create(
            card={
                "number": cc,
                "exp_month": mm,
                "exp_year": yyyy,
                "cvc": cvv
            }
        )
        logging.info("Token created successfully.")
        
        customer = create_stripe_customer(token)
        logging.info("Stripe customer created successfully.")
        
        charge = create_stripe_charge(customer.id)
        logging.info("Stripe charge created successfully.")
        
        refund = refund_stripe_charge(charge.id)
        logging.info("Stripe refund created successfully.")
        
        cvc_check = charge.payment_method_details.card.cvc_check
        decline_code = charge.failure_code
        message = charge.outcome.seller_message
        return cvc_check, decline_code, message, bank, country, type
    except stripe.error.CardError as e:
        body = e.json_body
        err = body.get('error', {})
        message = err.get('message', 'Unknown error')
        logging.error(f"Stripe CardError: {message}")
        return None, None, message, bank, country, type
    except Exception as e:
        logging.error(f"Error occurred: {e}")
        return None, None, str(e), bank, country, type



# Example usage
cc = "5404044988233600"
mm = 8
yyyy = 2028
cvv = "251"
if check_stripe_secret_key(secret_key=secret) == True:
    cvc_check, decline_code, message, bank, country, type = charge_credit_card(cc, mm, yyyy, cvv)
    print(f"CVC check: {cvc_check}")
    print(f"Decline code: {decline_code}")
    print(f"Message: {message}")
    print(f"------BIN lookup result:------")
    print(f"Bank: {bank}")
    print(f"Country: {country}")
    print(f"Type: {type}")
    
    
    
 
  #########################MAKE SURE YOU READ THIS#########################
############################################################################
#0 MADE BY Ggre55, You have no right to distibute this tool or sell or resell it.
#1 Ggre55 is the only owner of this tool.
#2 This scripts are only for educational purpose. If you use this script for other purposes except 
#3 education we will not be responsible in such cases.
############################################################################



