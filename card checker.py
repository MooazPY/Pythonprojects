import copy
import sys
def check_card(cardnumber):

    mb = copy.copy(cardnumber)
    sum = 0
    multi2 = 0
    checker1 = str(cardnumber)
    checker2 = len(checker1)
    while cardnumber != 0:
        lastdigit = cardnumber % 10 #GET LAST DIGIT ALONE
        #sum digit
        sum = sum + lastdigit
        cardnumber = (cardnumber - lastdigit) // 10 #TO DELETE LAST DIGIT
        lastdigit = cardnumber % 10    
        #multiply digits by 2
        count = lastdigit * 2
        if count >= 10:
            while count != 0:
                lastdigit = count % 10
                multi2 += lastdigit
                count = (count - lastdigit) // 10
        else:
            multi2 += (lastdigit * 2)
        cardnumber = (cardnumber - lastdigit) // 10

    #CHECK IF IT COULD BE CARD OR NOT
    check = multi2 + sum
    lastdigit = check % 10
    if lastdigit == 0:
        if checker2 == 15: #if the len of the card == 15
            print("Your Card Type Is AMEX")
            sys.exit()
        elif checker2 == 13:
            print("Your Card Type Is VISA")
            sys.exit()
        elif checker2 == 16:
            while mb != 0:
                lastdigit = mb % 10  # GET LAST DIGIT ALONE
                mb = (mb - lastdigit) // 10  # TO DELETE LAST DIGIT
                checker1 = str(mb)
                checker2 = len(checker1)
                while checker2 == 2:
                    if mb >= 51 or mb <=55:
                        print("Your Card Type Is MASTERCARD")
                        sys.exit()
                    elif mb//10 == 4:
                        print("Your Card Type Is VISA")
                        sys.exit()

    else:
        print("INVALID")


cardnumber= int(input("Please Enter Your Card Number : "))
check_card(cardnumber)