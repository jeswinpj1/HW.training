 
inventory = {"beatroot":50.7,"carrot":65.3,"banana":40.6,"onion":30.2}
cart=["onion","banana","carrot","chocolate"]
print("inventory : ",type(inventory))
print("cart : ",type(cart))
print("one value price : ",type(inventory["banana"]))

print("checking items in cart")
total_price = 0
for item in  cart:
    if item in inventory:
        price = inventory[item]
        if price is not None:
            total_price += price
            print(f"Item: {item}, Price: {price}")
    else:
        print(f"Item: {item} is not available in inventory")

print("Total price of items in cart: ", total_price)

unique_cart = set(cart)
print(" Unique items in cart:", unique_cart) 

products = ("apple","dragonfruit","milk","burger")
print("tuple : " ,products,type(products))


print("adding an item with none")
inventory["chocolate"]=None
print("type of chocolate : ",type(inventory["chocolate"]))

discount = total_price>100
if discount:
    print("discont applied")
else:
    print("no discount applied")
print("discount applied : ",discount,type(discount))

