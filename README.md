/*
* Authors: Brian Wong and Kevin Mu
*             brianwong@college.harvard.edu
*             kevinmu@college.harvard.edu
* Date:    December 10, 2014
* Class:   Computer Science 143 - Computer Networks 
* Project: Traffic Routing in the Context of a Centralized Driverless System
* Description: In this project, we explore whether having a central controller
*              coordinate routing can reduce the average travel time of 
*              vehicles in a graph.
*/

------ --- -- -  -   
Overview
------ --- -- -  - 
The files that should be included in this directory include:

0) README.md
    - A file that describes what you will find in this directory.
1) heapmodule.py
    - A file that implements a min-heap to support an O(|E|log|V|) 
      single-source Dijkstra's algorithm.
2) graph.py
    - A file used to randomly generate a graph environment for the
      simulation.
3) main.py
    - The file containing our algorithms' code, as well as code to
      run each timestep of the simulations.


----- --- -- -  -   
Running instructions
------ --- -- -  - 
To try out a test simulation for yourself, simply run:
    python main.py
    
This will run all 4 algorithms (naive baseline, fixed-route baseline, dynamic route, and 
centralized dynamic route) for 400 trials so that the average values converge. Using the 
current settings we expect you will get approximately the following results:
    Naive baseline:            117.5 (+/- 2.0)
    Fixed-route baseline:      34.1  (+/- 2.0)
    Dynamic route:             30.2  (+/- 2.0)
    Centralized dynamic route: 25.9  (+/- 2.0)
    
On our machine, main.py takes about 6 minutes to run on average.