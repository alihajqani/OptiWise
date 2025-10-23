# ===== IMPORTS & DEPENDENCIES =====
import pandas as pd
import numpy as np
import pulp
from scipy.optimize import linprog 

# ===== CORE BUSINESS LOGIC =====
def _solve_single_sbm(k: int, X: np.ndarray, Y: np.ndarray, exclude_dmu_index: int = None):
    """
    Solve the SBM-VRS model. Can exclude one DMU from the reference set for super-efficiency.
    """
    K, m = X.shape
    _, n = Y.shape
    prob = pulp.LpProblem(f"SBM_DMU_{k+1}", pulp.LpMinimize)

    w = pulp.LpVariable("w", lowBound=0)  # For super-efficiency, w can be > 1
    lambda_vars = [pulp.LpVariable(f"lambda_{j+1}", lowBound=0) for j in range(K)]
    slack_vars = [pulp.LpVariable(f"s_{i+1}", lowBound=0) for i in range(m)]

    prob += w, "Minimize_w"
    x0 = X[k, :]
    prob += (
        w
        + (1.0 / m)
        * pulp.lpSum(
            slack_vars[i] * (1.0 / (x0[i] if x0[i] > 1e-9 else 1e-9)) for i in range(m)
        )
        == 1
    )

    # Define the reference set (all DMUs except the one to exclude)
    reference_set_indices = [j for j in range(K) if j != exclude_dmu_index]

    for i in range(m):
        prob += pulp.lpSum(X[j, i] * lambda_vars[j] for j in reference_set_indices) + slack_vars[i] == X[k, i]

    for r in range(n):
        prob += pulp.lpSum(Y[j, r] * lambda_vars[j] for j in reference_set_indices) >= Y[k, r]

    prob += pulp.lpSum(lambda_vars[j] for j in reference_set_indices) == 1, "VRS_Constraint"

    prob.solve(pulp.PULP_CBC_CMD(msg=False))

    return pulp.value(w)


def run_dea_analysis(df: pd.DataFrame, dmu_column: str, inputs: list, outputs: list):
    required_cols = [dmu_column] + inputs + outputs
    if not all(col in df.columns for col in required_cols):
        raise ValueError("برخی ستون‌ها در دیتافریم یافت نشدند.")
    work_df = df[required_cols].copy()
    work_df[inputs + outputs] = work_df[inputs + outputs].apply(pd.to_numeric, errors="coerce").fillna(0)
    dmu_names = work_df[dmu_column].tolist()
    X = work_df[inputs].values
    Y = work_df[outputs].values
    K = len(dmu_names)
    if K == 0:
        raise ValueError("داده معتبری برای تحلیل وجود ندارد.")

    solver = pulp.PULP_CBC_CMD(msg=False)

    raw_results = []
    for k in range(K):
        # Standard SBM-VRS formulation for each DMU
        prob = pulp.LpProblem(f"SBM_VRS_DMU_{k+1}", pulp.LpMinimize)
        w = pulp.LpVariable("w", 0, 1)
        lambda_vars = [pulp.LpVariable(f"L_{j}", 0) for j in range(K)]
        slacks = [pulp.LpVariable(f"S_{i}", 0) for i in range(len(inputs))]
        prob += w
        x0 = X[k, :]
        prob += (
            w
            + (1 / len(inputs))
            * pulp.lpSum([slacks[i] * (1 / (x0[i] if x0[i] > 0 else 1e-9)) for i in range(len(inputs))])
            == 1
        )
        for i in range(len(inputs)):
            prob += pulp.lpSum([X[j, i] * lambda_vars[j] for j in range(K)]) + slacks[i] == X[k, i]
        for r in range(len(outputs)):
            prob += pulp.lpSum([Y[j, r] * lambda_vars[j] for j in range(K)]) >= Y[k, r]
        prob += pulp.lpSum(lambda_vars) == 1
        prob.solve(solver)

        peers_list = [
            f"{dmu_names[j]} ({lam.varValue:.2f})"
            for j, lam in enumerate(lambda_vars)
            if lam.varValue is not None and lam.varValue > 1e-6
        ]
        raw_results.append(
            {
                "dmu": dmu_names[k],
                "efficiency": w.varValue,
                "slacks": {inputs[i]: slacks[i].varValue for i in range(len(inputs))},
                "peers": ", ".join(peers_list),
            }
        )
    return raw_results


