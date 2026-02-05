import pandas as pd
import numpy as np
import time

# --- 1. CONFIGURATION ---
# The path you provided:
file_path = "/Users/michaelbeaudoin/Downloads/olas-operate-app-main/Categorized_Agent_Bets_Final.xlsx"
n_iterations = 10000                # Number of bootstrap samples
batch_size = 1000                   # Optimize memory usage
alpha = 0.95                        # 95% Confidence Interval

# --- 2. YOUR FUNCTION ---
def run_monotonic_simulation_optimized():
    start_time = time.time()
    print(f"Loading file: {file_path}...")
    print("(This step takes the longest for 500k rows...)")
    
    try:
        # Load all sheets
        # engine='openpyxl' is strictly required for .xlsx files
        all_sheets = pd.read_excel(file_path, sheet_name=None, header=0, engine='openpyxl')
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return
    except Exception as e:
        print(f"Error loading file: {e}")
        return
    
    load_time = time.time()
    print(f"File loaded in {load_time - start_time:.1f} seconds.\n")

    print(f"{'Sheet Name':<30} {'N':<8} {'Sim Flat ROI':<15} {'LB (2.5%)':<10} {'UB (97.5%)':<10} {'Efficacy'}")
    print("-" * 95)

    for sheet_name, df in all_sheets.items():
        try:
            # Load Column H (ROI), Index 7
            # Note: Ensure your Excel actually has ROI in the 8th column (H)
            # If your sheet layout differs, change 'iloc[:, 7]' to the correct index
            roi_data = df.iloc[:, 7].dropna() 
            roi_data = pd.to_numeric(roi_data, errors='coerce').dropna()
            
            # Unit correction (Integer 90 -> 0.90)
            rois = roi_data.values / 100.0
            n_samples = len(rois)
            
            if n_samples < 5: continue

            obs_mean_roi = np.mean(rois)

            # --- OPTIMIZED BATCHED BOOTSTRAP ---
            boot_means = []
            
            # We loop until we have collected n_iterations
            for _ in range(0, n_iterations, batch_size):
                # Current batch size (handles the remainder at the end)
                current_batch = min(batch_size, n_iterations - len(boot_means))
                
                if current_batch <= 0: break
                
                # Create small batch of indices (e.g., 50 x 500,000)
                indices = np.random.randint(0, n_samples, size=(current_batch, n_samples))
                
                # Look up values
                batch_samples = rois[indices]
                
                # Calculate means for this batch and store them
                batch_means = np.mean(batch_samples, axis=1)
                boot_means.extend(batch_means)

            boot_means = np.array(boot_means)
            # -----------------------------------

            lower_ci = np.percentile(boot_means, (1 - alpha) / 2 * 100)
            upper_ci = np.percentile(boot_means, (1 + alpha) / 2 * 100)

            if lower_ci > 0:
                efficacy = "POSITIVE"
            elif upper_ci < 0:
                efficacy = "NEGATIVE"
            else:
                efficacy = "NO EDGE"

            # Truncate sheet name if too long for cleaner printing
            display_name = (sheet_name[:27] + '..') if len(sheet_name) > 27 else sheet_name
            
            print(f"{display_name:<30} {n_samples:<8} {obs_mean_roi:.2%}          {lower_ci:.2%}     {upper_ci:.2%}     {efficacy}")

        except Exception as e:
            # print(f"Error on {sheet_name}: {e}")
            pass

    total_time = time.time() - start_time
    print(f"\nAnalysis complete in {total_time:.1f} seconds.")

# --- 3. EXECUTION ---
if __name__ == "__main__":
    # Ensure you have 'openpyxl' installed: pip install openpyxl
    run_monotonic_simulation_optimized()