#!/usr/bin/env python3
"""
DATATHON 2026 - Master EDA Pipeline

Executes all analysis phases in sequence:
  1. Product & Market Dominance (17 charts)
  2. Customer Lifecycle & Acquisition (10 charts)
  3. Operational Friction & Leakage (23 charts)
  4. Financial & Payment Dynamics (15 charts)

Usage:
  source .venv/bin/activate
  python scripts/run_all.py

Output: 65 visualizations in output/figures_living/
"""

import os
import sys
import subprocess
from pathlib import Path

# Color codes for output
GREEN = '\033[92m'
BLUE = '\033[94m'
RED = '\033[91m'
RESET = '\033[0m'
BOLD = '\033[1m'

def run_phase(phase_num, phase_name, script_path):
    """Execute a single phase script."""
    print(f"\n{BLUE}{'='*80}{RESET}")
    print(f"{BOLD}[{phase_num}/4] {phase_name}{RESET}")
    print(f"{BLUE}{'='*80}{RESET}")
    
    if not os.path.exists(script_path):
        print(f"{RED}✗ Script not found: {script_path}{RESET}")
        return False
    
    try:
        result = subprocess.run(
            ['python', script_path],
            cwd=os.path.dirname(os.path.abspath(__file__)) + '/..',
            capture_output=False
        )
        
        if result.returncode == 0:
            print(f"{GREEN}✓ {phase_name} completed successfully{RESET}")
            return True
        else:
            print(f"{RED}✗ {phase_name} failed with return code {result.returncode}{RESET}")
            return False
    except Exception as e:
        print(f"{RED}✗ Error running {phase_name}: {str(e)}{RESET}")
        return False

def main():
    """Master pipeline execution."""
    project_root = Path(__file__).parent.parent
    scripts_dir = project_root / 'scripts'
    
    print(f"\n{BOLD}{BLUE}DATATHON 2026 - MASTER EDA PIPELINE{RESET}")
    print(f"Project Root: {project_root}")
    print(f"Scripts Dir: {scripts_dir}\n")
    
    # Define phases
    phases = [
        (1, "Product & Market Dominance (01)", "scripts/product_market/generate_enhanced_figures.py"),
        (2, "Customer Lifecycle & Acquisition (02)", "scripts/part2_eda/cohort_analysis.py"),
        (3, "Operational Friction & Leakage (03)", "scripts/part2_eda/visualize_operational_friction.py"),
        (4, "Financial & Payment Dynamics (04)", "scripts/financial_payment/generate_enhanced_figures.py"),
    ]
    
    results = []
    
    # Execute all phases
    for phase_num, phase_name, script_path in phases:
        success = run_phase(phase_num, phase_name, str(project_root / script_path))
        results.append((phase_name, success))
    
    # Summary
    print(f"\n{BLUE}{'='*80}{RESET}")
    print(f"{BOLD}PIPELINE SUMMARY{RESET}")
    print(f"{BLUE}{'='*80}{RESET}\n")
    
    for phase_name, success in results:
        status = f"{GREEN}✓ PASSED{RESET}" if success else f"{RED}✗ FAILED{RESET}"
        print(f"{status} - {phase_name}")
    
    total_passed = sum(1 for _, success in results if success)
    total_phases = len(results)
    
    print(f"\nResult: {GREEN}{total_passed}/{total_phases} phases completed{RESET}\n")
    
    if total_passed == total_phases:
        print(f"{GREEN}{BOLD}✓ ALL PHASES COMPLETED SUCCESSFULLY!{RESET}")
        print(f"\nOutput Location: output/figures_living/")
        print(f"  • 01_product_market_dominance/ (17 charts)")
        print(f"  • 02_customer_lifecycle_acquisition/ (10 charts)")
        print(f"  • 03_operational_friction_leakage/ (23 charts)")
        print(f"  • 04_financial_payment_dynamics/ (15 charts)")
        print(f"\nTotal: 65 visualizations generated\n")
        return 0
    else:
        print(f"{RED}{BOLD}⚠ Some phases failed. Review output above.{RESET}\n")
        return 1

if __name__ == '__main__':
    sys.exit(main())
