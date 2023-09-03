from flask import Flask, render_template, request, redirect, flash, session
from pymongo.mongo_client import MongoClient
from bson.objectid import ObjectId
import random
from passlib.hash import sha256_crypt
app = Flask(__name__)
app.config['SECRET_KEY'] = 'safe1222345semicodewq'

uri = "mongodb+srv://SemiAkindipeCluster:Semicoding2011@cluster0.wqfphzp.mongodb.net/OneStopShop?retryWrites=true&w=majority"

# Create a new client and connect to the server
client = MongoClient(uri)
db=client.OneStopShop


@app.route('/',methods=['POST','GET'])
def index():
    if request.method=='GET':
        if 'email' in session:
            logged = True
            shopper = db.Shoppers.find_one({'email':session['email']})
            if type(shopper) is dict:
                total = 0
                for r in shopper['cart']:
                    total = total + int(r[1])
                cart_count = total
            else:
                cart_count = 0
                logged = False

        else:
            cart_count = 0
            logged = False
        cursor=db.Shop.find()
        stores=[]
        products=[]
        for r in cursor:
            stores.append(r)
        cursor=db.Products.find()
        for r in cursor:
            products.append(r)
        print(products,stores,cart_count)
        return render_template("index.html",stores = stores, products = products, cart_count = cart_count, logged = logged)
    if request.method=='POST':
        print(request.form.keys())
        if "Signup" in request.form.keys():
            if request.form['password']!='' and request.form['email']!='' and request.form['store']!='' and request.form['owner']!='' and request.form['contact']!='':
                logins = db.Shop.find()
                cancreate=True
                for r in logins:
                    if request.form['email']==r['email']:
                        cancreate=False
                if cancreate==True:
                    document={}
                    document['password'] = sha256_crypt.hash(request.form['password'])
                    document['email'] = request.form['email']
                    document['contact'] = request.form['contact']
                    document['store'] = request.form['store']
                    document['extra'] = request.form['extra']
                    document['owner'] = request.form['owner']
                    db.Shop.insert_one(document)
                    flash('Account created.')
                    session.clear()
                    session['email']=request.form['email']
                    return redirect('/')
                else:
                    flash('Email already in use.')
                    return redirect('/')
            else:
                flash('Please complete all values.')
                return redirect('/')
        elif "Login" in request.form.keys():
            if request.form['password']!='':
                logins = db.Shop.find()
                email=False
                password=False

                for r in logins:
                    if r['email']==request.form['email']:
                        email=True
                    if sha256_crypt.verify(request.form['password'],r['password']):
                        password=True
                    print(r['email'])
                    print(r['password'])
                if email and password:
                    session.clear()
                    session['email']=request.form['email']
                    flash('Logged in')
                    return redirect('/home')
                else:
                    flash('Incorrect Email or Password')
                    return redirect('/')
        elif "AddCart" in request.form.keys():
            if 'email' in session:
                keys = list(request.form.keys())
                db.Shoppers.update_many({'email':session['email']},{'$push':{'cart':[keys[0],request.form[keys[0]]]}})
                sub = int(request.form[keys[0]]) - (int(request.form[keys[0]])*2)
                db.Products.update_one({'name':keys[0]},{'$inc':{'stock':sub}})
                flash('Cart updated.')
                return redirect('/')
            else:
                flash('You must sign in to shop')
                return redirect('/')
        elif "Signup_Shopper" in request.form.keys():
            if request.form['password']!='' and request.form['email']!='' and request.form['first']!='' and request.form['last']!='':
                cursor = db.Shoppers.find()
                cancreate=True
                for r in cursor:
                    if request.form['email']==r['email']:
                        cancreate=False
                if cancreate==True:
                    document = {}
                    document['first'] = request.form['first']
                    document['last'] = request.form['last']
                    document['email'] = request.form['email']
                    document['password'] = sha256_crypt.hash(request.form['password'])
                    document['cart'] = []
                    db.Shoppers.insert_one(document)
                    session.clear()
                    session['email'] = request.form['email']
                    return redirect('/')
                else:
                    flash('Email already in use.')
                    return redirect('/')
            else:
                flash('Please complete all values.')
                return redirect('/')
        elif "Login_Shopper" in request.form.keys():
            if request.form['password']!='':
                logins = db.Shoppers.find()
                email=False
                password=False

                for r in logins:
                    if r['email']==request.form['email']:
                        email=True
                    if sha256_crypt.verify(request.form['password'],r['password']):
                        password=True
                    print(r['email'])
                    print(r['password'])
                if email and password:
                    session.clear()
                    session['email']=request.form['email']
                    flash('Logged in')
                    return redirect('/')
                else:
                    flash('Incorrect Email or Password')
                    return redirect('/')
    return render_template('index.html')

