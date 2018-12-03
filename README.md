# GraphDrawer
Trabajo práctico final para Complementos Matemáticos I, Paoloni Gianfranco, FCEIA UNR

Para correr los casos de prueba:
    1) clonar repositorio a una ubicación donde esté instalado GNUPlot (python) ya que se utiliza el mismo para dibujar los grafos
    2) copiar "graph_drawer" a la carpeta /bin
    3) dar pemisos de ejecución ($ sudo chmod -x graph_plotter.py)
    4) correr test.py ($ python test.py)

Para correr casos de prueba alternativos basta con llamar, desde una ubicación con GNUPlot, al archivo graph_plotter:
    $ python graph_ploter "arg_file" (donde "arg_file" es un archivo que contiene un grafo en formato de lista, al igual que los ejemplos en Tests)
