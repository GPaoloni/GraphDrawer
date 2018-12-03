#! /usr/bin/python

# Trabajo final Complementos Matematicos 1, Paoloni Gianfranco

import argparse
import time
from random import randint
from Gnuplot import Gnuplot
from math import sqrt

# Constants
Gplot = Gnuplot()
SZ = 150          # frame width and length


# Classes we'll use for modeling a graph
class vector:
    '''Representation of a 2d vector'''
    def __init__(self, x, y):
        self.__x, self.__y = x, y

    def __add__(self, v):                                       #vector addition
        assert isinstance(v, vector), "Not a vector"
        return vector(self.__x + v.x(), self.__y + v.y())
    def __sub__(self, v):                                       #vector substraction
        assert isinstance(v, vector), "Not a vector"
        return vector(self.__x - v.x(), self.__y - v.y())
    def __mul__(self, a):                                       #scalar product
        return vector(self.__x * a, self.__y * a)
    def __div__(self, a):                                       #division by scalar
        return vector(self.__x / a, self.__y / a)
    def x(self):
        return self.__x
    def y(self):
        return self.__y
    def reposition(self, x, y):
        self.__x, self.__y = x, y
    def modulus(self):
        return sqrt(self.__x**2 + self.__y**2)

class vertex:
    '''Representation of a vertex
       (x,y) is the position of vertex in the screen
       It should be repositioned through "reposition" method 
    '''
    def __init__(self, name, x=0, y=0):
        self.__name = name
        self.__pos = vector(x, y)
        self.__degree = 0                                                       # degree (count of neighbors)

    def __str__(self):
        return '{name} at ({x}, {y})'.format(name=self.__name, x=self.__pos.x(), y=self.__pos.y())

    def name(self):
        return self.__name

    def position(self):
        #This method returns a new object so the only way to reposition is through the propper method
        return vector(self.__pos.x(), self.__pos.y())

    def reposition(self, x, y):
        self.__pos.reposition(x, y)
    
    def increase_degree(self):
        self.__degree += 1

    def degree(self):
        return self.__degree

    def pos_for_draw(self):
        '''Returns position ready to be concat with Gnuplot-style string'''
        return '{x},{y}'.format(x=self.__pos.x(), y=self.__pos.y())

class LayoutGraph:
    '''Representation of a graph
        V is a set of vertex (vertices)
        E is a set of pairs of verteices
        If (u,v) is added to E, u and v will be added to V (if not present)
        If both (u,v) and (v,u) are in E, both will overlap so only one will be visible
        The functions used for update the positions of vertices, are defined as graph methods
    '''
    def __init__(self, path, iters=1000, refresh=10, c1=1, c2=1, verbose=False):
        #assert isinstance(V, set) and isinstance(E, set), "Error in parameters"     #minimal check
        self.V, self.E = set(), set()
        (V, E) = graph_file_to_list(path)
        for v in V:
            self.add_vertex(vertex(v, randint(5, SZ-5), randint(5, SZ-5)))          #randomize positions)
        for e in E:
            self.add_edge(e)
        #(self.V, self.E) = (V, E)
        self.t = float(SZ / 10)                                                     #initial temperature
        self.eps = 0.00000000001                                                    #prevents div by zero
        self.iters = iters                                                          #iters to be done
        self.refresh = refresh                                                      #refresh rate
        self.c1 = c1                                                                #repulsion const
        self.c2 = c2                                                                #atraction const

    def __str__(self):
        return "V: " + str([v.name() for v in self.V]) + '\n' \
             + "E: " + str([(u.name(), v.name()) for (u,v) in self.E])

    def __contains__(self, w):
        if isinstance(w, vertex):
            for v in self.V:
                #returns true even if we say that the vertex is in another position
                if v.name() == w.name():
                    return True
        else:
            for v in self.V:
                #returns true even if we say that the vertex is in another position
                if v.name() == w:
                    return True
        return False

    def unstable(self):
        self.iters -= 1
        return (self.t > 0.01) and self.iters

    def add_vertex(self, v):
        '''Takes vertex name or object and adds it to graph'''
        if v not in self:
            if isinstance(v, vertex):
                self.V.add(v)
            else:
                self.V.add(vertex(v))

    def add_edge(self, e):
        '''Takes a pair of vertices names and
           adds the edge as vertex objects pair'''      #Takes str pair for simplicity, as edges came in a list of strings
        (u, v) = e
        #if u not in self.names():                      #This slows down performance, but avoid lots of runtime errors
        if u not in self:                               #This slows down performance, but avoid lots of runtime errors
            self.add_vertex(vertex(u))
        #if v not in self.names():                      #Same as above
        if v not in self:                               #Same as above
            self.add_vertex(vertex(v))
        u_ = self.get_vertex(u)
        v_ = self.get_vertex(v)
        self.E.add((u_, v_))
        u_.increase_degree()
        v_.increase_degree()

    def cardinal(self):
        return len(self.V)

    def names(self):
        for v in self.V:
            yield v.name()

    def get_vertex(self, a):
        '''Takes the name of a vertex
           and returns the vertex object'''
        for v in self.V:
            if v.name() == a:
                return v
        raise Exception("Vertex not in graph")

