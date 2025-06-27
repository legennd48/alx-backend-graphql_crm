import graphene
from graphene_django import DjangoObjectType
from django.core.exceptions import ValidationError
from django.db import transaction
from decimal import Decimal, InvalidOperation
from .models import Customer, Product, Order
import re


# GraphQL Types
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = "__all__"


class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = "__all__"


class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = "__all__"


# Custom Error Types
class ErrorType(graphene.ObjectType):
    field = graphene.String()
    message = graphene.String()


class CustomerErrorType(graphene.ObjectType):
    index = graphene.Int()
    email = graphene.String()
    errors = graphene.List(ErrorType)


# Mutation Response Types
class CreateCustomerResponse(graphene.ObjectType):
    customer = graphene.Field(CustomerType)
    success = graphene.Boolean()
    message = graphene.String()
    errors = graphene.List(ErrorType)


class BulkCreateCustomersResponse(graphene.ObjectType):
    customers = graphene.List(CustomerType)
    success_count = graphene.Int()
    errors = graphene.List(CustomerErrorType)
    message = graphene.String()


class CreateProductResponse(graphene.ObjectType):
    product = graphene.Field(ProductType)
    success = graphene.Boolean()
    message = graphene.String()
    errors = graphene.List(ErrorType)


class CreateOrderResponse(graphene.ObjectType):
    order = graphene.Field(OrderType)
    success = graphene.Boolean()
    message = graphene.String()
    errors = graphene.List(ErrorType)


# Input Types
class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()


# Utility Functions
def validate_phone(phone):
    """Validate phone number format"""
    if not phone:
        return True
    
    phone_clean = re.sub(r'[^\d+\-]', '', phone)
    return bool(re.match(r'^\+?1?\d{9,15}$|^\d{3}-\d{3}-\d{4}$', phone_clean))


def validate_email(email):
    """Validate email format"""
    return bool(re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email))


