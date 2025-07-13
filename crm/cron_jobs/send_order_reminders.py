#!/usr/bin/env python3

import os
import sys
from datetime import datetime, timedelta
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

# Add project directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

def send_order_reminders():
    """
    Query GraphQL endpoint for pending orders and log reminders
    """
    # GraphQL endpoint
    transport = RequestsHTTPTransport(url="http://localhost:8000/graphql")
    client = Client(transport=transport, fetch_schema_from_transport=True)
    
    # Calculate date 7 days ago
    seven_days_ago = datetime.now() - timedelta(days=7)
    seven_days_ago_str = seven_days_ago.isoformat()
    
    # GraphQL query for recent orders
    query = gql("""
        query GetRecentOrders($startDate: DateTime!) {
            allOrders(orderDate_Gte: $startDate) {
                edges {
                    node {
                        id
                        orderDate
                        customer {
                            email
                            name
                        }
                        totalAmount
                    }
                }
            }
        }
    """)
    
    try:
        # Execute the query
        result = client.execute(query, variable_values={"startDate": seven_days_ago_str})
        
        # Process orders
        orders = result.get('allOrders', {}).get('edges', [])
        
        # Log reminders
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        with open('/tmp/order_reminders_log.txt', 'a') as log_file:
            log_file.write(f"[{timestamp}] Order reminders batch started\n")
            
            for order_edge in orders:
                order = order_edge['node']
                order_id = order['id']
                customer_email = order['customer']['email']
                customer_name = order['customer']['name']
                order_date = order['orderDate']
                total_amount = order['totalAmount']
                
                log_entry = f"[{timestamp}] Reminder: Order ID {order_id}, Customer: {customer_name} ({customer_email}), Date: {order_date}, Amount: ${total_amount}\n"
                log_file.write(log_entry)
            
            log_file.write(f"[{timestamp}] Processed {len(orders)} order reminders\n")
        
        print("Order reminders processed!")
        
    except Exception as e:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open('/tmp/order_reminders_log.txt', 'a') as log_file:
            log_file.write(f"[{timestamp}] Error processing order reminders: {str(e)}\n")
        print(f"Error processing order reminders: {str(e)}")

if __name__ == "__main__":
    send_order_reminders()
