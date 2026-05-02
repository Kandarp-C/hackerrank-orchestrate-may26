import os
import time
import pandas as pd
from dotenv import load_dotenv
from corpus_loader import load_corpus
from retriever import retrieve
from agent import generate_response

def main():
    # Load environment variables
    load_dotenv()
    
    # Check for output directory/file requirements
    input_file = "../support_tickets/support_tickets.csv"
    output_file = "../support_tickets/output.csv"
    
    # Load corpus
    print("Loading support corpus...")
    corpus = load_corpus()
    print(f"Index complete. {len(corpus)} articles loaded.")
    
    # Load tickets
    if not os.path.exists(input_file):
        print(f"Error: Input file {input_file} not found.")
        return
        
    df = pd.read_csv(input_file)
    print(f"Processing {len(df)} tickets...")
    
    results = []
    
    for idx, row in df.iterrows():
        issue = str(row.get("Issue", ""))
        subject = str(row.get("Subject", ""))
        company = str(row.get("Company", "")).strip()
        
        print(f"[{idx+1}/{len(df)}] Processing: {company} | {subject[:50]}...")
        
        # 1. Retrieve relevant articles
        articles = retrieve(issue, subject, company, corpus)
        
        # 2. Generate response via LLM
        try:
            prediction = generate_response(issue, subject, company, articles)
        except Exception as e:
            print(f"  FAILED: {e}")
            # Graceful failover to escalation
            prediction = {
                "status": "escalated",
                "product_area": "general",
                "request_type": "product_issue",
                "response": "This issue has been escalated to a human agent for further review due to an internal processing error.",
                "justification": f"Automated processing failed: {str(e)}"
            }
        
        # Merge with input row for final CSV
        # schema: issue,subject,company,response,product_area,status,request_type,justification
        results.append({
            "issue": issue,
            "subject": subject,
            "company": company,
            "response": prediction.get("response", ""),
            "product_area": prediction.get("product_area", ""),
            "status": prediction.get("status", "escalated"),
            "request_type": prediction.get("request_type", "product_issue"),
            "justification": prediction.get("justification", "")
        })
        
        # Rate limiting for OpenRouter
        time.sleep(1)

    # Save results
    output_df = pd.DataFrame(results)
    # Ensure exact column order per requirement
    output_df = output_df[["issue", "subject", "company", "response", "product_area", "status", "request_type", "justification"]]
    
    output_df.to_csv(output_file, index=False)
    print(f"\nProcessing complete. Output saved to {output_file}")

if __name__ == "__main__":
    main()