def run_ranking_dea(df: pd.DataFrame, dmu_column: str, inputs: list, outputs: list):
    """
    Calculate super-efficiency scores for ranking all DMUs.
    """
    required_cols = [dmu_column] + inputs + outputs
    if not all(col in df.columns for col in required_cols):
        raise ValueError("برخی ستون‌ها در دیتافریم یافت نشدند.")

    work_df = df[required_cols].copy()
    work_df[inputs + outputs] = work_df[inputs + outputs].apply(pd.to_numeric, errors="coerce").fillna(0)
    dmu_names = work_df[dmu_column].tolist()
    X = work_df[inputs].values
    Y = work_df[outputs].values
    K = len(dmu_names)
    if K == 0:
        raise ValueError("داده معتبری برای تحلیل وجود ندارد.")

    scores = np.zeros(K)
    tol = 1e-6

    # Step 1: Run standard efficiency for all DMUs
    for k in range(K):
        scores[k] = _solve_single_sbm(k, X, Y, exclude_dmu_index=None)

    # Step 2: For efficient DMUs, re-run in super-efficiency mode (exclude DMU from reference)
    efficient_indices = np.where(scores >= 1 - tol)[0]
    for k in efficient_indices:
        scores[k] = _solve_single_sbm(k, X, Y, exclude_dmu_index=k)

    # Step 3: Format results
    results = [{"dmu": dmu_names[k], "score": scores[k]} for k in range(K)]
    return results


def run_hr_dea_analysis(df: pd.DataFrame, dmu_column: str, inputs: list, outputs: list):
    """
    Calculates efficiency scores using the PRIMAL formulation of the input-oriented BCC model.
    This model directly solves for the efficiency score (theta) for each DMU.
    The logic is an exact, production-ready replica of the validated debug script.
    """
    # --- 1. Data Preparation ---
    required_cols = [dmu_column] + inputs + outputs
    if not all(col in df.columns for col in required_cols):
        raise ValueError("برخی ستون‌ها در دیتافریم یافت نشدند.")

    work_df = df[required_cols].copy()
    work_df[inputs + outputs] = work_df[inputs + outputs].apply(pd.to_numeric, errors="coerce").fillna(1e-6)
    for col in inputs + outputs:
        work_df[col] = work_df[col].clip(lower=1e-6)

    dmu_names = work_df[dmu_column].values
    X = work_df[inputs].values   # Shape: (n_dmus, n_inputs)
    Y = work_df[outputs].values  # Shape: (n_dmus, n_outputs)
    
    n_dmus, n_inputs, n_outputs = X.shape[0], X.shape[1], Y.shape[1]

    results = []

    # --- 2. Solve LP for each DMU ---
    for k in range(n_dmus):
        # The variables are [theta, lambda_1, ..., lambda_n_dmus]
        # Total variables: n_dmus + 1

        # Objective: Minimize theta
        c = np.zeros(n_dmus + 1)
        c[0] = 1

        # --- Constraint Matrix Construction (Row-by-Row for fidelity) ---
        A_ub_rows = []
        b_ub_rows = []

        # Input constraints: Sum(lambda_j * X_ij) - theta * X_ik <= 0
        for i in range(n_inputs):
            row = np.concatenate([[-X[k, i]], X[:, i]])
            A_ub_rows.append(row)
            b_ub_rows.append(0)

        # Output constraints: -Sum(lambda_j * Y_rj) <= -Y_rk
        for r in range(n_outputs):
            row = np.concatenate([[0], -Y[:, r]])
            A_ub_rows.append(row)
            b_ub_rows.append(-Y[k, r])
        
        A_ub = np.array(A_ub_rows)
        b_ub = np.array(b_ub_rows)
        
        # Equality constraint: Sum(lambda_j) = 1 (VRS constraint)
        A_eq = np.zeros((1, n_dmus + 1))
        A_eq[0, 1:] = 1
        b_eq = [1]
        
        # Bounds for variables: theta >= 0, lambdas >= 0
        bounds = [(0, None)] * (n_dmus + 1)

        # Solve the linear programming problem
        res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')
        
        score = res.fun if res.success and res.fun is not None else 0.0
        
        results.append({
            'dmu': dmu_names[k],
            'score': score
        })
        
    return results