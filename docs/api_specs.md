# UniFound REST API Specification (Phase 1)

## Base URL
`/api/v1`

---

## Authentication & Users Endpoints

### 1. Register User
- **Method**: `POST`
- **Path**: `/api/v1/auth/register`
- **Request Body**:
  ```json
  {
    "email": "student@campus.edu",
    "password": "SecurePassword123!",
    "full_name": "Alex Student",
    "phone": "+1 555-0199",
    "department": "Computer Science",
    "role": "USER"
  }
  ```
- **Response** `201 Created`:
  ```json
  {
    "id": 1,
    "email": "student@campus.edu",
    "full_name": "Alex Student",
    "phone": "+1 555-0199",
    "department": "Computer Science",
    "role": "USER",
    "is_active": true,
    "created_at": "2026-09-03T19:40:00Z"
  }
  ```

### 2. Login User
- **Method**: `POST`
- **Path**: `/api/v1/auth/login`
- **Request Body**:
  ```json
  {
    "email": "student@campus.edu",
    "password": "SecurePassword123!"
  }
  ```
- **Response** `200 OK`:
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsIn...",
    "token_type": "bearer",
    "user": {
      "id": 1,
      "email": "student@campus.edu",
      "full_name": "Alex Student",
      "role": "USER"
    }
  }
  ```

### 3. Get Current User Profile
- **Method**: `GET`
- **Path**: `/api/v1/auth/me`
- **Headers**: `Authorization: Bearer <access_token>`
- **Response** `200 OK`: Current user object.

### 4. Update User Profile
- **Method**: `PUT`
- **Path**: `/api/v1/users/profile`
- **Headers**: `Authorization: Bearer <access_token>`
- **Request Body**:
  ```json
  {
    "full_name": "Alex Updated",
    "phone": "+1 555-9988",
    "department": "Electrical Engineering",
    "avatar_url": "https://..."
  }
  ```
- **Response** `200 OK`: Updated user profile.

### 5. Health Check
- **Method**: `GET`
- **Path**: `/api/v1/health`
- **Response** `200 OK`:
  ```json
  {
    "status": "healthy",
    "timestamp": "2026-09-03T19:40:00Z",
    "version": "1.0.0",
    "environment": "development"
  }
  ```
