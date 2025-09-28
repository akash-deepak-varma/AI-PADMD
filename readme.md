# AI-Powered Medical OCR System

An intelligent document processing pipeline that extracts and categorizes financial amounts from medical documents (bills/receipts) using OCR technology and Large Language Models. The system features a Node.js backend proxy to a FastAPI LLM service, with MySQL database storage and JWT-based authentication.

## 🚀 Features

- **User Authentication**: Secure signup and login with JWT token-based authentication
- **Document Processing**: Upload medical documents for automated OCR processing
- **AI-Powered Analysis**: Multi-stage LLM pipeline for intelligent data extraction:
  - **Normalization**: Automatic OCR error correction
  - **Classification**: Context-aware categorization (total_bill, paid, discount, etc.)
  - **Enhancement**: Currency detection, source attribution, and summary generation
- **Data Persistence**: Store and retrieve processing results with user-specific history
- **Secure API**: JWT-protected endpoints for sensitive operations

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| **Backend** | Node.js (Express.js) |
| **AI/OCR** | FastAPI + LiteLLM / EasyOCR |
| **Database** | MySQL 8 |
| **Authentication** | JWT + bcrypt |
| **File Upload** | Multer |
| **HTTP Client** | node-fetch + FormData |

## 📁 Project Structure

```
project-root/
│
├── server.js                  # Node.js backend entry point
├── package.json               # Node.js dependencies
├── .env                       # Environment variables
├── uploads/                   # Temporary file storage
├── ocr_pipeline/              # Python FastAPI backend
│   ├── main.py               # FastAPI application
│   ├── llm_utils.py          # LLM processing utilities
│   ├── ocr.py                # OCR processing
│   ├── utils.py              # Helper functions
│   └── config.py             # Configuration settings
└── README.md                  # Project documentation
```

### Component Overview

- **server.js**: Express.js server handling JWT authentication, MySQL integration, and proxy routes to FastAPI
- **ocr_pipeline/**: FastAPI backend containing the OCR + LLM processing pipeline
- **uploads/**: Temporary storage directory for uploaded document files

## 🗄️ Database Schema

**Database**: `ocr_system`

### Users Table
```sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Results Table
```sql
CREATE TABLE results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    pipeline JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

## ⚙️ Setup Instructions

### 1. Clone the Repository
```bash
git clone <repo_url>
cd project-root
```

### 2. Install Node.js Dependencies
```bash
npm install
```

### 3. Install Python Dependencies
```bash
pip install -r ocr_pipeline/requirements.txt
```

### 4. Environment Configuration
Create a `.env` file in the project root:
```env
DB_HOST=localhost
DB_USER=root
DB_PASS="your_mysql_password"
DB_NAME=ocr_system
JWT_SECRET="your_jwt_secret_here"
```

### 5. Database Setup
Connect to MySQL and create the database:
```sql
CREATE DATABASE ocr_system;
USE ocr_system;

-- Users table
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Results table
CREATE TABLE results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    pipeline JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

## 🏃‍♂️ Running the Application

### 1. Start FastAPI Backend (OCR + LLM Service)
```bash
cd ocr_pipeline
uvicorn main:app --reload --port 8000
```

### 2. Start Node.js Server
```bash
cd ..
node server.js
```

The Node.js server will run at `http://127.0.0.1:8001` and proxy requests to the FastAPI backend.

## 📚 API Endpoints

| Endpoint | Method | Auth Required | Description |
|----------|--------|---------------|-------------|
| `/signup` | POST | ❌ | Create new user account |
| `/login` | POST | ❌ | User login and JWT token generation |
| `/process_image_stepwise` | POST | ✅ | Upload and process medical documents |
| `/results` | GET | ✅ | Retrieve user's processing history |

### Request Examples

#### User Signup
```json
POST /signup
Content-Type: application/json

{
  "username": "akash",
  "password": "password123"
}
```

#### User Login
```json
POST /login
Content-Type: application/json

{
  "username": "akash",
  "password": "password123"
}
```

#### Process Medical Document
```
POST /process_image_stepwise
Content-Type: multipart/form-data
Authorization: Bearer <JWT_TOKEN>

Form Data:
- file: [uploaded image file]
```

#### Retrieve Results
```
GET /results
Authorization: Bearer <JWT_TOKEN>
```

## 🧪 Testing with Postman

### Complete Workflow

1. **User Registration**
   - Method: `POST`
   - URL: `http://127.0.0.1:8001/signup`
   - Body: JSON with username and password

2. **User Login**
   - Method: `POST`
   - URL: `http://127.0.0.1:8001/login`
   - Body: JSON with credentials
   - Action: Copy the JWT token from response

3. **Configure Authorization**
   - Type: Bearer Token
   - Token: Paste the JWT token from login response

4. **Upload Document**
   - Method: `POST`
   - URL: `http://127.0.0.1:8001/process_image_stepwise`
   - Headers: Authorization with Bearer token
   - Body: form-data with key `file` and select image file

5. **Fetch Results History**
   - Method: `GET`
   - URL: `http://127.0.0.1:8001/results`
   - Headers: Authorization with Bearer token

## 📝 Important Notes

### Authentication & Security
- JWT tokens expire after 1 hour by default (`expiresIn: "1h"`)
- Passwords are securely hashed using bcrypt
- JWT payload structure: `{ id, username }`
- Protected routes require valid JWT token in Authorization header

### Data Storage
- All processed results are stored in JSON format in the `results.pipeline` column
- User-specific data isolation ensures privacy and security
- Processing history is maintained for each user account

### Processing Pipeline
The FastAPI backend implements a sophisticated multi-stage pipeline:
1. **OCR**: Text extraction from uploaded medical documents
2. **Normalization**: AI-powered correction of OCR recognition errors
3. **Classification**: Intelligent categorization of extracted numbers and amounts
4. **Final Output**: Enhanced results with currency detection, source attribution, and summary

## 🔧 Troubleshooting

### Common Issues
- Ensure both FastAPI (port 8000) and Node.js (port 8001) servers are running
- Verify MySQL connection and database setup
- Check that all environment variables are properly configured
- Confirm JWT token is included in Authorization header for protected routes

### Dependencies
- Node.js version 14 or higher recommended
- Python 3.8+ for FastAPI backend
- MySQL 8.0+ for database operations

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request



**Built with ❤️ for intelligent medical document processing by Akash**