@app.route('/home',methods=['GET','POST'])
def home():
    if request.method=='GET':
        if 'email' not in session:
            flash('You must sign in.')
            return redirect('/')
        logins=db.Shop.find_one({'email':session['email']})
        cursor=db.Products.find({'email':session['email']})
        print(logins['store'])
        people=logins['store']
        products=[]
        for r in cursor:
            products.append(r)
        # for r in logins:
        #     people.append(r)
        return render_template("home.html", people = people, products = products)
    if request.method=='POST':
        print(request.form)
        if "Add" in request.form.keys():
            if request.form['name']!='' and request.form['description']!='' and request.form['price']!='' and request.form['stock']!='' and request.form['image']!='':
                document={}
                document['name'] = request.form['name']
                document['description'] = request.form['description']
                document['price'] = request.form['price']
                document['stock'] = int(request.form['stock'])
                document['image'] = request.form['image']
                document['email'] = session['email']
                document['max'] = int(request.form['max'])
                db.Products.insert_one(document)
                flash('Product added')
                return redirect('/home')
        elif 'StockUp' in request.form.keys():
            key=list(request.form.keys())
            print(request.form)
            db.Products.update_one({'name':key[0]},{'$set':{'stock':int(request.form[key[0]])}})
            flash('Stock updated')
            return redirect('/home')
        elif 'DeleteProduct' in request.form.keys():
            cursor = db.Products.find({'email':session['email']})
            names=[]
            for r in cursor:
                names.append(r['name'])
            key=list(request.form.keys())
            if request.form['name'] in names:
                db.Products.delete_one({'name':request.form['name']})
                flash('Product Deleted')
                return redirect('/home')
            else:
                flash('Product name does not exist')
                return redirect('/home')

@app.route('/store/<email>',methods=['GET','POST'])
def shop(email):
    if request.method=='GET':
        if 'email' in session:
            shopper = db.Shoppers.find_one({'email':session['email']})
            total = 0
            for r in shopper['cart']:
                total = total + int(r[1])
            cart_count = total
            products = list(db.Products.find({'email':email}))
            return render_template('shop.html', products = products, logged = True, cart_count = cart_count)
        else:
            flash("You must sign in to view stores.")
            return redirect('/')
    if request.method=='POST':
        if 'email' in session:
            keys = list(request.form.keys())
            db.Shoppers.update_many({'email':session['email']},{'$push':{'cart':[keys[0],request.form[keys[0]]]}})
            sub = int(request.form[keys[0]]) - (int(request.form[keys[0]])*2)
            db.Products.update_one({'name':keys[0]},{'$inc':{'stock':sub}})
            shopper = db.Shoppers.find_one({'email':session['email']})
            total = 0
            for r in shopper['cart']:
                total = total + int(r[1])
            cart_count = total
            products = list(db.Products.find({'email':email}))
            return render_template('shop.html', products = products, logged = True, cart_count = cart_count)
        else:
            flash('You must sign in to shop')
@app.route('/logout',methods=['GET','POST'])
def logout():
    session.clear()
    flash('Logout succesful')
    return redirect('/')
@app.route('/cart',methods=['GET','POST'])
def cart():
    if request.method=='GET':
        shopper = db.Shoppers.find_one({'email':session['email']})
        total = 0
        cart = []
        bill = 0

        for r in shopper['cart']:
            product = db.Products.find_one({'name':r[0]})
            price = product['price']
            ptotal = int(r[1])*float(price)
            cart.append((r,int(total+1),float(price),ptotal))
            total = total + int(r[1])
            bill = bill+ptotal
        cart_count = total
        return render_template('cart.html', cart = cart, total = total, bill = bill)

@app.route('/checkout',methods=['GET','POST'])
def checkout():
    products = db.Products.find()
    names = []
    for r in products:
        names.append(r['name'])
    db.Shoppers.update_one({'email':session['email']},{'$pull':{'cart': {'$in' : names}}})
    flash('Thank You!')
    return redirect('/')
    
    
if __name__ == '__main__':
    app.run(debug=True,port=8000)
    session.clear()