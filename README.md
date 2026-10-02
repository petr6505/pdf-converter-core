# EfficientPDF - Backend Architecture Showcase

> ⚠️ **Project status: Discontinued.** The EfficientPDF.com service was shut down in October 2026 and is no longer available. This repository is kept for reference only and is not actively maintained.
>
> **Note:** This repository serves as a backend architectural showcase and portfolio piece for the former commercial SaaS application EfficientPDF.com.
> 
> 🔒 **To protect intellectual property, the core proprietary business logic (PDF parsing algorithms and Google Gemini LLM integration) has been omitted from this public repository.**

## Overview

This project demonstrates the Python backend infrastructure that ran the service in production. It showcases modern web development using Flask, focusing on clean architecture (Application Factory pattern, Blueprints), security, and robust integration with third-party APIs.

## Highlighted Features

* 🏗️ **Application Factory Pattern:** Scalable and maintainable Flask initialization and configuration management.
* 🔐 **Advanced Authentication:** * Custom login/registration flows protected by Google reCAPTCHA.
  * Secure password hashing using Werkzeug.
  * Google OAuth integration via Authlib.
* 📧 **Email Verification:** Secure, token-based email confirmation system utilizing the Resend API.
* 💳 **Payment Processing:** Full Stripe API integration, including Checkout Sessions and asynchronous Webhook handling for user credit top-ups.
* 🗄️ **Database Modeling:** Clean SQLAlchemy ORM implementation with Flask-Migrate for version control.

## Tech Stack

* **Backend Framework:** Python, Flask
* **Database:** SQLite / PostgreSQL (SQLAlchemy ORM)
* **Authentication:** Flask-Login, Authlib (OAuth)
* **Third-Party APIs:** Stripe, Resend, Google Cloud APIs
* **Infrastructure:** Docker, Gunicorn, Fly.io

---

# EfficientPDF - Ukázka backendové architektury

> ⚠️ **Stav projektu: Ukončeno.** Služba EfficientPDF.com byla v říjnu 2026 vypnuta a již není dostupná. Repozitář zůstává zachován pouze jako reference a není dále aktivně udržován.
>
> **Poznámka:** Tento repozitář slouží jako architektonická ukázka a součást portfolia backendu bývalé komerční SaaS aplikace EfficientPDF.com.
>
> 🔒 **Z důvodu ochrany duševního vlastnictví (IP) byla z tohoto veřejného repozitáře vynechána proprietární byznysová logika (algoritmy pro zpracování PDF a integrace s LLM modelem Google Gemini).**

## O projektu

Tento projekt prezentuje backendovou infrastrukturu, na které služba běžela v produkci. Ukazuje moderní vývoj v Pythonu (Flask) se zaměřením na čistou architekturu (Application Factory, Blueprints), bezpečnost a robustní integraci služeb třetích stran.

## Hlavní ukázky kódu

* 🏗️ **Application Factory Pattern:** Škálovatelná a snadno udržovatelná inicializace Flask aplikace.
* 🔐 **Pokročilá autentizace:** * Vlastní registrační a přihlašovací procesy chráněné pomocí Google reCAPTCHA.
  * Bezpečné hashování hesel pomocí Werkzeug.
  * Integrace Google OAuth přes Authlib.
* 📧 **Ověřování e-mailů:** Bezpečný systém potvrzování e-mailů na bázi časově omezených tokenů s využitím Resend API.
* 💳 **Zpracování plateb:** Kompletní integrace Stripe API, včetně Checkout Sessions a asynchronního zpracování Webhooků pro automatické připisování kreditů uživatelům.
* 🗄️ **Databázové modely:** Čistá implementace SQLAlchemy ORM s využitím Flask-Migrate pro správu verzí databáze.

## Použité technologie

* **Backend Framework:** Python, Flask
* **Databáze:** SQLite / PostgreSQL (SQLAlchemy ORM)
* **Autentizace:** Flask-Login, Authlib (OAuth)
* **Externí API:** Stripe, Resend, Google Cloud APIs
* **Infrastruktura:** Docker, Gunicorn, Fly.io