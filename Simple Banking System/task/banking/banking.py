# Write your code here
import random
import sqlite3

conn = sqlite3.connect('card.s3db')

cur = conn.cursor()
cur.execute('create table if not exists card(id integer, number text, pin text, balance integer default 0)')
conn.commit()


class Card:
    IIN = "400000"

    def __init__(self):
        self.PIN = None
        self.CardNumber = None
        self.Balance = 0
        self.generate_pin()
        self.generate_card_number()

    def generate_pin(self):
        first = random.randint(0, 9)
        second = random.randint(0, 9)
        third = random.randint(0, 9)
        fourth = random.randint(0, 9)
        self.PIN = str(first) + str(second) + str(third) + str(fourth)

    def generate_card_number(self):
        account_number = str(random.randint(1, 999999999))
        initial_numbers = ""
        if len(str(account_number)) < 9:
            initial_numbers = "0" * (9 - len(str(account_number)))
        card_number = Card.IIN + initial_numbers + account_number
        card_digits1 = []
        digit_sum1 = 0
        for index1, digit1 in enumerate(card_number):
            if index1 % 2 == 0:
                card_digits1.append(int(digit1) * 2)
            else:
                card_digits1.append(int(digit1))
            if card_digits1[index1] > 9:
                card_digits1[index1] -= 9
            digit_sum1 += card_digits1[index1]
        checksum1 = (10 - (digit_sum1 % 10)) % 10
        self.CardNumber = card_number + str(checksum1)


# main program body
logged_in = False
all_cards = []
current_card = None
while True:
    # initial menu (Create account, Login, Exit)
    if not logged_in:
        option = int(input("1. Create an account\n2. Log into account. \n0. Exit\n"))
        # create an account
        if option == 1:
            new_card = Card()
            cur.execute('insert into card (number, pin, balance) values({}, {}, {})'.format(new_card.CardNumber, new_card.PIN, new_card.Balance))
            conn.commit()
            all_cards.append(new_card)
            print("Your card has been created\nYour card number:")
            print(new_card.CardNumber)
            print("Your card PIN:")
            print(new_card.PIN)
        # logging in
        elif option == 2:
            card = input("Enter your card number:\n")
            pin = input("Enter your PIN:\n")
            for obj in all_cards:
                if obj.CardNumber == card and obj.PIN == pin:
                    print("You have successfully logged in!")
                    logged_in = True
                    current_card = obj
                    break
            if not logged_in:
                print("Wrong card number or PIN!")
        elif option == 0:
            print("Bye!")
            break
    else:
        option = int(input("1. Balance\n2. Add income\n3. Do transfer\n4. Close account\n5. Log out\n0. Exit\n"))
        # checking balance
        if option == 1:
            cur.execute('select balance from card where number = {}'.format(current_card.CardNumber))
            balance = cur.fetchone()
            print("Balance:", balance)
        # adding income
        elif option == 2:
            income = int(input("Enter income: "))
            current_card.Balance += income
            cur.execute('update card set balance = {} where number = {}'.format(current_card.Balance, current_card.CardNumber))
            conn.commit()
            print("Income was added")
        # transferring to another account
        elif option == 3:
            print("Transfer")
            transfer_card = input("Enter card number:")
            if transfer_card == current_card.CardNumber:
                print("You can't transfer money to the same account!")
            else:
                card_digits = []
                digit_sum = 0
                for index, digit in enumerate(transfer_card[:-1]):
                    if index % 2 == 0:
                        card_digits.append(int(digit) * 2)
                    else:
                        card_digits.append(int(digit))
                    if card_digits[index] > 9:
                        card_digits[index] -= 9
                    digit_sum += card_digits[index]
                checksum = (10 - (digit_sum % 10)) % 10
                if checksum != int(transfer_card[-1:]):
                    print("Probably you made a mistake in the card number. Please try again!")
                else:
                    exists = False
                    for obj in all_cards:
                        if obj.CardNumber == transfer_card:
                            exists = True
                            amount = int(input("Enter how much money you want to transfer: "))
                            if amount > current_card.Balance:
                                print("Not enough money!")
                            else:
                                current_card.Balance -= amount
                                obj.Balance += amount
                                cur.execute('update card set balance = {} where number = {}'.format(current_card.Balance, current_card.CardNumber))
                                cur.execute('update card set balance = {} where number = {}'.format(obj.Balance, obj.CardNumber))
                                conn.commit()
                                print("Success")
                            break
                    if not exists:
                        print("Such a card does not exist.")
        # closing the account
        elif option == 4:
            cur.execute("delete from card where number = {}".format(current_card.CardNumber))
            conn.commit()
            logged_in = False
            print("The account has been closed!")
        elif option == 5:
            logged_in = False
            print("You have successfully logged out!")
        elif option == 0:
            print("Bye!")
            break
