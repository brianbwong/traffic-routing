# * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
# 
# Author: Kevin Mu
# Class: Computer Science 143
# Date: December 01, 2014
# Title: Final Project
# Description: A vehicular traffic simulator with smart-routing
#
# * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *

from collections import Counter
import numpy as np
from random import randrange
import random
import re
import os
import math
import operator

time = 0
cars_in = 0
cars_out = 0
total_travel_time = 0
cars = set()
nodes = []
links = dict()

class Car:
    def __init__(self, src, dest):
        global cars
        self.src = src
        self.dest = dest
        self.currNode = src
        self.currLink = None
        self.progress = 0
        self.timer = 0
        cars.add(self)
    
    def addToNode(self, node):
        global cars
        global cars_out
        global total_travel_time 
        if node.car is not None:
            return False       
        if self.currLink is not None:
            self.currLink.removeCar(self)        
        if node == self.dest:
            cars_out += 1
            total_travel_time += self.timer
            cars.remove(self)
        else:
            self.currLink = None
            self.currNode = node            
            self.progress = 0            
            self.currNode.car = self
        return True
    
    def addToLink(self, link):
        link.addCar(self)
        self.currLink = link
        self.currNode.car = None
        self.currNode = None
        self.progress = 0
        return True  
        
    def advance(self):
        self.timer += 1
        if self.currLink is None:
            if self.currNode is None:
                return False
            self.currNode.routeCar(time)
            return True
            
        if self.currLink.distance - self.progress < 0.1:
            return self.addToNode(self.currLink.n2)
        else:
            self.progress += self.currLink.getSpeed(time)
            return True

class Link:
    """ class representing a uni-directional link in the graph"""
    def __init__(self, n1, n2):
        self.n1 = n1
        self.n2 = n2
        self.distance= n1.distance(n2)
        self.traffic = Counter()
        self.speedLimit = 3
    
    def getSpeed(self, time):
        return self.speedLimit - 0.5*self.traffic[time]
        
    def getCost(self, time):
        return self.distance / getSpeed(time)
        
    def addCar(self, car):
        self.traffic[time] += 1
        
    def removeCar(self, car):
        self.traffic[time] -= 1
    
class Node:
    """ class representing a node in the graph"""
    def __init__(self, x, y):
        self.neighbors = []
        self.x = x
        self.y = y
        self.car = None
        self.spawnProb = 0.1 + random.random() / 5  #between 0.1 and 0.3 
        self.routingTable = {}

    def setNeighbors(self, neighbors):
        self.neighbors = neighbors
        
    def distance(self, n2):
        distance = (self.x - n2.x)**2 + (self.y - n2.y)**2
        return math.sqrt(distance)
    
    def addLink(self, neighbor):
        link = Link(self, neighbor)
        return link
        
    def routeCar(self, time):
        #nextHopNode = self.routingTable[self.car.dest]
        nextHopNode = random.sample(self.neighbors, 1)[0]
        link = links[(self, nextHopNode)]
        self.car.addToLink(link)
        
    def maybeSpawnCar(self):
        global cars_in
        if self.car is not None:
            return False
        if random.random() < self.spawnProb:
            dest = random.sample(nodes, 1)[0]
            car = Car(self, dest)
            car.addToNode(self)
            cars_in += 1
            return True
            
    def dijkstra_add_routes(self):
        distances = {x: float('inf') for x in nodes}
        distances[self] = 0
        pred = {self: None}
        for terminus in self.neighbors:
            distances[terminus] = self.distance(terminus)
            pred[terminus] = self

        S = [self]
        V = list(set(nodes) - set(S))

        while V:
            closest = V[0]
            closestDist = float('inf')
            for v in V:
                if distances[v] < closestDist:
                    closest = v
                    closestDist = distances[v]
            distances[closest] = closestDist
            V.remove(closest)

            for terminus in closest.neighbors:
                if terminus in V:
                    new_dist = distances[closest] + closest.distance(terminus)
                    if new_dist < distances[terminus]:
                        distances[terminus] = new_dist
                        pred[terminus] = closest
        self.routingTable = {x: pred[x] for x in nodes}
            
# adapted from Machine Learning Mastery, http://bit.ly/1sdD7nG
# helper function for generateGraph.
def getClosestNeighbors(nodes, node, k):
    distances = []
    for x in range(len(nodes)):
        dist = node.distance(nodes[x])
        distances.append((nodes[x], dist))
    distances.sort(key=operator.itemgetter(1))
    neighbors = []
    for x in range(1,k+1): #avoid adding itself to list.
        neighbors.append(distances[x][0])
    return neighbors
    
def generateGraph(n, height, width, k):
    nodes = set()
    links = dict()
    for i in xrange(n):
        node = None
        while node is None or node in nodes:
            x = randrange(0, width)
            y = randrange(0, height)
            node = Node(x, y)
        nodes.add(Node(x, y))

    nodes = list(nodes)
    
    for node in nodes:
        neighbors = getClosestNeighbors(nodes, node, k)
        node.setNeighbors(neighbors)
        for neighbor in neighbors:
            link = node.addLink(neighbor)
            links[(node, neighbor)] = link
            
    return (nodes, links)

def get_graph_representation(nodes):
    nodes_dict = dict()
    for node in nodes:
        neighbors_dict = dict()
        for neighbor in node.neighbors:
            neighbors_dict[(neighbor.x, neighbor.y)] = node.distance(neighbor)
        nodes_dict[(node.x, node.y)] = neighbors_dict
    return nodes_dict

def advance():
    global time
    # spawn new cars
    for node in nodes:
        # node.dijkstra_add_routes()
        node.maybeSpawnCar()
    for car in cars.copy():
        car.advance()
    time += 1

def run(cycles):
    for i in xrange(cycles):
        if i % 10 == 0:
            print "cycle " + str(i)
        advance()
    print 'Summary'
    print 'Final Time                : {}'.format(time)
    print 'No. cars still travelling : {}'.format(cars_in)
    print 'No. cars at destinations  : {}'.format(cars_out)
    print 'Total travel time         : {}'.format(total_travel_time)
    print 'Avg travel time           : {}'.format(total_travel_time / cars_out)
    print '# cars at destinations    : {}'.format(cars_out)
    
def main():
    nodes, links = generateGraph(40, 500, 500, 5)
    get_graph_representation(nodes)
    '''
    global nodes
    global links
    nodes, links = generateGraph(40, 20, 20, 5)
    for n in nodes:
        print "(" + str(n.x) + "," + str(n.y) + ")"
    run(1300)
    for link in links.values():
        print link.getSpeed(time-1)
    '''
    
if __name__ == '__main__':
    main()

