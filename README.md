# Modeling and Simulation Project

A Python desktop application for modeling and simulation coursework. The current GUI contains a Task 1 single-server queue simulation.

## Setup and Run

Run these commands from the project root in PowerShell:

```powershell
py -m pip install -r requirements.txt
py gui/app.py
```

The GUI opens on the main menu. Select **Task 1** to enter the simulation inputs and view its results.

## Project Structure

```text
gui/
  app.py                     Starts the CustomTkinter application
  views/
    mainmenu.py              Main menu and page navigation
    task1.py                 Task 1 controls and result display
simulations/
  task1/
    customer/
      customer.py            Customer data and event times
    server/
      server.py              Server availability and server statistics
    simulation/
      simulation.py          Random generation, scheduling, metrics, and graph
    run.py                   Optional command-line simulation runner
requirements.txt             Third-party Python packages
```

## Task 1 GUI

The Task 1 page lets the user set the number of customers. The server count is fixed at one because the assignment specifies a single-server queue.

Both probability distributions are editable:

- **Inter-arrival distribution:** the default has eight outcomes, each with probability `0.125`.
- **Service-time distribution:** the default probabilities for service times 1 through 6 are `0.10`, `0.20`, `0.30`, `0.25`, `0.10`, and `0.05`.

Use `+` to add an outcome or `-` to remove the last outcome. The probability entries must each be between 0 and 1, and the values in each distribution must add up to 1. Cumulative probabilities update as the entries change.

After **Run simulation**, the page shows the generated random numbers and times, the customer schedule, four performance measures with their calculation values, and a graph of the number of customers in the system, $Q(t)$.

## Simulation Flow

`Simulation` accepts the customer count and the two probability lists:

```python
from simulations.task1.simulation import Simulation

simulation = Simulation(
    num_customers=6,
    interarrival_probabilities=[0.125] * 8,
    service_probabilities=[0.10, 0.20, 0.30, 0.25, 0.10, 0.05],
)
customers = simulation.run()
```

The probability lists are optional; if omitted, the assignment's default distributions are used. The class checks that each list is non-empty, contains probabilities between 0 and 1, and sums to 1.

Each customer receives one random value for inter-arrival generation and one for service-time generation. Values are generated with Python's `random` module and rounded to three decimal places before being mapped through the corresponding cumulative distribution.

For each random value, the simulation selects the first outcome whose cumulative probability is at least that value. Inter-arrival outcome rows represent times 1, 2, 3, and so on. Service-time outcome rows similarly represent service durations 1, 2, 3, and so on.

Customer 1 arrives at clock time 0. The simulation uses the first `num_customers - 1` generated inter-arrival times to calculate the later arrival times. It still displays all generated inter-arrival values, including the last draw that does not determine an arrival in this run.

Customers are served in arrival order. When a customer arrives before the server is free, service begins when the current service ends. The server class records idle time, service time, and how many customers it served.

## Classes and Main Methods

### `Customer`

Defined in `simulations/task1/customer/customer.py`. Each object stores:

- `number`: customer number.
- `interarrival_time`: time since the previous customer arrived; the first customer has `None`.
- `arrival_time`: arrival time on the simulation clock.
- `service_time`: sampled service duration.
- `waiting_time`: time from arrival until service begins.
- `service_begins` and `service_ends`: service start and departure clock times.
- `server_number`: the number of the assigned server, currently always 1.

### `Server`

Defined in `simulations/task1/server/server.py`. `serve_customer(customer)` assigns service start and end times, updates the customer's waiting time, and accumulates server idle and service totals. `calculate_statistics(total_run_time)` calculates idle probability and average service time.

### `Simulation`

Defined in `simulations/task1/simulation/simulation.py`.

- `generate_interarrival_times()` and `generate_service_times()` map random values to distribution outcomes.
- `build_arrival_times()` starts at time 0 and adds inter-arrival times for subsequent customers.
- `create_customers()` creates the Customer objects.
- `run()` schedules every customer on the single server and calculates performance measures. It returns the customer list.
- `create_system_population_graph()` returns a Matplotlib `(figure, axes)` pair after the simulation has run.

The GUI builds its table from `simulation.customers`, displays the random values and generated times, and embeds the returned Matplotlib figure. The simulation code does not print a console table.

## Performance Measures

The Task 1 page displays the result and the values used to calculate it:

- **Average waiting time:** `total_waiting_time / number_of_customers`.
- **Probability a customer waited:** `customers_who_waited / number_of_customers`. A customer counts as having waited when `waiting_time > 0`.
- **Server 1 idle probability:** `total_idle_time / total_run_time`. Total run time ends at the last service completion.
- **Average service time:** `total_service_time / customers_served`.

Overall waiting measures are stored on the Simulation object. Idle-time and service-time totals and averages are stored on the Server object.

## Current Scope

Task 1 currently supports a fixed number of customers per run and exactly one server. It does not yet have a stop-after-time mode or multiple servers. Changing the number of outcomes in a probability distribution changes the available time values: the first row means time 1, the second row means time 2, and so on.
