def recursion(n):
    try:
        if n==1 or n==0:
            return 1
        else:
            return n*recursion(n-1)
    except ValueError:
        print("Invalid")
        return 0


num=int(input(f"Enter Number: "))

print(recursion(num))
