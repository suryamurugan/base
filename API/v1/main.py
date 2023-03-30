import random
import secrets

def get_check_digit(card_number):
    digits = [int(d) for d in card_number]
    odd_sum = sum(digits[-1::-2])
    even_sum = sum([sum(divmod(2 * d, 10)) for d in digits[-2::-2]])
    total_sum = odd_sum + even_sum
    return (10 - total_sum % 10) % 10



def generateCardNumber():
    issuer_id = "4" # Assume it's a Visa card (starts with 4)
    card_number = issuer_id + "".join([str(secrets.randbelow(10)) for _ in range(14)]) # Generate random 14-digit number
    check_digit = str(get_check_digit(card_number)) # Compute check digit using Luhn algorithm
    return card_number + check_digit


