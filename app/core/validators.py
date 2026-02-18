"""
Separate file created for validators
"""


def validate_nip(nip: str) -> bool:
    if not nip or len(nip) != 10 or not nip.isdigit():
        raise ValueError("NIP must be 10 digits")

    weights = [6, 5, 7, 2, 3, 4, 5, 6, 7]
    counted = [int(nip[i]) * int(weights[i]) for i in range(len(weights))]
    summed = sum(counted)

    control_digit = summed % 11

    if control_digit == 10 or control_digit != int(nip[-1]):
        raise ValueError("Entered NIP is not valid number")

    return nip


def validate_regon(regon: str) -> bool:
    if not regon or len(regon) != 9 or not regon.isdigit():
        raise ValueError("REGON must be 9 digits")

    weights = [8, 9, 2, 3, 4, 5, 6, 7]
    counted = [int(regon[i]) * int(weights[i]) for i in range(len(weights))]

    summed = sum(counted)
    control_digit = summed % 11

    if control_digit == 10:
        control_digit = 0

    if control_digit != int(regon[-1]):
        raise ValueError("REGON is not valid")

    return regon
