import os
import pandas as pd
from dotenv import load_dotenv
from corpus_loader import load_corpus
from retriever import retrieve
from agent import generate_response

def test_validation():
    load_dotenv()
    
    # Check API key
    if not os.environ.get("OPENROUTER_API_KEY"):
        print("Error: OPENROUTER_API_KEY not set.")
        return

    print("Loading corpus...")
    corpus = load_corpus()
    
    # Load sample tickets
    sample_file = "../support_tickets/sample_support_tickets.csv"
    if not os.path.exists(sample_file):
        print(f"Error: {sample_file} not found.")
        return
        
    df = pd.read_csv(sample_file)
    
    # Test on first 3 tickets
    print(f"Running validation on first 3 sample tickets...")
    for idx, row in df.head(3).iterrows():
        issue = str(row.get("Issue", ""))
        subject = str(row.get("Subject", ""))
        company = str(row.get("Company", ""))
        
        print(f"\n--- Ticket {idx+1} ---")
        print(f"Company: {company}")
        print(f"Subject: {subject}")
        
        articles = retrieve(issue, subject, company, corpus)
        print(f"Retrieved {len(articles)} articles.")
        
        try:
            result = generate_response(issue, subject, company, articles)
            print(f"Status: {result.get('status')}")
            print(f"Request Type: {result.get('request_type')}")
            print(f"Product Area: {result.get('product_area')}")
            print(f"Response (truncated): {result.get('response', '')[:100]}...")
            
            # Ground truth comparison (if columns exist)
            gt_status = row.get("Status")
            if pd.notna(gt_status):
                print(f"Ground Truth Status: {gt_status}")
                if result.get("status").lower() == gt_status.lower():
                    print("✅ Status Match!")
                else:
                    print("❌ Status Mismatch")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    test_validation()