# Mutations
class CreateCustomer(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        email = graphene.String(required=True)
        phone = graphene.String()

    Output = CreateCustomerResponse

    def mutate(self, info, name, email, phone=None):
        errors = []

        # Validate email format
        if not validate_email(email):
            errors.append(ErrorType(field="email", message="Invalid email format"))

        # Validate phone format
        if phone and not validate_phone(phone):
            errors.append(ErrorType(field="phone", message="Invalid phone number format"))

        # Check email uniqueness
        if Customer.objects.filter(email=email).exists():
            errors.append(ErrorType(field="email", message="Email already exists"))

        if errors:
            return CreateCustomerResponse(
                customer=None,
                success=False,
                message="Validation failed",
                errors=errors
            )

        try:
            customer = Customer.objects.create(
                name=name.strip(),
                email=email.lower().strip(),
                phone=phone.strip() if phone else None
            )
            return CreateCustomerResponse(
                customer=customer,
                success=True,
                message="Customer created successfully",
                errors=[]
            )
        except Exception as e:
            return CreateCustomerResponse(
                customer=None,
                success=False,
                message="Failed to create customer",
                errors=[ErrorType(field="general", message=str(e))]
            )


class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        customers = graphene.List(CustomerInput, required=True)

    Output = BulkCreateCustomersResponse

    def mutate(self, info, customers):
        created_customers = []
        errors = []
        
        with transaction.atomic():
            for index, customer_data in enumerate(customers):
                customer_errors = []
                
                # Validate email format
                if not validate_email(customer_data.email):
                    customer_errors.append(ErrorType(field="email", message="Invalid email format"))

                # Validate phone format
                if customer_data.phone and not validate_phone(customer_data.phone):
                    customer_errors.append(ErrorType(field="phone", message="Invalid phone number format"))

                # Check email uniqueness
                if Customer.objects.filter(email=customer_data.email).exists():
                    customer_errors.append(ErrorType(field="email", message="Email already exists"))

                if customer_errors:
                    errors.append(CustomerErrorType(
                        index=index,
                        email=customer_data.email,
                        errors=customer_errors
                    ))
                    continue

                try:
                    customer = Customer.objects.create(
                        name=customer_data.name.strip(),
                        email=customer_data.email.lower().strip(),
                        phone=customer_data.phone.strip() if customer_data.phone else None
                    )
                    created_customers.append(customer)
                except Exception as e:
                    errors.append(CustomerErrorType(
                        index=index,
                        email=customer_data.email,
                        errors=[ErrorType(field="general", message=str(e))]
                    ))

        return BulkCreateCustomersResponse(
            customers=created_customers,
            success_count=len(created_customers),
            errors=errors,
            message=f"Successfully created {len(created_customers)} customers"
        )


class CreateProduct(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        price = graphene.Decimal(required=True)
        stock = graphene.Int()

    Output = CreateProductResponse

    def mutate(self, info, name, price, stock=0):
        errors = []

        # Validate price
        try:
            price_decimal = Decimal(str(price))
            if price_decimal <= 0:
                errors.append(ErrorType(field="price", message="Price must be positive"))
        except (InvalidOperation, ValueError):
            errors.append(ErrorType(field="price", message="Invalid price format"))

        # Validate stock
        if stock < 0:
            errors.append(ErrorType(field="stock", message="Stock cannot be negative"))

        if errors:
            return CreateProductResponse(
                product=None,
                success=False,
                message="Validation failed",
                errors=errors
            )

        try:
            product = Product.objects.create(
                name=name.strip(),
                price=price_decimal,
                stock=stock
            )
            return CreateProductResponse(
                product=product,
                success=True,
                message="Product created successfully",
                errors=[]
            )
        except Exception as e:
            return CreateProductResponse(
                product=None,
                success=False,
                message="Failed to create product",
                errors=[ErrorType(field="general", message=str(e))]
            )


class CreateOrder(graphene.Mutation):
    class Arguments:
        customer_id = graphene.Int(required=True)
        product_ids = graphene.List(graphene.Int, required=True)

    Output = CreateOrderResponse

    def mutate(self, info, customer_id, product_ids):
        errors = []

        # Validate customer exists
        try:
            customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            errors.append(ErrorType(field="customer_id", message="Customer not found"))
            customer = None

        # Validate products exist
        if not product_ids:
            errors.append(ErrorType(field="product_ids", message="At least one product must be selected"))
        else:
            existing_products = Product.objects.filter(id__in=product_ids)
            if len(existing_products) != len(product_ids):
                invalid_ids = set(product_ids) - set(existing_products.values_list('id', flat=True))
                errors.append(ErrorType(
                    field="product_ids", 
                    message=f"Invalid product IDs: {list(invalid_ids)}"
                ))

        if errors:
            return CreateOrderResponse(
                order=None,
                success=False,
                message="Validation failed",
                errors=errors
            )

        try:
            with transaction.atomic():
                order = Order.objects.create(customer=customer)
                order.products.set(existing_products)
                order.total_amount = order.calculate_total()
                order.save()

            return CreateOrderResponse(
                order=order,
                success=True,
                message="Order created successfully",
                errors=[]
            )
        except Exception as e:
            return CreateOrderResponse(
                order=None,
                success=False,
                message="Failed to create order",
                errors=[ErrorType(field="general", message=str(e))]
            )


# Query Class
class Query(graphene.ObjectType):
    all_customers = graphene.List(CustomerType)
    all_products = graphene.List(ProductType)
    all_orders = graphene.List(OrderType)
    customer = graphene.Field(CustomerType, id=graphene.Int(required=True))
    product = graphene.Field(ProductType, id=graphene.Int(required=True))
    order = graphene.Field(OrderType, id=graphene.Int(required=True))

    def resolve_all_customers(self, info):
        return Customer.objects.all()

    def resolve_all_products(self, info):
        return Product.objects.all()

    def resolve_all_orders(self, info):
        return Order.objects.select_related('customer').prefetch_related('products')

    def resolve_customer(self, info, id):
        try:
            return Customer.objects.get(pk=id)
        except Customer.DoesNotExist:
            return None

    def resolve_product(self, info, id):
        try:
            return Product.objects.get(pk=id)
        except Product.DoesNotExist:
            return None

    def resolve_order(self, info, id):
        try:
            return Order.objects.select_related('customer').prefetch_related('products').get(pk=id)
        except Order.DoesNotExist:
            return None


# Mutation Class
class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
