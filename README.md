# 🚗 Bless Digital Auto Care - Professional Car Diagnostic System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🌟 Overview

A **production-ready, professional car diagnostic system** that helps mechanics and car owners diagnose engine, battery, and starter issues. Features include customer management, vehicle history tracking, professional report generation, PWA support, and a mobile-friendly interface.

## ✨ Features

### Core Features
- 🔧 **Engine Diagnostic** - Overheating, smoke, noises, check engine light
- 🔋 **Battery & Charging System** - Voltage tests, load testing, alternator check  
- ⚡ **Starter System** - Clicking sounds, cranking issues, electrical faults

### Professional Features  
- 📊 **Customer & Vehicle Management** - Complete service history
- 📄 **Professional Report Generation** - Printable diagnostic reports
- 📱 **PWA Installable** - Works offline, install on phones
- 💰 **Cost Estimation** - Labor, parts, tax calculation
- 📈 **Real-time Statistics Dashboard** - Business metrics

## 🛠️ Tech Stack

### Frontend
- HTML5, CSS3, JavaScript (Vanilla)
- PWA with Service Worker
- Responsive Mobile-First Design

### Backend
- Python 3.11+
- Flask (REST API)
- SQLite3 (Database)
- Gunicorn (Production server)

### DevOps
- GitHub (Version Control)
- Render.com (Backend Hosting)

## 📦 Installation

### Local Development

```bash
# Clone the repository
git clone https://github.com/BLESS06703/auto-diagnostic-system.git
cd auto-diagnostic-system

# Install dependencies
pip install -r requirements.txt

# Run the API server
python api_server.py

# In another terminal, serve the frontend
python -m http.server 3000

# Open http://localhost:3000/web_interface.html
