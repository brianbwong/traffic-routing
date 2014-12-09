/*
*     Authors: Brian Wong and Kevin Mu
*                  brianwong@college.harvard.edu
*                  kevinmu@college.harvard.edu
*        Date: December 2, 2014
*       Class: Computer Science 143 - Computer Networks 
*     Project: Traffic Routing in the Context of a Centralized Driverless System
*/

-------------------
Overview of files
-------------------

0) README.md
    - A file that describes what you will find in this directory.
1) heap_module.py
    - A file that implements a min-heap to support an O(|E|log|V|) 
      single-source Dijkstra's algorithm.
2) graph.py
    - A file used to randomly generate a graph environment for the
      simulation.
3) main.py
    - The file containing our algorithms' code, as well as code to
      run the algorithms in our simulation environment.
4) traffic-routing.pdf
    - A PDF containing a writeup of our project and documenting 
      our results.


---------------------
Running instructions
---------------------
To replicate our main results, depicted in Figure 1 of our writeup, just run:
    python main.py
    
This will run all 4 algorithms (naive baseline, fixed-route baseline, dynamic route, and 
centralized dynamic route) for 400 trials so that the average values converge. Using the 
current settings we expect you will get approximately the following results:
    Naive baseline:            117.5 (+/- 2.0)
    Fixed-route baseline:      34.1  (+/- 2.0)
    Dynamic route:             30.2  (+/- 2.0)
    Centralized dynamic route: 25.9  (+/- 2.0)

As the simulations run, partial calculations of the average travel time will be printed
to the terminal so that you can see the values converge.
    
On our machine, main.py takes about 8 minutes to run.
