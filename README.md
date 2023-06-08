## Guidance
1. Please make sure you have configured aws cli before running "setup.sh"
2. Download the scripts:"setup.sh","deploy.sh" to the same directory and run setup.sh (alternatively you can clone this repository and run "setup.sh"). You should get the same output as "setup.out".
3. If you intend to rerun setup.sh, please ensure that you remove any AWS resources that were created during the previous execution.

## Notes
1. Regarding the implementation presented during the office hour, I had nearly completed my code at that time. However, due to time constraints, I decided to stick with my original code and not to make significant changes, resulting in a slight deviation from Oren's approach.
2. Each endpoint server operates an instance of SQLite to store all the necessary information.
3. Cron jobs are utilized for task scheduling.

## Tests
You can use the "curl" utility as follows:
### PUT
```
curl --location --request PUT 'http://<host_ip>:80/enqueue?buffer=some%20text%20I%20Implemented&Iterations=10'
```
### POST
```
curl --location --request POST 'http://<host_ip>:80/pullCompleted?top=5'
```

## Failure Modes and Mitigation Strategies at Real World Project

A. Machine Failure
1. Scenario: One of the EC2 instances handling the endpoints fails.
2. Mitigation Strategy:Implemention of fault tolerance mechanisms such as load balancing and failover to ensure uninterrupted service.

B. Network Split
1. Scenario: Network connectivity issue between EC2 instances.
2. Mitigation Strategy: we can use Quorum-based consensus algorithms such as Raft and locate our EC2 instances in different availability zones and regions.

C. Worker Node Failure
1. Scenario: One or more worker nodes fail during computation.
2. Mitigation Strategy: Implementation of job monitoring and detection mechanisms to identify failed nodes and in order to mark their assigned tasks available to compute by the other workers.

D. Database Failure
1. Scenario: The database used for storing work items and results experiences a failure or becomes unavailable.
2. Mitigation Strategy: We can use distributed database or database sharding for scalability and fault tolerance.

E. Performance Bottlenecks 
1. Scenario: System becomes overloaded due to high workload or increased user demand on the EC2 instances handling the endpoints. 
2. Mitigation Strategy: horizontal scaling as we have implemented with the workers nodes.


