"""
dataset/synthetic_generator.py
==============================
Synthetic Enterprise Policy Dataset Generator for VeriFlow.
Generates balanced natural language policies and ground-truth WorkflowIR data
for fine-tuning, few-shot prompting, and safety benchmarking.
"""
import random
import json
import uuid
from typing import List, Dict, Any

DOMAINS = ["Procurement", "IT Asset Provisioning", "HR Onboarding", "Financial Reimbursement", "Cloud Infrastructure", "Legal Contract Review"]
ROLES = ["Employee", "Manager", "IT Manager", "Finance_Director", "Legal_Counsel", "Intern"]
VAGUE_WORDS = ["quickly", "soon", "powerful", "urgent", "expensive", "appropriate", "senior", "reasonable"]

def generate_synthetic_dataset(count: int = 200) -> List[Dict[str, Any]]:
    """Generates synthetic dataset of enterprise policies with ground-truth labels."""
    dataset = []
    
    for i in range(count):
        domain = random.choice(DOMAINS)
        is_ambiguous = random.random() < 0.35
        has_rbac_violation = random.random() < 0.25
        has_cycle = random.random() < 0.15
        
        amount = random.choice([500, 1500, 3000, 15000, 45000, 120000])
        
        if domain == "Procurement":
            req_role = "Intern" if has_rbac_violation else "Employee"
            appr_role = "Intern" if has_rbac_violation else ("Manager" if amount <= 20000 else "Finance_Director")
            
            if is_ambiguous:
                vague = random.choice(VAGUE_WORDS)
                text = f"When a new team joins, order {vague} equipment {random.choice(VAGUE_WORDS)}. Management should provide appropriate approval."
            elif has_cycle:
                text = "IT Manager Approval requires Finance Director Approval. Finance Director Approval requires IT Manager Approval before placing the order."
            elif has_rbac_violation:
                text = f"Intern requests ${amount:,} high-end workstation. Intern self-approves the order without Manager review."
            else:
                text = f"Employee submits equipment purchase request (${amount:,}). {appr_role} approves request (${amount:,} limit). Finance Director issues vendor payment."
                
        elif domain == "Financial Reimbursement":
            if is_ambiguous:
                text = f"Submit travel receipts {random.choice(VAGUE_WORDS)}. Director should approve soon."
            elif has_rbac_violation:
                text = f"Intern submits and directly authorizes expense payout of ${amount:,}."
            else:
                text = f"Employee submits travel expense receipt (${amount:,}). Manager reviews and approves. Finance Director executes bank reimbursement."
                
        else: # IT Asset Provisioning / General
            if is_ambiguous:
                text = f"Deploy high-performance cloud server {random.choice(VAGUE_WORDS)}. Approvals needed promptly."
            elif has_cycle:
                text = "System Admin deployment requires Security Team signoff. Security Team signoff requires System Admin deployment."
            else:
                text = f"Employee requests access to cloud cluster. IT Manager reviews and grants permissions. System logs audit event."

        sample = {
            "id": f"SYNTH-{i+1:04d}",
            "domain": domain,
            "policy_text": text,
            "ground_truth": {
                "is_ambiguous": is_ambiguous,
                "has_rbac_violation": has_rbac_violation,
                "has_cycle": has_cycle,
                "is_valid": not (is_ambiguous or has_rbac_violation or has_cycle)
            }
        }
        dataset.append(sample)
        
    return dataset

if __name__ == "__main__":
    data = generate_synthetic_dataset(50)
    print(f"Generated {len(data)} synthetic policy samples.")
    print("Sample 1:", json.dumps(data[0], indent=2))
