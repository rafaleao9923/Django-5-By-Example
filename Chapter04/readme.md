# Django Bookmarks Application

## Overview
This is a Django-based user profile management system that provides:
- User authentication (login/logout)
- User registration
- Profile management with photo upload
- Dashboard interface

## Key Features
- User authentication system
- Profile management with:
  - Date of birth
  - Profile photo
  - Basic user information
- Media file handling
- Email-based notifications (development mode)

## Technology Stack
- Django 5.0.4
- SQLite database (development)
- Pillow for image handling
- Docker-based development environment

## Setup Instructions
1. Clone the repository
2. Run `docker compose up` to start the development environment
3. Access the application at http://localhost:8000

## Application Flow

```mermaid
flowchart TD
    A[User] -->|Visits| B(Login Page)
    B -->|Valid Credentials| C[Dashboard]
    B -->|New User| D(Registration)
    D -->|Success| C
    C -->|Edit Profile| E[Profile Management]
    E -->|Upload Photo| F[Media Storage]
    E -->|Update Details| G[Database]
    C -->|Logout| H[Logged Out]
    
    style A fill:#f9f,stroke:#333,stroke-width:4px
    style C fill:#bbf,stroke:#333,stroke-width:4px
    style E fill:#f96,stroke:#333,stroke-width:4px
