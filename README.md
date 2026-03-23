# Snap_Shop

Snap_Shop is a web-based product search and crowdsourcing platform that helps users discover the best deals across multiple marketplaces. Users can search for products on eBay and Amazon, compare prices and ratings, and contribute new product data to improve the platform.

---

## Features

### Product Search
- Search for products across eBay and Amazon using keywords
- Automatically retrieve:
  - Cheapest product
  - Highest-rated product
- Uses OpenAI API to clean and extract product names from noisy or natural language input

### User Authentication
- Secure signup and login with Firebase Authentication (email/password)
- Session management for authenticated users

### Crowdsourcing
- Users can submit new products for review
- Backend integration with Firestore (currently in progress)

### Frontend
- Simple and responsive HTML interface
- Dedicated pages for homepage and product listings
- Firebase SDK pre-configured for future enhancements

### Backend
- Built with Flask (Python)
- Real-time product search using:
  - eBay API
  - Amazon (via RapidAPI)
- OpenAI API integration for intelligent query parsing

---

## Installation

### 1. Clone the repository
```bash
git clone https://github.com/markkamuya/Snap_Shop.git
cd Snap_Shop
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Create a `config.py` file in the root directory:

```python
# Example config.py

OPENAI_API_KEY = "your_openai_api_key_here"
EBAY_APP_ID = "your_ebay_app_id_here"
RAPIDAPI_KEY = "your_rapidapi_key_here"
SECRET_KEY = "your_flask_secret_key_here"

MAIL_USERNAME = "your_email@example.com"
MAIL_PASSWORD = "your_email_password_here"
```

Note: Keep `config.py` private. It is excluded from version control to protect sensitive credentials.

---

### 4. Run the application
```bash
python main.py
```

Open your browser and go to: http://localhost:5000

---

## Project Structure

```
Snap_Shop/
│
├── backend/
│   ├── products.py        # eBay & Amazon search logic
│   └── firebase_admin.py  # Firebase integration (in progress)
│
├── frontend/
│   ├── homepage.html      # Homepage UI
│   └── index.html         # Product listing page
│
├── main.py                # Flask app entry point
├── requirements.txt       # Python dependencies
├── config.py              # API keys (ignored by Git)
└── venv/                  # Virtual environment
```

---

## Currently in Development

- Firestore integration for storing submitted products
- Full Firebase authentication flow
- Complete crowdsourcing review system

---

## Contributing

Contributions are welcome.

1. Fork the repository  
2. Create a new branch:
   ```bash
   git checkout -b feature/YourFeature
   ```
3. Commit your changes:
   ```bash
   git commit -m "Add YourFeature"
   ```
4. Push to your branch:
   ```bash
   git push origin feature/YourFeature
   ```
5. Open a Pull Request

---

## Contributing

This repository is currently not open for public contributions.  
If you would like to collaborate, please contact the repository owner.

---

## Copyright

This project is not licensed for public use.

All rights are reserved by the author.  
No part of this repository may be copied, modified, distributed, or used without explicit permission.

---

## Vision

Snap_Shop aims to combine price comparison, AI-powered search, and community-driven data into one seamless shopping experience.
