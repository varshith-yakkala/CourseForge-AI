# Security Policy — CourseForge AI

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

---

## Security Safeguards Implemented

1. **HTTP Security Headers**: Enforces `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, `Strict-Transport-Security`, and `Content-Security-Policy`.
2. **JWT Authentication**: Password hashing using Passlib (Bcrypt) and signed JWT bearer tokens.
3. **Request Tracing**: `X-Request-ID` tracking for auditing and observability.
4. **SQL Injection Prevention**: Built entirely with SQLAlchemy ORM parameterized queries.

---

## Reporting a Vulnerability

If you discover a potential security vulnerability within CourseForge AI, please report it by emailing the maintainer directly. Do not report security vulnerabilities via public GitHub issues.
