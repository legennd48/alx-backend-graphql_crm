# ALX Backend GraphQL CRM

A Django-based Customer Relationship Management (CRM) system built with GraphQL API using Graphene-Django.

## 🚀 Features

- GraphQL API endpoint
- Customer management
- Real-time queries with GraphiQL interface
- Django admin integration
- Extensible schema architecture

## 📋 Prerequisites

- Python 3.8+
- Django 4.0+
- pip (Python package manager)

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/alx-backend-graphql_crm.git
   cd alx-backend-graphql_crm
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install django graphene-django django-filter
   ```

4. **Run migrations**
   ```bash
   python manage.py migrate
   ```

5. **Create a superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

6. **Start the development server**
   ```bash
   python manage.py runserver
   ```

## 🔧 Configuration

### Settings Configuration

The project is configured with the following key settings:

```python
INSTALLED_APPS = [
    # ... default Django apps
    'graphene_django',
    'crm',
]

GRAPHENE = {
    'SCHEMA': 'schema.schema'
}
```

### URL Configuration

GraphQL endpoint is available at `/graphql/` with GraphiQL interface enabled.

## 📊 GraphQL Schema

### Available Queries

#### Basic Query
```graphql
{
  hello
}
```

Response:
```json
{
  "data": {
    "hello": "Hello, GraphQL!"
  }
}
```

#### Customer Queries (if models are implemented)
```graphql
# Get all customers
{
  allCustomers {
    id
    name
    email
    createdAt
  }
}

# Get specific customer
{
  customer(id: 1) {
    id
    name
    email
    createdAt
  }
}
```

## 🌐 API Endpoints

| Endpoint | Description |
|----------|-------------|
| `/graphql/` | Main GraphQL endpoint with GraphiQL interface |
| `/admin/` | Django admin interface |

## 📁 Project Structure

```
alx-backend-graphql_crm/
├── alx-backend-graphql_crm/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── crm/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── views.py
│   ├── tests.py
│   └── migrations/
├── schema.py
├── manage.py
└── README.md
```

## 🧪 Testing

### Using GraphiQL Interface

1. Start the development server
2. Navigate to `http://localhost:8000/graphql/`
3. Use the interactive GraphiQL interface to test queries

### Example Test Query

```graphql
{
  hello
}
```

Expected output:
```json
{
  "data": {
    "hello": "Hello, GraphQL!"
  }
}
```

## 📚 Development

### Adding New Models

1. Create models in `crm/models.py`
2. Create corresponding GraphQL types in `schema.py`
3. Add queries/mutations to the schema
4. Run migrations: `python manage.py makemigrations && python manage.py migrate`

### Example Model Addition

```python
# crm/models.py
class Customer(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)
```

```python
# schema.py
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = "__all__"
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Troubleshooting

### Common Issues

1. **GraphQL endpoint not working**
   - Ensure `graphene_django` is in `INSTALLED_APPS`
   - Check that `GRAPHENE` setting points to correct schema

2. **CSRF token missing**
   - The endpoint uses `csrf_exempt` decorator as configured

3. **Import errors**
   - Make sure all dependencies are installed: `pip install graphene-django django-filter`

## 📞 Support

For support and questions:
- Create an issue in the GitHub repository
- Contact: [your-email@example.com]

## 🔗 Links

- [Django Documentation](https://docs.djangoproject.com/)
- [Graphene-Django Documentation](https://docs.graphene-python.org/projects/django/)
- [GraphQL Official Site](https://graphql.org/)

---

**Built with ❤️ for ALX Backend Specialization**