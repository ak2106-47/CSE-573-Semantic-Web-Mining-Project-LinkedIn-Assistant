# test_real_data.py (in same folder as previous test)
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

# If you don't have a data/loader.py, skip to Plan B below
try:
    from data.loader import load_jobs
    jobs = load_jobs()[:3]
    
    print("First 3 jobs from actual dataset:\n")
    for i, job in enumerate(jobs, 1):
        print(f"\nJob {i}:")
        print(f"Title: {job.get('title')}")
        print(f"Description preview: {job.get('description', '')[:200]}...")
        print(f"Raw text preview: {job.get('raw_text', '')[:200]}...")
        
except ImportError:
    print("No data/loader.py found - see Plan B below")
