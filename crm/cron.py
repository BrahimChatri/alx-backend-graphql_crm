# crm/cron.py

import os
import sys
from datetime import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_backend_graphql_crm.settings')
django.setup()

from crm.models import Product


def log_crm_heartbeat():
    """
    Log a heartbeat message every 5 minutes to confirm CRM health
    """
    timestamp = datetime.now().strftime('%d/%m/%Y-%H:%M:%S')
    message = f"{timestamp} CRM is alive"
    
    # Test GraphQL endpoint responsiveness
    try:
        transport = RequestsHTTPTransport(url="http://localhost:8000/graphql")
        client = Client(transport=transport, fetch_schema_from_transport=True)
        
        # Simple hello query to test endpoint
        query = gql("""
            query {
                hello
            }
        """)
        
        result = client.execute(query)
        graphql_status = "GraphQL endpoint responsive"
    except Exception as e:
        graphql_status = f"GraphQL endpoint error: {str(e)}"
    
    # Log to file
    with open('/tmp/crm_heartbeat_log.txt', 'a') as log_file:
        log_file.write(f"{message} - {graphql_status}\n")


def update_low_stock():
    """
    Update low stock products using GraphQL mutation
    """
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    try:
        # Use GraphQL mutation to update low stock products
        transport = RequestsHTTPTransport(url="http://localhost:8000/graphql")
        client = Client(transport=transport, fetch_schema_from_transport=True)
        
        # GraphQL mutation for updating low stock products
        mutation = gql("""
            mutation {
                updateLowStockProducts {
                    products {
                        id
                        name
                        stock
                    }
                    message
                    count
                }
            }
        """)
        
        # Execute the mutation
        result = client.execute(mutation)
        
        # Process the response
        mutation_data = result.get('updateLowStockProducts', {})
        updated_products = mutation_data.get('products', [])
        message = mutation_data.get('message', '')
        count = mutation_data.get('count', 0)
        
        # Log updates
        with open('/tmp/low_stock_updates_log.txt', 'a') as log_file:
            log_file.write(f"[{timestamp}] Low stock update batch started\n")
            log_file.write(f"[{timestamp}] {message}\n")
            
            for product in updated_products:
                log_entry = (f"[{timestamp}] Updated {product['name']}: "
                           f"new stock level {product['stock']}\n")
                log_file.write(log_entry)
            
            log_file.write(f"[{timestamp}] Updated {count} products via GraphQL mutation\n")
        
        print(f"Updated {count} low stock products via GraphQL")
        
    except Exception as e:
        # Fallback to direct database update if GraphQL fails
        try:
            low_stock_products = Product.objects.filter(stock__lt=10)
            
            updated_products = []
            
            for product in low_stock_products:
                old_stock = product.stock
                product.stock += 10
                product.save()
                
                updated_products.append({
                    'name': product.name,
                    'old_stock': old_stock,
                    'new_stock': product.stock
                })
            
            # Log updates
            with open('/tmp/low_stock_updates_log.txt', 'a') as log_file:
                log_file.write(f"[{timestamp}] GraphQL failed, using direct DB update\n")
                log_file.write(f"[{timestamp}] GraphQL Error: {str(e)}\n")
                
                for product_info in updated_products:
                    log_entry = (f"[{timestamp}] Updated {product_info['name']}: "
                               f"stock {product_info['old_stock']} -> {product_info['new_stock']}\n")
                    log_file.write(log_entry)
                
                log_file.write(f"[{timestamp}] Updated {len(updated_products)} products via fallback\n")
            
            print(f"Updated {len(updated_products)} low stock products (fallback method)")
            
        except Exception as fallback_error:
            with open('/tmp/low_stock_updates_log.txt', 'a') as log_file:
                log_file.write(f"[{timestamp}] Error in both GraphQL and fallback: {str(fallback_error)}\n")
            print(f"Error updating low stock products: {str(fallback_error)}")