#    Not in use
#    def distance(self, u, v):
#        '''Takes a pair of vertices
#           and returns its distance'''
#        # We are using the vector method using u.pos() method to make things clear
#        return (u.position() - v.position()).modulus()

    def vertices_positions(self):
        '''yields positions as strings, ready to be ploted with Gnuplot'''
        for v in self.V:
            yield v.pos_for_draw()

    def edges_positions(self):
        '''yields starting and ending positions of edges, ready to be ploted with Gnuplot'''
        for (u, v) in self.E:
            yield (u.pos_for_draw(), v.pos_for_draw())

    # Repulsion
    def Fr(self, x):
        return self.c1 * (self.k / x)

    # Atraction
    def Fa(self, x):
        return self.c2 * (x**2 / self.k**2)

    # Central gravity
    def Fc(self, x):
        return x / self.k**2

    def step(self):
        rage = 1
        for v in self.V:
            if v.degree() < 3:
                rage += 0.2
        self.k = (self.cardinal() / min((rage**2), 3.5)) * sqrt(SZ / (self.cardinal() or 1))        #experimental
#        self.k = (self.cardinal() / float(2.6)) * sqrt(SZ / (self.cardinal() or 1))                #safe one
        disp = {}
        
        # Repulsion forces
        for v in self.V:
            disp[v.name()] = vector(0, 0)
            # Repulsion between vertices
            for u in self.V:
                if v != u:
                    delta = v.position() - u.position()
                    d = max(delta.modulus(), self.eps)
                    disp[v.name()] += (delta/d) * self.Fr(d)
            
        # Atraction forces
        for (u, v) in self.E:
            delta = u.position() - v.position()
            d = max(delta.modulus(), self.eps)
            disp[u.name()] -= (delta/d) * self.Fa(d)
            disp[v.name()] += (delta/d) * self.Fa(d)

        # Central gravity force
        for v in self.V:
            delta = vector(SZ/2, SZ/2) - v.position()
            d = max(delta.modulus(), self.eps)
            disp[v.name()] += (delta/d) * self.Fc(d)
            
        # Recalculate positions for vertices
        for v in self.V:
            pos = v.position()
            delta = disp[v.name()]
            d = max(delta.modulus(), self.eps)
            pos += (delta/d) * min(self.t, d)
            v.reposition(max(5, min(SZ-5, pos.x())), max(5, min(SZ-5, pos.y())))

            # Reheat if graph is ugly (this is almost unnecesary, but helps sometimes when the graph spawns horribly)
            if (pos.x() <= 5 or pos.x() >= SZ-5):
                self.t *= 1.03
            if (pos.y() <= 5 or pos.y() >= SZ-5):
                self.t *= 1.03

        # Cool graph
        self.t /= 1.01
        #End draw if cant balance
        if self.t > 1000:
            self.t = 0
        print self.t

    # Plotting utilities
    def first_plot(self):
        ''' Initial plot of the graph'''
        Gplot('set title "Graph drawer')
        Gplot('set xrange [0: {sz}]; set yrange [0: {sz}]'.format(sz = SZ + 5))             # Leave margin of 5
        for pos in self.vertices_positions():
            Gplot('set object circle center {0} size 1 fillcolor rgb "blue" fillstyle solid'.format(pos))
        for (u_pos, v_pos) in self.edges_positions():
            Gplot('set arrow nohead from {0} to {1}'.format(u_pos, v_pos))
        Gplot('plot NaN')
    
    def replot(self):
        ''' Clear screen and replots'''
        Gplot('clear')
        Gplot('reset')
        Gplot('set title "Graph drawer')
        Gplot('set xrange [0: {sz}]; set yrange [0: {sz}]'.format(sz = SZ + 5))             # Leave margin of 5
        for pos in self.vertices_positions():
            Gplot('set object circle center {0} size 1 fillcolor rgb "blue" fillstyle solid'.format(pos))
        for (u_pos, v_pos) in self.edges_positions():
            Gplot('set arrow nohead from {0} to {1}'.format(u_pos, v_pos))
        Gplot('replot')

    def layout(self):
        self.first_plot()
        count = 0
        while (self.unstable()):
            self.step()
            count += 1
            if (not (count % self.refresh)):
                self.replot()
                time.sleep(0.1)
        time.sleep(5)


# Input handlers
def graph_file_to_list(file_path):
    '''
    Lee un grafo desde un archivo y devuelve su representacion como lista.
    Ejemplo Entrada: 
        3
        A
        B
        C
        A B
        B C
        C B
    Ejemplo retorno: 
        (['A','B','C'],[('A','B'),('B','C'),('C','B')])
    '''
    (vertices, edges) = ([], [])
    with open(file_path) as f:
        n = int(f.readline())
        for x in xrange(n):
            vertices.append((f.readline())[:-1])
        for line in f:
            if line[-1] == '\n':
                edge = (line[:-1]).split()
            else: 
                edge = line.split()
            if len(edge) == 2 and (edge[0] in vertices and edge[1] in vertices):    
                edges.append((edge[0], edge[1]))    
    return (vertices, edges)

#def init_graph(path):
#    '''Takes graph in list form and returns graph object ready to be plotted'''
#    (V, E) = 
#    G = graph(V, E)
#    return G


#def plot(path):
#    G = init_graph(path)
#    G.plot()

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-v', '--verbose', 
                        action='store_true', 
                        help='Muestra mas informacion')
    # Iterations to be done
    parser.add_argument('--iters', type=int, 
                        help='Cantidad de iteraciones a efectuar', 
                        default=1000)
    # Iterations until draw is refreshed
    parser.add_argument('--refresh', type=int, 
                        help='Cantidad de iteraciones hasta que refresque pantalla', 
                        default=10)
    # Source file (containing graph in list form)
    parser.add_argument('file_name', 
                        help='Archivo del cual leer el grafo a dibujar')

    args = parser.parse_args()

    layout_gr = LayoutGraph(
        path=args.file_name,
        iters=args.iters,
        refresh=args.refresh,
        #c1=1,
        #c2=1,
        verbose=args.verbose
        )
    
    layout_gr.layout()
    return

if __name__ == "__main__":
    main()
