import time
import random
import copy
import heap_module as hm
import graph as gm
import math

car_id = 1

CONNECTIVITY = 6
TRAFFIC_MULTIPLIER = 8

class Car:
    def __init__(self, source=None, dest=None):
        global car_id
        self.id = car_id

        # Where the car is instantiated
        self.source = source

        # The car's final destination
        self.dest = dest

        # The last node the car was at
        self.current_node = source

        # The node the car is traveling to currently;
        # if the car is at a junction waiting for 
        # routing info, then self.next_node = None
        self.next_node = None

        # The car's progress on the current road
        self.progress = 0

        # The total progress required to complete this road
        self.road_cost = None

        # The total time this car has been traveling
        # since instantation
        self.time_elapsed = 0

        self.fixed_route = []

        car_id += 1

    def __str__(self):
        s = 'CAR ' + str(self.id) + '| Start: ' + str(self.source)
        s += ',  ' + 'Dest: ' + str(self.dest)
        s += ',  ' + str(self.current_node)
        s += '->' + str(self.next_node)
        s += ',  ' + str(self.progress) + '/'
        s += str(self.road_cost)
        s += '. Time Elapsed: ' + str(self.time_elapsed)
        return s

def get_zero_traffic_cost_map(graph, road_cost_map):
    '''
    Construct a weighted graph using the road_cost_map by evaluating
    each of the lambda functions at 0, corresponding to no traffic
    '''
    zero_traffic_cost_map = {}
    for node in graph:
        zero_traffic_cost_map[node] = {}
        for dest in graph[node].keys():
            zero_traffic_cost_map[node][dest] = road_cost_map[node][dest](0)

    return zero_traffic_cost_map

def get_grid_graph(n):
    '''
    Construct a grid graph using graph.py
    '''
    nodes = gm.generateGraph(n, int(math.sqrt(n)) + 4, int(math.sqrt(n)) + 4, CONNECTIVITY)
    return convert_graph(gm.get_graph_representation(nodes))

def convert_graph(version):
    '''
    Convert graph made using graph.py into a road_cost_map
    '''
    graph = {}
    road_cost_map = {}

    nodes = version.keys()
    for node in nodes:
        graph[node] = {}
        road_cost_map[node] = {}
        for terminus in version[node]:
            graph[node][terminus] = 0
            cost = version[node][terminus]
            road_cost_map[node][terminus] = lambda n, cost=cost: TRAFFIC_MULTIPLIER*n + cost

    spawn_probability = {x: random.random() for x in nodes}

    return graph, road_cost_map, spawn_probability

def dijkstra(graph, start):
    '''
    Perform Dijkstra's algorithm from a single start node,
    returning the distances from the start to each other node 
    as well as the predecessor map.

    This function uses the priority queue from our heap_module
    in order to reduce complexity from O(V^2) to O(Elog(V)), which is
    beneficial for sparse graphs. 
    '''
    distances = {start: 0}

    # After this algorithm, pred[node] = x will mean that if you
    # want to go from start to node, then an optimal path involves going
    # to x first.
    pred = {start: None}
    for terminus in graph[start].keys():
        # Seed the pred map
        pred[terminus] = start

    value = {}
    heap = []

    for v in graph.keys():
        value[v] = float('inf')
        heap.append(v)

    hm.changeValue(heap, start, 0, value)

    while (len(heap) > 0):
        # Using the heap, min extraction takes log(V) time
        smallest = hm.extractMin(heap, value)
        distances[smallest] = value[smallest]

        for terminus in graph[smallest].keys():
            if terminus in heap:
                newDist = value[smallest] + graph[smallest][terminus]
                if newDist < value[terminus]:
                    hm.changeValue(heap, terminus, newDist, value)
                    pred[terminus] = smallest

    return distances, pred

def avg(li):
    return sum(li) / float(len(li))

def dijkstra_add_routes(graph, start, routing_table):
    '''
    Augment the given routing_table with a dictionary routing_table[start],
    such that for all other nodes dest, routing_table[start][dest] contains
    the next hop for a car currently at start with destination dest.
    '''

    # We use the predecessor map from Dijkstra's to retrieve shortest paths
    _, pred = dijkstra(graph, start)

    routing_table[start] = {}
    for node in graph:
        if node == start:
            continue
        curr_node = node

        # Trace backwards using the predecessor map until you find the first hop
        if curr_node not in pred:
            routing_table[start][node] = None
            continue
        while pred[curr_node] != start:
            curr_node = pred[curr_node]

        routing_table[start][node] = curr_node

def gen_routing_table(graph, starts_set):
    '''
    Generate a routing table for a given starts_set.

    starts_set contains a list of nodes in the graph that need to be 
    routed from; e.g. x is in starts_set if a car is at the junction x
    and needs to know where its next hop is.
    '''
    routing_table = {}
    for node in starts_set:
        dijkstra_add_routes(graph, node, routing_table)

    return routing_table

