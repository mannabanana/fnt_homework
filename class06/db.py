#!/usr/bin/python
import psycopg2
import os
from config import config

def create_tables():
    """ create tables in the PostgreSQL database"""
    
    commands = ("""
        CREATE TABLE customers (
            cust_id SERIAL PRIMARY KEY,
            first_nm VARCHAR(100) NOT NULL,
            last_nm VARCHAR(100) NOT NULL
        );
	""",
	"""
	CREATE TABLE goods (
	    good_id SERIAL PRIMARY KEY,
    	    vendor VARCHAR(100) NOT NULL,
    	    name VARCHAR(100) NOT NULL,
    	    description VARCHAR(300)
    	);
    	""",
        """
        CREATE TABLE orders (
            order_id SERIAL PRIMARY KEY,
            cust_id SERIAL,
            order_dttm TIMESTAMP,
            status VARCHAR(20) NOT NULL,
            FOREIGN KEY (cust_id)
                REFERENCES customers (cust_id)
                ON UPDATE CASCADE ON DELETE CASCADE
        );
        """,
        """
        CREATE TABLE order_items (
            order_item_id SERIAL PRIMARY KEY,
            order_id SERIAL,
            good_id SERIAL,
            quantity INTEGER NOT NULL,
            FOREIGN KEY (order_id)
                REFERENCES orders (order_id)
                ON UPDATE CASCADE ON DELETE CASCADE,
            FOREIGN KEY (good_id)
    	        REFERENCES goods (good_id)
                ON UPDATE CASCADE ON DELETE CASCADE
        );
        """)

    for command in commands:
	cur.execute(command)
    conn.commit()

def insert_good(order_id, good_id):
    """ insert a new good into the order_items table """
    quantity = 1
    sql = """INSERT INTO order_items (order_id,good_id,quantity)
	     VALUES(%s,%s,%s) RETURNING order_item_id;"""
    order_item_id = None
    # execute the INSERT statement
    cur.execute(sql, (order_id,good_id,quantity,))
    # get the generated id back
    order_item_id = cur.fetchone()[0]
    # commit the changes to the database
    conn.commit()

def delete_good(order_id, good_id):
    """ delete good by good id """
    item_id = order_search(order_id, good_id)
    cur.execute("DELETE FROM order_items WHERE order_item_id = %s", (item_id,))
    conn.commit()

def update_good(quantity, order_id, good_id):
    """ update quantity based on the good id """
    item_id = order_search(order_id, good_id)
    sql = """ UPDATE order_items
        	SET quantity = %s
                WHERE order_item_id = %s"""
    cur.execute(sql, (quantity,item_id,))
    conn.commit()

def order_search(order_id, good_id):
    cur.execute("SELECT * FROM order_items WHERE good_id = %s", (good_id,))
    rows = cur.fetchall()
    for row in rows:
	if int(row[1]) == order_id:
    	    item_id = row[0]
	    return item_id

def copy_to_file():
    cur.execute("COPY (SELECT customers.first_nm, customers.last_nm, goods.name, goods.vendor FROM order_items JOIN goods ON order_items.good_id = goods.good_id JOIN orders ON order_items.order_id = orders.order_id JOIN customers ON customers.cust_id = orders.cust_id) TO '/home/postgres/tables_shop_data.csv' WITH CSV HEADER;")
    print("Info has printed to /home/postgres/tables_shop_data.csv")

def check_order_id(order_id):
    cur.execute("SELECT order_id FROM orders WHERE order_id = %s", (order_id,))
    if cur.rowcount > 0:
	return True
    else:
        return False

def check_good_id(order_id,good_id):
    cur.execute("SELECT order_id,good_id FROM order_items WHERE good_id = %s", (good_id,))
    rows = cur.fetchall()
    order_check = False
    for row in rows:
	if int(row[0]) == order_id:
	    return True
    return False



if __name__ == '__main__':

    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        # read connection parameters
	params = config()
        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)
        # create a cursor
        cur = conn.cursor()
        #create table one by one if db is empty
        cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema NOT IN ('information_schema','pg_catalog')")
        if cur.rowcount == 0:
    	    create_tables()
    	    print ('Tables was created')
    	else:
    	    print 'The number of exist tables: ', cur.rowcount
    	print("====================================\n1. Insert good in order\n2. Delete good from order\n3. Update quantity of good in order\n4. Export database to txt file\n5. Exit\n====================================")
	options = 0
	while options != 5:
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
		copy_to_file()
	    if options == 5:
		print("Exit")
        # close the communication with the PostgreSQL
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
	print(error)
    finally:
	if conn is not None:
    	    conn.close()
            print('Database connection closed.')