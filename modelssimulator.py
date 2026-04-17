import math
import random

def simulate_performance(d_f, eps, L, d_p):
    # Dummy ML-based predictions (mocking U-Net/CFD)
    alpha = 1 - eps
    
    # Interception parameter
    R = d_p / d_f if d_f > 0 else 0
    
    # Kuwabara number
    Ku = -0.5 * math.log(alpha) - 0.75 + alpha - 0.25 * (alpha ** 2) if alpha < 1 and alpha > 0 else 0.1
    Ku = max(0.001, Ku)
    
    eta = (2.0 * (1 + R) / Ku) * math.log(1 + R) if Ku > 0 else 0
    eta = min(1.0, max(0.001, eta * 0.1))
    
    # Efficiency E
    E_exp = 4 * alpha * eta * L / (math.pi * d_f * (1 - alpha)) if d_f > 0 and (1-alpha) > 0 else 0
    E = 1 - math.exp(-E_exp)
    E = min(0.999999, max(0.0, E))
    
    # Pressure drop dP 
    velocity = 0.05 
    viscosity = 1.81e-5
    dP = 64 * viscosity * velocity * alpha * L / (d_f**2) if d_f > 0 else 1000
    dP = min(10000, max(1, dP))
    
    # Quality factor
    QF = -math.log(1 - E) / dP if E < 1 else 0
    
    return {
        "efficiency": E,
        "pressure_drop": dP,
        "quality_factor": QF,
        "exit_dust_conc": 100 * (1 - E)  # Dummy target input conc = 100mg
    }

def calculate_costs(param, performance):
    Q = param.get("Q", 50.0) 
    eta_fan = param.get("eta_fan", 0.7)
    T = param.get("T", 8000) 
    unit_elec = param.get("unit_elec", 20.0)
    
    dP = performance["pressure_drop"]
    
    # C_energy
    power_kw = (Q / 60.0 * dP) / eta_fan / 1000.0
    c_energy = power_kw * T * unit_elec
    
    # pulse cost
    n_pulses = param.get("n_pulses", 1000)
    v_p = param.get("v_p", 0.1)
    unit_air = param.get("unit_air", 2.0)
    c_pulse = n_pulses * v_p * unit_air
    
    # Product price
    product_price = param.get("product_price", 100000)
    exchange_rate = 1.0 # 1 per year
    
    c_product = product_price * exchange_rate
    maint_cost = 20000
    
    tc = c_product + c_energy + c_pulse + maint_cost
    
    return {
        "energy_cost": c_energy,
        "pulse_cost": c_pulse,
        "product_cost": c_product,
        "maint_cost": maint_cost,
        "total_cost": tc
    }

def optimize_params(target_efficiency):
    best_cost = float('inf')
    best_params = {}
    best_perf = {}
    
    base_cost_param = {
        "Q": 50.0, "eta_fan": 0.7, "T": 8000, "unit_elec": 20.0,
        "n_pulses": 1000, "v_p": 0.1, "unit_air": 2.0, "product_price": 50000
    }
    
    for _ in range(500):
        df = random.uniform(5e-6, 20e-6)
        eps = random.uniform(0.8, 0.95)
        L = random.uniform(0.001, 0.005)
        dp = 1e-6 
        
        perf = simulate_performance(df, eps, L, dp)
        if perf["efficiency"] >= target_efficiency:
            costs = calculate_costs(base_cost_param, perf)
            if costs["total_cost"] < best_cost:
                best_cost = costs["total_cost"]
                best_params = {"d_f": df, "eps": eps, "L": L}
                best_perf = perf
                
    if best_cost == float('inf'):
        best_params = {"d_f": 10e-6, "eps": 0.9, "L": 0.002}
        best_perf = simulate_performance(10e-6, 0.9, 0.002, 1e-6)
        best_cost = calculate_costs(base_cost_param, best_perf)["total_cost"]
        
    return {
        "optimized_params": best_params,
        "predicted_performance": best_perf,
        "predicted_cost": best_cost
    }