def gen_route(routing_table, start, dest):
    route = []
    curr_node = start
    while dest in routing_table[curr_node] and routing_table[curr_node][dest] != None:
        route.append(curr_node)
        curr_node = routing_table[curr_node][dest]

    route.pop(0)
    route.append(dest)

    return route

def print_cars(cars):
    print '################## CARS ##################'
    for car in cars:
        print car
    print '##########################################'
    print ''

def evaluate(arrived_cars):
    '''
    Calculate the average travel time for a list of cars that
    have arrived at their destinations.
    '''
    sum_elapsed = 0
    for car in arrived_cars:
        sum_elapsed += car.time_elapsed

    return sum_elapsed / float(len(arrived_cars))

def one_timestep(graph, road_cost_map, cars, fix_route=False, centralized=False, naive_routing_table=None):
    '''
    Simulate the passage of one unit of time. This involves increment the position
    of each car, labeling the cars that have arrived at their destinations, and
    routing all cars that have arrived at junctions (nodes in the graph).
    '''
    # A list of all junctions where cars are currently waiting
    # for routing information
    starts_set = set([])

    # A list of all cars at junctions that are waiting to be routed
    waiting_cars = []

    # A list of all cars that have arrived at their destination
    arrived_cars = []

    # Will hold all cars that are still traveling after this iteration
    new_car_list = []

    # STEP 1:
    # Increment each car's progress on the road it is on, simulating
    # the passage of a unit of time
    for car in cars:
        # Will update flag if we find out it has arrived
        is_traveling = True
        car.time_elapsed += 1
        if car.next_node:
            # Move car forward one unit along current road
            car.progress += 1

        # If car has reached the end of its current road
        if car.progress >= car.road_cost and car.road_cost != None:
            car.current_node = car.next_node

            # Check whether it has arrived at destination
            if car.current_node == car.dest:
                # To correct one-off error
                car.time_elapsed -= 1
                arrived_cars.append(car)
                is_traveling = False
            else:
                # If the new junction is not the destination,
                # routing from this junction is required
                starts_set.add(car.current_node)
                waiting_cars.append(car)

            car.next_node = None
            car.road_cost = None

        # Handle the special case where the car does not have next_node set,
        # this may occur at the start of the algorithm depending on how you
        # instantiate cars.
        elif not car.next_node:
            waiting_cars.append(car)
            starts_set.add(car.current_node)

        if is_traveling:
            new_car_list.append(car)

    # STEP 2:
    # Figure out how much traffic is on each road
    traffic_graph = copy.deepcopy(graph)
    for car in cars:
        if car.next_node:
            traffic_graph[car.current_node][car.next_node] += 1

    # STEP 3:
    # Use traffic graph to compute new cost of each path
    cost_graph = copy.deepcopy(graph)
    for current_node in cost_graph:
        for next_node in cost_graph[current_node]:
            traffic = traffic_graph[current_node][next_node]
            cost = road_cost_map[current_node][next_node](traffic)
            cost_graph[current_node][next_node] = cost

    # STEP 4
    # Use cost graph to route cars
    if fix_route:
        for car in waiting_cars:
            car.next_node = car.fixed_route[0]
            car.fixed_route.pop(0)
            car.progress = 0
            car.road_cost = cost_graph[car.current_node][car.next_node]

            # Update traffic info for later cars
            traffic_graph[car.current_node][car.next_node] += 1
            new_traffic = traffic_graph[car.current_node][car.next_node]
            new_cost = road_cost_map[car.current_node][car.next_node](new_traffic)
            cost_graph[car.current_node][car.next_node] = new_cost

    else:
        routing_table = None

        if naive_routing_table:
            routing_table = naive_routing_table

        else:
            routing_table = gen_routing_table(cost_graph, starts_set)

        for car in waiting_cars:
            car.next_node = routing_table[car.current_node][car.dest]
            car.progress = 0
            car.road_cost = cost_graph[car.current_node][car.next_node]

            # Update traffic info for later cars
            traffic_graph[car.current_node][car.next_node] += 1
            new_traffic = traffic_graph[car.current_node][car.next_node]
            new_cost = road_cost_map[car.current_node][car.next_node](new_traffic)
            cost_graph[car.current_node][car.next_node] = new_cost

            # If centralized parameter is set to true, we simulate that the 
            # the coordinated driverless cars will know in advance the turns
            # of nearby cars, and will thus have access to up-to-date routing 
            # information based on the near-future behavior of other cars 
            # on the road.
            if centralized:
                routing_table = gen_routing_table(cost_graph, starts_set)

    return new_car_list, arrived_cars

