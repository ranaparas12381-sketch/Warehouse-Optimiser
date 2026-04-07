WAREHOUSE INVENTORY OPTIMIZATION ENVIRONMENT

OVERVIEW

This project implements an advanced warehouse inventory optimization system using reinforcement learning and operations research techniques. The environment simulates real world multi SKU logistics operations including demand seasonality, trend analysis, stochastic supplier lead times, capacity constraints, and comprehensive cost optimization.

The system models the core decision making processes found in large scale fulfillment centers similar to those operated by major e commerce platforms. It maintains optimal service levels while minimizing holding costs, stockout penalties, and ordering expenses under uncertain conditions.

TECHNICAL SPECIFICATIONS

Observation Space Configuration

The environment provides the following state observations:

* time_step: Integer representing current day index within the episode range from 0 to maximum episode steps
* inventory_levels: Float array of on hand inventory per SKU normalized by maximum stock capacity range 0 to 1
* pipeline_inventory: Float array of inbound inventory per SKU over near term horizon normalized range 0 to 1
* demand_forecast: Float array of next step demand estimates per SKU normalized range 0 to 1
* days_since_last_order: Integer array tracking days since most recent order for each SKU range 0 to infinity
* capacity_utilization: Float representing fraction of warehouse currently occupied range 0 to infinity

Action Space Configuration

The action space consists of:

* order_quantities: Integer array of non negative replenishment units per SKU to be ordered at current time step

Reward Function Design

The reward function is bounded to the range of negative 1 to positive 1 and calculated as:

R(t) = w1*F(t) - w2*H(t) - w3*S(t) - w4*O(t) - w5*C(t) + w6*E(t)

Component definitions with normalization to signed range:

* F(t): Fulfillment reward calculated as fraction of demand successfully met
* H(t): Holding cost component based on inventory carrying expenses
* S(t): Stockout cost component reflecting unmet demand penalties
* O(t): Order cost component including fixed and variable ordering expenses
* C(t): Capacity violation penalty for exceeding warehouse limits
* E(t): Inventory efficiency bonus for maintaining stock near operational targets

Default weight configuration: w1=0.4, w2=0.15, w3=0.25, w4=0.1, w5=0.05, w6=0.05

State Transition Mechanics

Each simulation step executes the following sequence:

1. Process pending deliveries whose lead times have matured
2. Sample demand per SKU from seasonal trend and stochastic processes
3. Fulfill demand using available inventory with partial fulfillment capability
4. Place new replenishment orders into the pipeline inventory system
5. Calculate holding costs, stockout penalties, and ordering costs
6. Advance the time step counter
7. Compute shaped reward signal
8. Evaluate episode termination conditions

TASK CONFIGURATIONS

The system includes three difficulty levels:

Easy Task: Single SKU Deterministic
* SKU count: 1
* Episode length: 15 steps
* Stochasticity: Disabled
* Challenge: Maintain inventory above reorder point with deterministic demand patterns

Medium Task: Multi SKU Stochastic
* SKU count: 5
* Episode length: 30 steps
* Stochasticity: Enabled
* Challenge: Balance service level against cost under uncertain demand and variable lead times

Hard Task: Full Warehouse Optimization
* SKU count: 10
* Episode length: 60 steps
* Stochasticity: Enabled
* Challenge: Handle demand disruptions, inventory spikes, capacity constraints, and long horizon optimization

GRADING SYSTEM

Each task implements a dedicated grading function returning normalized scores from 0.0 to 1.0:

* Score 0.0: Indicates very poor operational performance with high stockout rates, excessive costs, and inadequate service levels
* Score 1.0: Indicates near optimal performance with excellent service reliability and cost efficiency under task constraints

Easy difficulty emphasizes fulfillment rates and stockout avoidance. Medium difficulty incorporates cost efficiency metrics and stockout frequency analysis. Hard difficulty evaluates discounted cumulative reward, service reliability, inventory turnover quality, and resilience to demand disruptions.

INSTALLATION AND USAGE

Installation Requirements

Install required dependencies using:

pip install -r requirements.txt

Running the Dashboard

Launch the interactive dashboard with:

streamlit run dashboard/app.py

Running Baseline Simulations

Execute baseline policy simulations with:

python -m baseline.run_baseline --task medium --seed 42 --episodes 10

Docker Deployment

Build and run using Docker:

docker build -t warehouse-optimization .
docker run -p 8501:8501 warehouse-optimization

PROJECT ARCHITECTURE

Directory structure:

warehouse_openenv/
  openenv.yaml                     OpenEnv metadata and task definitions
  Dockerfile                       Container configuration for deployment
  requirements.txt                 Python package dependencies
  README.md                        Project documentation
  env/
    __init__.py                    Environment module exports
    warehouse_env.py               Core simulation engine and transition dynamics
    models.py                      Pydantic data models for configuration and state
    reward.py                      Reward calculation and normalization
    utils.py                       Mathematical and signal processing utilities
  tasks/
    __init__.py                    Task registry and configuration
    easy.py                        Single SKU deterministic task parameters
    medium.py                      Multi SKU stochastic task parameters
    hard.py                        Full warehouse optimization parameters
  graders/
    __init__.py                    Grading system registry
    base_grader.py                 Abstract grading interface
    easy_grader.py                 Easy task evaluation logic
    medium_grader.py               Medium task evaluation logic
    hard_grader.py                 Hard task evaluation logic
  baseline/
    __init__.py                    Baseline package exports
    run_baseline.py                Command line interface and heuristic policies
  dashboard/
    app.py                         Streamlit application entry point
    components.py                  Dashboard visualization components

DEPLOYMENT INSTRUCTIONS

For deployment on cloud platforms:

1. Ensure all dependencies are listed in requirements.txt
2. Configure the Dockerfile with appropriate base image and runtime settings
3. Set environment variables for production deployment
4. Configure health check endpoints for container orchestration
5. Deploy using platform specific instructions

The application exposes port 8501 for web interface access. Health monitoring is available at the endpoint /_stcore/health


