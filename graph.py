# * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
# 
# Author: Brian Wong and Kevin Mu
# Class: Computer Science 143
# Date: December 2, 2014
# Description: A class that creates the graph representation.
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
    
class Node:
    """ class representing a node in the graph"""
    def __init__(self, x, y):
        self.neighbors = []
        self.x = x
        self.y = y

    def setNeighbors(self, neighbors):
        self.neighbors = neighbors
        
    def distance(self, n2):
        distance = (self.x - n2.x)**2 + (self.y - n2.y)**2
        return math.sqrt(distance)
        
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
    nodes.add(Node(0,0))
    nodes.add(Node(height-1, width-1))
    nodes.add(Node(height-2, width-2))
    for i in xrange(n-3):
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
    return nodes

def get_graph_representation(nodes):
    nodes_dict = dict()
    for node in nodes:
        neighbors_dict = dict()
        for neighbor in node.neighbors:
            neighbors_dict[(neighbor.x, neighbor.y)] = node.distance(neighbor)
        nodes_dict[(node.x, node.y)] = neighbors_dict
    return nodes_dict

def main():
    nodes = generateGraph(40, 500, 500, 5)
    get_graph_representation(nodes)
    
if __name__ == '__main__':
    main()