def test(num_total_cars, graph, road_cost_map, spawn_probability, fix_route=False, centralized=False, use_naive=False, printable=False):
    '''
    This function tests the performance of an algorithm (specified by the parameters centralized and use_naive).
    If centralized=False and use_naive=True, this runs Alg0.
    If centralized=False and use_naive=False, this runs Alg1.
    If centralized=True and use_naive=False, this runs Alg2.

    The algorithm runs until num_total_cars have arrived at their destinations.

    Set printable=True if you want to see the location and direction of each car at each time step.
    '''
    nodes = graph.keys()
    zero_traffic_cost_map = get_zero_traffic_cost_map(graph, road_cost_map)
    naive_routing_table = gen_routing_table(zero_traffic_cost_map, nodes)

    cars = []
    i = 0
    arrived = []

    # When the start state and destination state of each node is fixed,
    # they will be equal to special_start and special_dest. They are chosen
    # to make sure that there is a route from special_start to special_dest.
    special_start = None
    special_dest = None
    for node in nodes:
        for terminus in naive_routing_table[node].keys():
            if naive_routing_table[node][terminus] != None:
                special_start = node
                special_dest = terminus

    while len(arrived) < num_total_cars:
        traffic_graph = copy.deepcopy(graph)
        for car in cars:
            if car.next_node:
                traffic_graph[car.current_node][car.next_node] += 1

        cost_graph = copy.deepcopy(graph)
        for current_node in cost_graph:
            for next_node in cost_graph[current_node]:
                traffic = traffic_graph[current_node][next_node]
                cost = road_cost_map[current_node][next_node](traffic)
                cost_graph[current_node][next_node] = cost

        routing_table = gen_routing_table(cost_graph, nodes)


        for node in nodes:
            '''
            if random.random() < spawn_probability[node]:
                dest = random.choice(nodes)
                while dest == node or (naive_routing_table[node][dest]==None):
                    dest = random.choice(nodes)
                new_car = Car(source=node, dest=dest)
                cars.append(new_car)
            '''

            #n = int(random.random() * spawn_probability[node] * 30)

            # Instantiate 4 cars with source=special_start, dest=special_dest
            n = 8 if node==special_start else 0
            for z in range(n):
                dest = special_dest
                counter = 0
                ongoing = True
                #dest = random.choice(nodes)
                while dest == node or (naive_routing_table[node][dest]==None):
                    # It is possible that the chosen start node will not be able to reach
                    # any other node. To skip over these bad start nodes we keep a counter
                    # to keep track of the number of destination nodes we have tried.
                    # When the counter gets too high we abandon this start node choice.
                    if counter > 5:
                        ongoing = False
                        break
                    dest = random.choice(nodes)
                    counter += 1

                if not ongoing:
                    break

                new_car = Car(source=node, dest=dest)
                if fix_route:
                    new_car.fixed_route = gen_route(routing_table, node, dest)

                cars.append(new_car)

        temp_naive = copy.deepcopy(naive_routing_table)
        if not use_naive:
            temp_naive = None
                    
        if printable:
            print_cars(cars)
        cars, arrived_cars = one_timestep(graph, road_cost_map, cars, fix_route=fix_route, centralized=centralized, naive_routing_table=temp_naive)

        arrived += arrived_cars 
        i += 1

    # Just in case more than the required number of cars arrived in the last time step, we truncate the arrived list
    # to the required number.
    arrived = arrived[:num_total_cars]

    if printable:
        print 'ARRIVED CARS:'
        print_cars(arrived)

    avg_elapsed = evaluate(arrived)

    # Return the average travel time of all the cars that have arrived
    return avg_elapsed

#graph, road_cost_map, spawn_probability = get_grid_graph(12)
#zero_traffic_cost_map = get_zero_traffic_cost_map(graph, road_cost_map)

def evaluate_algo(z, fix_route, centralized, use_naive):
    li = []
    print "This trial's result,", "Average of all trials"
    for i in range(z):
        graph, road_cost_map, spawn_probability = get_grid_graph(12)
        avg_delta = test(30, graph, road_cost_map, spawn_probability, fix_route=fix_route, centralized=centralized, use_naive=use_naive, printable=False)
        li.append(avg_delta)
        print str("%.1f" % avg_delta) + ',', "%.1f" % avg(li)

    return avg(li)

def print_divider():
    print ''
    print '###########################################'
    print ''

def main():
    print 'Evaluating naive baseline'
    naive = evaluate_algo(100, False, False, True)
    print_divider()
    print 'Evaluating fixed baseline'
    fixed = evaluate_algo(400, True, False, False)
    print_divider()
    print 'Evaluating dynamic algorithm'
    dynamic = evaluate_algo(400, False, False, False)
    print_divider()
    print 'Evaluating centralized dynamic algorithm'
    centralized = evaluate_algo(400, False, True, False)
    print_divider()

    print 'naive', naive
    print 'fixed', fixed
    print 'dynamic', dynamic
    print 'centralized', centralized

if __name__ == '__main__':
    main()


'''
z = 400
li = []
print "This trial's result,", "Average of all trials"
for i in range(z):
    graph, road_cost_map, spawn_probability = get_grid_graph(12)
    avg_delta = test(30, graph, road_cost_map, spawn_probability, fix_route=True, centralized=False, use_naive=False, printable=False)
    li.append(avg_delta)
    print str("%.1f" % avg_delta) + ',', "%.1f" % avg(li)
'''



