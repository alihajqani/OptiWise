import pandas as pd
import numpy as np
import pulp


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