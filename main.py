from flask import Flask, session, render_template, redirect, url_for, request, flash
import sqlite3
app = Flask('app')
app.secret_key = "lower"
#app.debug = 1


@app.route('/', methods = ['POST', 'GET']) 
def home():
  with get_db_connection() as connection:
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute("SELECT category FROM categories") 
    catagories = cursor.fetchall()
    selected_category = request.args.get('category')
    print(type(selected_category))
    if selected_category != "None" and type(selected_category) == str:
      cursor.execute("SELECT * FROM products WHERE category = ?", (selected_category,))
      print("Filtering")
    else :
      print("Selecting everything")
      cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    
    #print(products)
  '''
  cursor.close()
  connection.commit()
  connection.close()
  '''
  return render_template("home.html", products=products, catagories=catagories, selected_category=selected_category) 


@app.route('/login', methods=['GET','POST'])
def login() :
  with get_db_connection() as connection:
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    if request.method == 'POST':
      session['user'] = request.form["username"]
      session['pw'] = request.form["password"]
      
      cursor.execute("SELECT * FROM users WHERE username = ?", (session['user'],))
      values=cursor.fetchone()
      print(values)
      '''
      cursor.close()
      connection.commit()
      connection.close()
      '''
      if values is None:
        flash("Username or password does not exist")
        return render_template("login.html")
      elif session['pw'] == values['password'] :
        session['cart'] = list()
        session['name'] = values['name']
        session['loggedIn'] = True
        #print("Session after login:", session)
        return redirect('/')
          
  return render_template("login.html")



@app.route('/CreateAccount', methods=['GET','POST'])
def createAccount() :
  with get_db_connection() as connection:
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    if request.method == 'POST' :
      session['user'] = request.form["username"]
      session['pw'] = request.form["password"]
      session['name'] = request.form["name"]
      if session['user'] == "" or session['pw'] == "" or session['name'] == "" : 
        flash("Please fill out every feild")
        return render_template('createAccount.html')
      elif len(session['pw']) < 8 :
        flash("Password must be longer than 8 characters")
      else :
        cursor.execute("SELECT * FROM users WHERE username = ?",  (session['user'],))
        exists = cursor.fetchone()
        if not exists :
          print("Adding a new user")
          cursor.execute("INSERT INTO users VALUES (?, ?, ?)",  (session['user'], session['pw'], session['name'],))
          connection.commit()
          '''
          cursor.close()
          connection.commit()
          connection.close()
          '''
          return redirect('/login')
        else :
          flash("Username already exists")
          return redirect('CreateAccount')
    '''
    cursor.close()
    connection.commit()
    connection.close()
    '''
  return render_template('createAccount.html', failed = False)


@app.route('/Cart', methods = ['GET', 'POST'])
def loadCart() :
  with get_db_connection() as connection:
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    if request.method == 'POST' :
      print(session['cart'])
      prod_id = request.form.get('product_id')
      if prod_id in session['cart']:
        session['cart'].remove(prod_id)
      session.modified = True
      print(session['cart'])

    total = 0
    currentCart = list()
    for item in session.get('cart', []):
      cursor.execute("SELECT * FROM products WHERE prodID = ?", (int(item),))
      value = cursor.fetchone()
      if value:
        currentCart.append(value)
        total += value['price'] 
        
    print(total)
    #print(currentCart)
    '''
    cursor.close()
    connection.commit()
    connection.close()
    '''
  return render_template('cart.html', cart = currentCart, total = total)


@app.route('/orders') 
def loadOrders():
    with get_db_connection() as connection:
      connection.row_factory = sqlite3.Row
      cursor = connection.cursor()
      
      display = []

      cursor.execute("SELECT orderId, products FROM orders WHERE username = ?", (session['user'], ))
      orders = cursor.fetchall()

      

      for order in orders:
        total = 0
        product_ids = order['products'].split(',')
        placeholders = ','.join(['?'] * len(product_ids)) 
        cursor.execute(f"SELECT name, price FROM products WHERE prodId IN ({placeholders})", product_ids)
        products = cursor.fetchall()
        for prod in products :
          total += prod['price'] 
        product_details = ', '.join([f"{prod['name']} (${prod['price']:.2f})" for prod in products])
        order_display = f"Order ID: {order['orderId']} - Products: {product_details}" + " Total Price = $" + str(total)
        display.append(order_display)
      '''
      cursor.close()
      connection.commit()
      connection.close()
      '''
      return render_template("orders.html", orders=display)
    
  


