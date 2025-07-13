#!/usr/bin/env python3
"""
Test script for manually testing cron functions
"""

import sys
import os
import django

# Set up Django environment
sys.path.append(os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_backend_graphql_crm.settings')
django.setup()

from crm.cron import log_crm_heartbeat, update_low_stock
from crm.models import Product

def test_heartbeat():
    """Test the heartbeat logging function"""
    print("Testing heartbeat function...")
    log_crm_heartbeat()
    print("Heartbeat logged. Check /tmp/crm_heartbeat_log.txt")

def test_low_stock_update():
    """Test the low stock update function"""
    print("Testing low stock update function...")
    
    # Create some test products with low stock
    print("Creating test products with low stock...")
    test_products = [
        {'name': 'Test Product 1', 'price': 10.00, 'stock': 5},
        {'name': 'Test Product 2', 'price': 20.00, 'stock': 3},
        {'name': 'Test Product 3', 'price': 15.00, 'stock': 8},
    ]
    
    for product_data in test_products:
        product, created = Product.objects.get_or_create(
            name=product_data['name'],
            defaults=product_data
        )
        if created:
            print(f"Created: {product.name} with stock {product.stock}")
        else:
            # Update existing product to have low stock
            product.stock = product_data['stock']
            product.save()
            print(f"Updated: {product.name} to stock {product.stock}")
    
    # Show products before update
    print("\nProducts with stock < 10 before update:")
    low_stock_products = Product.objects.filter(stock__lt=10)
    for product in low_stock_products:
        print(f"- {product.name}: {product.stock}")
    
    # Run the update function
    print("\nRunning low stock update...")
    update_low_stock()
    
    # Show products after update
    print("\nProducts after update:")
    updated_products = Product.objects.filter(name__startswith='Test Product')
    for product in updated_products:
        print(f"- {product.name}: {product.stock}")
    
    print("Low stock update completed. Check /tmp/low_stock_updates_log.txt")

def cleanup_test_products():
    """Clean up test products"""
    print("Cleaning up test products...")
    deleted_count = Product.objects.filter(name__startswith='Test Product').delete()[0]
    print(f"Deleted {deleted_count} test products")

if __name__ == "__main__":
    print("CRM Cron Functions Test Script")
    print("=" * 40)
    
    while True:
        print("\nOptions:")
        print("1. Test heartbeat function")
        print("2. Test low stock update function")
        print("3. Cleanup test products")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == '1':
            test_heartbeat()
        elif choice == '2':
            test_low_stock_update()
        elif choice == '3':
            cleanup_test_products()
        elif choice == '4':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")
