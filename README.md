MultiShop — Django E-Commerce Platform

MultiShop is a Django-based e-commerce platform developed as an example of an online clothing store. It provides shopping functionality, product discovery, vendor features, discount management, and online payments through Stripe.

Features

User Authentication
- User registration and login
- Sign-up and sign-out functionality
- User access management

Product and Vendor Management
- Vendor functionality
- Product detail pages
- Search bars for finding products
- Product sorting and filtering
- Pagination for product listings
- Product likes and ratings
- Category and subcategory organization

Shopping Cart
- Add products to the shopping cart
- Calculate prices based on product quantities
- Apply discounted prices when a discount is available
- Use regular prices when no discount applies

Discounts and Coupons
- Product discount management
- Coupon functionality to reduce the total price

Online Payments
- Stripe payment integration
- Support for online payment processing

Administration
- Superuser and staff status management
- Administrative management through Django Admin

Contact
- Contact functionality for the store

Technologies Used

- Python
- Django
- HTML
- CSS
- JavaScript
- Stripe
- python-dotenv

Environment Configuration

Sensitive configuration values are stored in environment variables and loaded using `python-dotenv`.

Create a `.env` file in the project root:

```env
SECRET_KEY=your_django_secret_key
DEBUG=True
STRIPE_SECRET_KEY=your_stripe_secret_key
STRIPE_PUBLISHABLE_KEY=your_stripe_publishable_key
```

Use the variable names expected by the project's settings and Stripe integration.

Installation and Setup

1. Clone the repository.
2. Create and activate a virtual environment.
3. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Create the `.env` file and configure the required environment variables.
5. Apply database migrations:

   ```bash
   python manage.py migrate
   ```

6. Create an administrator account:

   ```bash
   python manage.py createsuperuser
   ```

7. Start the development server:

   ```bash
   python manage.py runserver
   ```

8. Open the local development URL in your browser.

Security

- Sensitive keys are loaded from `.env` using `python-dotenv`.
- The `.env` file must not be committed to GitHub.
- Use `.env.example` to document required variables without exposing real credentials.
- Use Stripe test credentials while testing payment functionality.