@app.route('/checkout', methods=['POST'])
def checkout():
  with get_db_connection() as connection:
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cart_counts = {}
    prodIds = ""
    for item in session.get('cart', []):
      cart_counts[item] = cart_counts.get(item, 0) + 1
      prodIds += str(item) + ", "
    prodIds = prodIds[:len(prodIds) - 2]
    for prod_id, count in cart_counts.items():
      cursor.execute("SELECT * FROM products WHERE prodID = ?", (int(prod_id),))
      product = cursor.fetchone()

      if product is None or product['quantity'] < count:
        flash(f"Not enough stock for {product['name']}.")
        return redirect('/Cart')

    for prod_id, count in cart_counts.items():
      cursor.execute("UPDATE products SET quantity = quantity - ? WHERE prodID = ?", (count, int(prod_id)))
      connection.commit()
      
    print(prodIds)
    #cursor.execute("INSERT INTO orders VALUES (SELECT Max(orderId) FROM orders + 1), ?, ?)", (session['user'], prodIds), )
    cursor.execute("INSERT INTO orders (username, products) VALUES (?, ?)", (session['user'], prodIds), )
    connection.commit()
    
    session['cart'] = []
    session.modified = True
    flash("Checkout successful!")

    '''
    cursor.close()
    connection.commit()
    connection.close()
    '''
  return redirect('/Cart')
 
@app.route('/addToCart', methods=['POST'])
def addToCart():
  if request.method == 'POST':
    if session.get('loggedIn') :
      prod_id = request.form.get('product_id')
      quantity = request.form.get('quantity', type=int)

      if not prod_id or not quantity:
        flash("Invalid product selection.")
        return redirect('/')

      with get_db_connection() as connection:
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()

        # Check if product exists and has enough stock
        cursor.execute("SELECT * FROM products WHERE prodID = ?", (prod_id,))
        product = cursor.fetchone()

        if not product:
          flash("Product not found.")
          return redirect('/')

        if quantity > product['quantity']:
          flash(f"Only {product['quantity']} items in stock!")
          return redirect('/')

        # Add to cart
        for _ in range(quantity):
            session['cart'].append(prod_id)
        session.modified = True
        '''
        cursor.close()
        connection.commit()
        connection.close()
        '''
        flash(f"Added {quantity} x {product['name']} to cart!")
    else :
      flash("You must be logged in to add items to the cart")
      return redirect('/login')
  if request.args.get('category') :
    return redirect('/?category=' + request.args.get('category'))
  else :
    return redirect('/')


@app.route('/search', methods = ['POST', 'GET'])
def search() :
  if request.method == 'POST' :
    searchterm = request.form.get('search')
    #print("Searching for " + str(searchterm))
    with get_db_connection() as connection:
      connection.row_factory = sqlite3.Row
      cursor = connection.cursor()

      cursor.execute("SELECT category FROM categories") 
      catagories = cursor.fetchall()

      selected_category = request.args.get('category')

      cursor.execute("SELECT * FROM products WHERE name LIKE ?", (f"%{searchterm}%", ))  
      products = cursor.fetchall()
      if len(products) == 0:
        flash("No results for that search")
    '''
    cursor.close()
    connection.commit()
    connection.close()
    '''
    return render_template("home.html", products=products, catagories=catagories, selected_category=selected_category) 


@app.route('/logout') 
def logout() :
  session.pop('user', None)
  session.pop('pw', None)
  session.pop('name', None)
  session.pop('cart', None)
  session.pop('loggedIn', None)
  session.clear()
  return redirect('/')

def get_db_connection():
  return sqlite3.connect("database.db", check_same_thread=False)


app.run(host='0.0.0.0', port=8080)
