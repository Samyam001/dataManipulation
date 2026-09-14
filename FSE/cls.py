class Dog:

    def __init__(self, name, age):
        self.name = name
        self.age = age


dog1 = Dog("SUSU", 23)
dog2 = Dog("DODO", 34)

# print(dog1.name,dog1.age)
# print(dog2.name,dog2.age)


class account:
    def __init__(self, name, balance):
        self.name = name
        self.balance = balance
        self.charge = 0

    def wirhdrawl(self, amount):
        if amount+self.charge > self.balance:
            print("Insufficent Balance")
        else:
            self.balance-=(amount+self.charge)
            print("Current Balance: ",{self.balance})



account1 = account("Samyam", 10000)
account2=account("Er",2999)

account1.charge=100

print(f"{account1.name}, {account1.wirhdrawl(300)}")
print(f"Name: {account2.name} Balance: {account2.balance}")


