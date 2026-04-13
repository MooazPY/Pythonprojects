from menu import MENU

#Create a list containing drinks
menu_list = [i for i in MENU]


def report(water,milk,coffee,money):
    """Print the water, milk, coffee and money as a report"""
    print(f"Water: {water}ml\nMilk: {milk}ml\nCoffee: {coffee}g\nMoney: ${money}")


def coins_calculator(quar,dim,nick,penn):
    """Calculate the coins and return the sum of them"""
    sum = 0
    
    quarters = quar * 0.25
    dimes = dim * 0.10
    nickles = nick * 0.05
    pennies = penn * 0.01
    
    sum = quarters + dimes + nickles + pennies
    return sum


def drink(user_drink):
        """Take the coins from user and also check if money is enough or not"""
        print("Please insert coins.")
        quarters = int(input("How many quarters?: "))
        dimes = int(input("How many dimes?: "))
        nickles = int(input("How many nickles?: "))
        pennies = int(input("How many pennies?: "))
        
        coins = coins_calculator(quarters,dimes,nickles,pennies)
        
        
        if coins < MENU[user_drink]['cost']:
            print("Sorry that's not enough money. Money refunded.")
            return 0
        else:
            print(f"Here is ${round(coins,2)} in change.\nHere is your {user_drink} ☕ Enjoy!")
            return 1


def run_machine():
    water = 300
    milk = 200
    coffee = 100
    money = 0
    while True:
        
            user_order = input("What would you like? (espresso/latte/cappuccino): ")
            
            if user_order.lower() == "report":
                report(water,milk,coffee,money) 
            elif user_order.lower() == "off":
                return
            elif user_order in menu_list:
                #water
                if MENU[user_order]['ingredients']['water'] > water:
                    print("Sorry there is not enough water.")
                #milk
                elif user_order.lower() != "espresso" and MENU[user_order]['ingredients']['milk'] > milk:
                        print("Sorry there is not enough milk.")
                #coffee
                elif MENU[user_order]['ingredients']['coffee'] > coffee:
                        print("Sorry there is not enough coffee.")
                else:
                    if drink(user_order) == 1:
                        water -= MENU[user_order]['ingredients']['water']
                        if user_order.lower()!= "espresso":
                            milk -= MENU[user_order]['ingredients']['milk']
                        coffee -= MENU[user_order]['ingredients']['coffee']
                        money += MENU[user_order]['cost']
            else:
                print(f"Sorry {user_order} is not available.")

run_machine()