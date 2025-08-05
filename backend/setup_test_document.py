#!/usr/bin/env python3
"""
Setup a test document with extracted content for chat testing
"""

import sqlite3
import json
from datetime import datetime

def setup_test_document():
    """Create a test document with extracted content"""
    
    # Sample extracted markdown content
    extracted_md = """# Financial Report Q3 2024

## Executive Summary
The company achieved record revenue of $50 million in Q3 2024, representing a 25% increase year-over-year.

## Key Metrics
- **Revenue**: $50 million
- **Profit Margin**: 22%
- **Customer Growth**: 15,000 new customers
- **Employee Count**: 450

## Product Performance
Our flagship product, DataSync Pro, continues to dominate the market with a 35% market share.
The new AI-powered features have been well-received by enterprise customers.

## Regional Performance
- **North America**: $30 million (60%)
- **Europe**: $15 million (30%)
- **Asia Pacific**: $5 million (10%)

## Future Outlook
We expect continued growth in Q4 with the launch of our new cloud platform.
Investment in R&D will increase by 20% to maintain our competitive edge.
"""

    # Sample extracted data
    extracted_data = {
        "title": "Financial Report Q3 2024",
        "revenue": "$50 million",
        "profit_margin": "22%",
        "customer_growth": "15,000",
        "regions": {
            "north_america": "$30 million",
            "europe": "$15 million", 
            "asia_pacific": "$5 million"
        }
    }
    
    # Connect to database
    conn = sqlite3.connect('apex_ade.db')
    cursor = conn.cursor()
    
    # Update the first document with extracted content
    cursor.execute("""
        UPDATE documents 
        SET extracted_md = ?, 
            extracted_data = ?,
            processed_at = ?
        WHERE id = 1
    """, (extracted_md, json.dumps(extracted_data), datetime.now().isoformat()))
    
    conn.commit()
    
    # Verify the update
    cursor.execute("SELECT id, filename, status, extracted_md FROM documents WHERE id = 1")
    doc = cursor.fetchone()
    
    if doc:
        print(f"✅ Updated document {doc[0]} ({doc[1]})")
        print(f"   Status: {doc[2]}")
        print(f"   Extracted content: {len(doc[3])} characters")
    else:
        print("❌ Document not found")
    
    conn.close()

if __name__ == "__main__":
    setup_test_document()