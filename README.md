# Expense Tracker API

This is a RESTful API for an Expense Tracker application, built using [FastAPI](https://fastapi.tiangolo.com/). The API allows users to manage and track expenses efficiently by interacting with various endpoints.

## Prerequisites

Before getting started, ensure that you have the following tools installed on your machine:

- **Python 3.12.5**
- **PostgreSQL** (Ensure pgAdmin4 is installed to manage the database)
- **pip** (Python package installer)

## Getting Started

Follow the steps below to set up and run the project locally.

### 1. Clone the Repository

Clone this repository to your local machine using:

```bash
git clone https://github.com/Viay0710/expense-tracker.git
```

### 2. Setting Up Dependencies

#### Creating Virtual Environment
It is advised to create a virtual environment before proceeding with installation of dependencies
```bash
virtualenv venv
```

#### Activating Virtual Environment
On Windows
```bash
.\venv\Scripts\activate
```
On Mac
```bash
source venv/bin/activate
```

### Installing Dependencies
```bash
pip install -r requirements.txt
```

### 3. Running Fast API Server
[label /expense-tracker-api]
```bash
fastapi dev main.py
```
