# ===== IMPORTS & DEPENDENCIES =====
import pandas as pd
import numpy as np
import pulp

# ===== CORE LOGIC =====
def _solve_single_sbm(k: int, X: np.ndarray, Y: np.ndarray):
    """
    Solves the Input‐Oriented SBM model for a single DMU with a VRS constraint.
    """
    K, m = X.shape; _, n = Y.shape
    prob = pulp.LpProblem(f"SBM_InputOriented_DMU_{k+1}", pulp.LpMinimize)
    
    # --- Variables ---
    w = pulp.LpVariable("w", lowBound=0, upBound=1)
    lambda_vars = [pulp.LpVariable(f"lambda_{j+1}", lowBound=0) for j in range(K)]
    slack_vars = [pulp.LpVariable(f"s_{i+1}", lowBound=0) for i in range(m)]

    # --- Objective Function ---
    prob += w, "Minimize_w"

    # --- Constraints ---
    x0 = X[k, :]
    prob += w + (1.0 / m) * pulp.lpSum(slack_vars[i] / (x0[i] if x0[i] > 1e-9 else 1e-9) for i in range(m)) == 1
    
    for i in range(m):
        prob += pulp.lpSum(X[j, i] * lambda_vars[j] for j in range(K)) + slack_vars[i] == X[k, i]
    
    for r in range(n):
        prob += pulp.lpSum(Y[j, r] * lambda_vars[j] for j in range(K)) >= Y[k, r]

    # --- CRITICAL FIX: Add the VRS constraint ---
    # This forces the sum of lambdas to equal 1, making the model VRS.
    prob += pulp.lpSum(lambda_vars) == 1, "VRS_Constraint"
    # --- END OF FIX ---

    # --- Solve ---
    prob.solve(pulp.PULP_CBC_CMD(msg=False))

    # --- Retrieve Results ---
    w_star = pulp.value(w)
    lambdas_star = [pulp.value(var) for var in lambda_vars]
    slacks_star = [pulp.value(var) for var in slack_vars]
    
    return w_star, lambdas_star, slacks_star

def run_dea_analysis(df: pd.DataFrame, dmu_column: str, inputs: list, outputs: list):
    """
    Acts as a bridge between the UI and the core DEA solver.
    """
    # 1. Prepare Data
    required_cols = [dmu_column] + inputs + outputs
    if not all(col in df.columns for col in required_cols):
        raise ValueError("برخی ستون‌ها در دیتافریم یافت نشدند.")

    work_df = df[required_cols].copy()
    work_df[inputs + outputs] = work_df[inputs + outputs].apply(pd.to_numeric, errors='coerce').fillna(0)
    dmu_names = work_df[dmu_column].tolist()
    X = work_df[inputs].values
    Y = work_df[outputs].values
    K = len(dmu_names)
    if K == 0: raise ValueError("داده معتبری برای تحلیل وجود ندارد.")

    # 2. Solve for each DMU
    raw_results = [_solve_single_sbm(k, X, Y) for k in range(K)]

    # 3. Format Results
    formatted_results = []
    tol = 1e-6
    for k, (w, lambdas, slacks) in enumerate(raw_results):
        dmu_name = dmu_names[k]
        peers_list = [f"{dmu_names[j]} ({lam:.2f})" for j, lam in enumerate(lambdas) if lam is not None and lam > tol]
        peers_str = ", ".join(peers_list)
        slacks_dict = {inputs[i]: slacks[i] for i in range(len(inputs))}
        
        formatted_results.append({
            'dmu': dmu_name,
            'efficiency': w,
            'slacks': slacks_dict,
            'peers': peers_str
        })
        
    return formatted_results