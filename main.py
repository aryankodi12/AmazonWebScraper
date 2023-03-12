# Sure! Here's a more detailed plan for the project with your requested changes:

# Backend:

# Use Python as the backend language.
# Use Flask to create a RESTful API to handle requests from the frontend.
# Use Beautiful Soup to extract product information from the Amazon website.
# Use SQLAlchemy to store the extracted data in a database.
# Use APScheduler to schedule web scraping tasks.
# Frontend:

# Use React as the frontend library.
# Use Axios to send requests to the backend API.
# Use Bootstrap or Material UI to style the frontend components.
# Allow users to input the URL of the product they want to track.
# Display a list of tracked products and their current prices.
# Allow users to set a target price for each product and receive email alerts when the price drops below the target.
# Here's a basic outline of the steps involved:

# Set up the backend:
# Install necessary Python libraries: Flask, Beautiful Soup, SQLAlchemy, APScheduler.
# Create a Flask app and define routes to handle requests from the frontend.
# Use Beautiful Soup to extract product information from the Amazon website.
# Use SQLAlchemy to store the extracted data in a database.
# Use APScheduler to schedule web scraping tasks.
# Set up the frontend:
# Install necessary libraries: React, Axios, Bootstrap or Material UI.
# Create a React app and define components to handle user input and display product information.
# Use Axios to send requests to the backend API and retrieve data.
# Use Bootstrap or Material UI to style the frontend components.
# Implement the core functionality:
# Allow users to input the URL of the product they want to track.
# Extract the current price of the product and store it in the database.
# Display a list of tracked products and their current prices.
# Allow users to set a target price for each product and receive email alerts when the price drops below the target.
# Deploy the application:
# Deploy the backend and frontend to a hosting service like Heroku or AWS.
# Configure the email notification system using a service like SendGrid or Amazon SES.


from flask import Flask, request, jsonify
from flask_cors import CORS
from bs4 import BeautifulSoup
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import sessionmaker
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from sqlalchemy import DateTime
from sqlalchemy.ext.declarative import declarative_base

import requests
import os

app = Flask(__name__)
CORS(app)

# Set up database connection
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///products.db')
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

# Set up email notification system
# You can use a service like SendGrid or Amazon SES for this
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = os.environ.get('EMAIL_PORT', 587)
EMAIL_USER = os.environ.get('EMAIL_USER', 'youremail@gmail.com')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD', 'yourpassword')
EMAIL_SENDER = os.environ.get('EMAIL_SENDER', 'youremail@gmail.com')
EMAIL_RECIPIENT = os.environ.get('EMAIL_RECIPIENT', 'recipient@example.com')

def send_email(product_name, current_price):
    import smtplib
    server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
    server.starttls()
    server.login(EMAIL_USER, EMAIL_PASSWORD)
    msg = f"The price of {product_name} has dropped to {current_price}."
    server.sendmail(EMAIL_SENDER, EMAIL_RECIPIENT, msg)
    server.quit()

Base = declarative_base()

class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True)
    product_id = Column(String(255), unique=True, nullable=False)
    title = Column(String(255), nullable=False)
    current_price = Column(Float, nullable=False)
    target_price = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, product_id, title, current_price, target_price=None):
        self.product_id = product_id
        self.title = title
        self.current_price = current_price
        self.target_price = target_price

    def __repr__(self):
        return f"<Product(id={self.id}, product_id='{self.product_id}', title='{self.title}', \
            current_price={self.current_price}, target_price={self.target_price})>"

    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'title': self.title,
            'current_price': self.current_price,
            'target_price': self.target_price
        }
    def is_below_target_price(self):
        return self.target_price is not None and self.current_price <= self.target_price

Base.metadata.create_all(engine)

def scrape_product(product_id):
    url = f"https://www.amazon.com/dp/{product_id}"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    title = soup.find(id="productTitle").get_text().strip()
    price = soup.find(id="priceblock_ourprice").get_text().strip()
    price = float(price.replace('$', '').replace(',', ''))
    return title, price

@app.route('/api/products', methods=['GET', 'POST'])
def products():
    if request.method == 'GET':
        products = session.query(Product).all()
        return jsonify([product.to_dict() for product in products])
    elif request.method == 'POST':
        data = request.json
        product_id = data['product_id']
        target_price = data['target_price']
        title, current_price = scrape_product(product_id)
        product = Product(product_id=product_id, title=title, current_price=current_price, target_price=target_price)
        session.add(product)
        session.commit()
        return product.to_dict()

@app.route('/api/products/<int:product_id>', methods=['GET', 'PUT', 'DELETE'])
def product(product_id):
    product = session.query(Product).filter_by(id=product_id).first()
    if request.method == 'GET':
        return product.to_dict()
    elif request.method == 'PUT':
        data = request.json
        if 'target_price' in data:
            product.target_price = data['target_price']
            session.commit()
        return product.to_dict()
    elif request.method == 'DELETE':
        session.delete(product)
        session.commit()
        return '', 204


def check_prices():
    products = session.query(Product).all()
    for product in products:
        title, current_price = scrape_product(product.product_id)
        product.current_price = current_price
        session.commit()
        if product.is_below_target_price():
            send_email(product.title, product.current_price)

scheduler = BackgroundScheduler()
scheduler.add_job(check_prices, 'interval', hours=1)
scheduler.start()


@app.route('/api/check-prices', methods=['POST'])
def check_prices_route():
    check_prices()
    return '', 204
