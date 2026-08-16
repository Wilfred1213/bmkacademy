# BMK Academy Management System

A Django-based school management system for managing students, attendance, school fees, payments, and related academic records.

## Overview

BMK Academy Management System is being developed to provide a centralized platform for managing important day-to-day school operations.

The project is built with **Django** and uses Django's ORM and service-layer approach to keep business logic separate from views.

## Current Features

### Student Management

* Student registration and profiles
* Admission numbers
* Student status tracking
* Gender and date of birth
* Student enrollment and current class
* Parent/student relationships
* Student detail pages

### Attendance Management

* Select a school class and attendance date
* Mark students as:

  * Present
  * Absent
  * Late
  * Excused
* Attendance history
* Individual student attendance records
* Attendance statistics
* Attendance rate calculation

### School Fees

* Create fee invoices
* View student fee summaries
* Track total invoiced amount
* Track total payments
* Calculate outstanding balances
* Automatically update invoice status
* Record payments
* Payment history
* Payment receipts
* Print-friendly payment receipts
* Prevent payments greater than the outstanding invoice balance
* Invoice cancellation

### Fee Invoice Status

Invoices can have the following statuses:

* Unpaid
* Partially Paid
* Paid
* Cancelled

## Technology Stack

* **Python**
* **Django**
* **Django ORM**
* **HTML5**
* **Bootstrap 5**
* **MySQL**
* **Git / GitHub**

## Project Structure

```text
bmk_academy/
│
├── academics/
│   ├── models.py
│   ├── views.py
│   └── urls.py
│
├── attendance/
│   ├── models.py
│   ├── services.py
│   ├── views.py
│   ├── urls.py
│   └── templates/
│
├── fees/
│   ├── models.py
│   ├── services.py
│   ├── views.py
│   ├── urls.py
│   └── templates/
│
├── students/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── templates/
│
├── templates/
│   └── base.html
│
├── manage.py
└── README.md
```

## Service Layer

The project uses service classes for important business logic.

For example, fee-related operations are handled by `FeeService`.

Some of the current methods include:

```python
FeeService.get_paid_amount(invoice)
FeeService.get_balance(invoice)
FeeService.update_invoice_status(invoice)
FeeService.record_payment(...)
FeeService.get_invoice_summary(invoice)
FeeService.get_payment_history(invoice)
FeeService.get_student_fee_summary(student)
FeeService.cancel_invoice(invoice)
```

This keeps business rules such as payment validation and invoice status updates out of the templates and reduces duplication between views.

## Fee Payment Logic

The system calculates an invoice balance using:

```text
Outstanding Balance = Invoice Amount - Total Payments
```

The system also prevents a payment from exceeding the outstanding balance.

For example:

```text
Invoice Amount:       ₦100,000
Already Paid:          ₦90,000
Outstanding Balance:   ₦10,000
```

A payment of ₦10,000 is allowed, while a payment of ₦15,000 is rejected.

## Attendance Logic

Attendance is recorded against the student's current enrollment and school class.

Each attendance record can have one of four statuses:

```text
Present
Absent
Late
Excused
```

The system can then calculate individual attendance statistics such as:

```text
Total attendance records
Present
Absent
Late
Excused
Attendance rate
```

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/Wilfred1213/bmkacademy.git
```

### 2. Enter the project directory

```bash
cd bmk_academy
```

### 3. Create a virtual environment

Windows:

```bash
python -m venv .venv
```

Activate it:

```bash
.venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure environment variables

Create a `.env` file and configure the required database and Django settings.

Do not commit sensitive credentials such as:

* `SECRET_KEY`
* Database passwords
* API keys
* Email credentials

### 6. Run migrations

```bash
python manage.py migrate
```

### 7. Create a superuser

```bash
python manage.py createsuperuser
```

### 8. Start the development server

```bash
python manage.py runserver
```

Then open:

```text
http://127.0.0.1:8000/
```

## Development Status

This project is currently under active development.

The current focus is building the core school management functionality and establishing a clean and maintainable Django architecture.

Future modules and improvements will be added as development continues.

## Author

**Wilfred Mathias**

Built with Django for BMK Academy.
