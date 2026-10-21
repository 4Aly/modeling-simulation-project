# Queueing Systems | Modeling & Simulation

Explore how arrivals, service times, and server assignment shape a queue. This project provides an interactive desktop simulator for two queueing tasks, with editable probability distributions, customer schedules, performance statistics, and visualizations.

## Tasks

### Task 1 — Single-server queue

Model customers arriving at and receiving service from one server.

- Set the number of customers.
- Edit the inter-arrival-time and service-time probability distributions.
- View generated random values, arrival and service times, the customer schedule, and queue statistics.
- Visualize the number of customers in the system over time, **Q(t)**.

### Task 2 — Multiple-server queue

Model a shared arrival stream served by multiple servers, each with its own service-time distribution.

- Set the customer count and number of servers.
- Edit one shared inter-arrival distribution and a separate service-time distribution for each server.
- Configure each server's priority when **Highest Priority** is selected. Lower numbers mean higher priority.
- Choose how an arriving customer is assigned:
  - **Highest Priority** — choose the available candidate with the highest configured priority.
  - **Random** — choose randomly among the candidates.
  - **Least Utilization** — choose the candidate with the lowest accumulated utilization.
- Review the generated values and customer schedule, including assigned server and time in queue.
- Compare average service time, idle probability, and utilization for each server.
- View **Q(t)** and a busy/idle timeline for every server.

> **Stopping condition:** Task 2 currently runs for the entered number of customers. The **Time** option changes the input label, but time-based stopping is not yet implemented.

## How a Task 2 run works

1. Customers arrive according to the shared inter-arrival distribution.
2. At each arrival, idle servers are considered first. If all servers are busy, the candidates are the server or servers that become available soonest.
3. The selected server's own service-time distribution determines the customer's service duration.
4. The simulation calculates the schedule and statistics, then updates the charts.

## Task 2 statistics

| Measure | Calculation |
| --- | --- |
| Average waiting time | Total customer waiting time / number of customers |
| Probability a customer waited | Customers with positive waiting time / number of customers |
| Average service time, per server | Server's total service time / customers served by that server |
| Idle probability, per server | Server's total idle time / total simulation run time |
| Utilization, per server | Server's total time handling calls / total simulation run time |

## Default Task 2 distributions

| Distribution | Time values | Probabilities |
| --- | --- | --- |
| Inter-arrival | 1, 2, 3, 4 | 0.25, 0.40, 0.20, 0.15 |
| Server 1 service | 2, 3, 4, 5 | 0.30, 0.28, 0.25, 0.17 |
| Server 2 service | 3, 4, 5, 6 | 0.35, 0.25, 0.20, 0.20 |
