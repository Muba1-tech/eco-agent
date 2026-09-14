"""
EcoAgent Single-Command Launcher
Runs index validation and launches the Streamlit Enterprise Dashboard.
"""

import os
import sys
import subprocess

# Prevent Windows OpenMP conflicts & encoding errors
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
os.environ["PYTHONIOENCODING"] = "utf-8"

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def main():
    print("================================================================")
    print(" [EcoAgent] Agentic AI Sustainability Advisor")
    print(" Built for 1M1B AI for Sustainability / AICTE / IBM SkillsBuild")
    print("================================================================")
    print("\n[1/2] Verifying Hybrid RAG Index (FAISS + BM25)...")
    
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    faiss_path = os.path.join(data_dir, "faiss_index.bin")
    
    if not os.path.exists(faiss_path):
        print(" -> Index missing. Building index now...")
        res = subprocess.run([sys.executable, "build_index.py"], check=True)
        if res.returncode != 0:
            print("❌ Index building failed.")
            sys.exit(1)
    else:
        print(" -> RAG Index verified successfully.")

    print("\n[2/2] Launching Streamlit Web Application...")
    print(" -> Server URL: http://localhost:8501")
    print(" -> Press Ctrl+C in terminal to stop the server.")
    print("================================================\n")

    # Launch Streamlit app with high-performance flags
    cmd = [
        sys.executable, "-m", "streamlit", "run", "app.py",
        "--server.headless=true",
        "--global.developmentMode=false",
        "--client.toolbarMode=viewer"
    ]
    subprocess.run(cmd)


if __name__ == "__main__":
    main()
