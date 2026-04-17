from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import models.simulator as sim

app = FastAPI(title="Filter Simulator ML Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SimRequest(BaseModel):
    d_f: float
    eps: float
    L: float
    d_p: float
    # 標準設定値
    Q: float = 50.0
    eta_fan: float = 0.7
    T: float = 8000.0
    unit_elec: float = 20.0
    n_pulses: int = 1000
    v_p: float = 0.1
    unit_air: float = 2.0
    product_price: float = 100000.0

@app.post("/simulate")
def simulate(req: SimRequest):
    perf = sim.simulate_performance(req.d_f, req.eps, req.L, req.d_p)
    cost_params = req.dict()
    costs = sim.calculate_costs(cost_params, perf)
    return {
        "performance": perf,
        "costs": costs
    }

class OptRequest(BaseModel):
    target_efficiency: float

@app.post("/optimize")
def optimize(req: OptRequest):
    return sim.optimize_params(req.target_efficiency)
