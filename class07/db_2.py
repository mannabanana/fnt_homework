#!/usr/bin/python36

from peewee import *


db = PostgresqlDatabase('shop_data', user='postgres', password='postgres', host='localhost')
class customers(Model):
    cust_id = AutoField(primary_key=True)
    first_nm = CharField(100)
    last_nm = CharField(100)

    class Meta:
        database = db

class orders(Model):
    order_id = AutoField(primary_key=True)
    cust_id = ForeignKeyField(customers, related_name ='cust_id')
    order_dttm = DateTimeField()
    status = CharField(20)

    class Meta:
        database = db

class goods(Model):
    good_id = AutoField(primary_key=True)
    vendor = CharField(100)
    name = CharField(100)
    description = CharField(300)

    class Meta:
        database = db

class order_items(Model):
    order_item_id = AutoField(primary_key=True)
    order_id = ForeignKeyField(orders, related_name ='order_id')
    good_id = ForeignKeyField(goods, related_name ='good_id')
    quantity = IntegerField()

    class Meta:
        database = db

def create_tables():

    customers.create_table()
    orders.create_table()
    goods.create_table()
    order_items.create_table()

def insert_good(order_id, good_id):
    """ insert a new good into the order_items table """
    order_items.insert(order_id = order_id, good_id = good_id, quantity = 1).execute()
    print "Good id",good_id,"was inserted in order",order_id

def delete_good(order_id, good_id):
    """ delete good by good id """
    order_items.delete().where((order_items.order_id == order_id) & (order_items.good_id == good_id)).execute()
    print "Good was deleted"

def update_good(quantity, order_id, good_id):
    """ update quantity based on the good id """
    order_items.update(quantity = quantity).where((order_items.order_id == order_id) & (order_items.good_id == good_id)).execute()


def check_order_id(order_id):
    for order in orders.select():
	if order.order_id == order_id:
	    return True
    return False

def check_good_id(order_id,good_id):
    try:
	items = order_items.select().where((order_items.order_id == order_id) & (order_items.good_id == good_id)).get()
        return True
    except (Exception, DoesNotExist) as error:
	return False

""" Connect to the PostgreSQL database server """

if len(db.get_tables()) == 0:
    create_tables()
    print ('Tables was created')
else:
    print 'The number of exist tables:',len(db.get_tables())
    print("====================================\n1. Insert good in order\n2. Delete good from order\n3. Update quantity of good in order\n4. Exit\n====================================")
    options = 0
    while options !=4:
	options = int(input("Choose options: "))
	if options == 1:
	    order_id = int(input("Order ID: "))
	    check = check_order_id(order_id)
	    if check == False:
		print "Order number", order_id, "doesn't exist"
		continue
	    good_id = int(input("Good ID: "))
	    if check_good_id(order_id,good_id) == True:
	        print "Good exist in", order_id, "order"
	    else:
		insert_good(order_id, good_id)
	if options == 2:
	    order_id = int(input("Order ID: "))
	    check = check_order_id(order_id)
	    if check == False:
		print "Order number", order_id, "doesn't exist"
		continue
	    good_id = int(input("Good ID: "))
	    if check_good_id(order_id,good_id) == False:
		print "Good doesn't exist in", order_id, "order"
	    else:
	        delete_good(order_id, good_id)
	if options == 3:
	    order_id = int(input("Order ID: "))
	    check = check_order_id(order_id)
	    if check == False:
	        print "Order number", order_id, "doesn't exist"
	    good_id = int(input("Good ID: "))
	    if check_good_id(order_id,good_id) == False:
	        print "Good doesn't exist in", order_id, "order"
	    else:
	        quantity = int(input("New quantity of good:"))
	        update_good(quantity,order_id,good_id)
	if options == 4:
	    print("Exit")