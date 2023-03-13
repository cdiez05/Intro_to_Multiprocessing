#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar  7 13:51:00 2023

@author: carlosdm
"""
from multiprocessing import Process
from multiprocessing import Semaphore, Lock
from multiprocessing import current_process
from multiprocessing import Array, Manager
from random import randint, random
from time import sleep
from numpy import min,max

N = 20
NPROD = 6 
'''
En este caso el tamaño del buffer es 1, es decir, K=1
N = número de vueltas
NPROD = número de productores
'''





def delay(factor = 3):
    sleep(random()/factor)

def producer(almacen, notfull_lst, notempty_lst, valores):
    '''
    Función principal que se encarga de que cada productor produzca elementos y los añada al almacen
    
    Parameters
    ----------
    almacen : [Int]
        Lista de elementos producidos
    notfull_lst : [Lock()]
        Semáforos habitación
    notempty_lst : [SEMAPHORE(0)]

    valores : [Int]
        Últimos valores de los elementos producidos

    Returns
    -------
    None.

    '''
    for i in range(N):
        print (f"Producer {current_process().name} produciendo")
        k = int(current_process().name.split('_')[1])
        notfull_lst[k].acquire()
        producto = valores[k] + randint(0,5)
        #producto = valores[k]
        almacen[k] = producto
        delay()
        notempty_lst[k].release()
        print (f"Productor {current_process().name} ha guardado {producto} en almacen")
        print('Almacén tras producir: ',almacen[:])
    
    k = int(current_process().name.split('_')[1])
    notfull_lst[k].acquire()
    almacen[k] = -1 #indicamos que ha terminado con un -1
    print (f"Producer {current_process().name} ha terminado de producir")
    valores[k] = -1
    notempty_lst[k].release()
    


def consumer_merge(almacen, notfull_lst, notempty_lst,consum_list, valores):
    '''
    Función principal que se encarga de que el consumidor consuma los productos y los añada a una lista final de consumiciones.
    
    Parameters
    ----------
    almacen : [Int]
        Lista de elementos producidos
    notfull_lst : [Lock()]
        Semáforos habitación - de 1 elemento
    notempty_lst : [SEMAPHORE(0)]
    
    consum_list : [Int]
        Lista con los productos consumidos por el consumidor

    valores : [int]
        Últimos valores de los elementos producidos

    Returns
    -------
    None.

    '''
    for i in range(NPROD):
        notempty_lst[i].acquire()
    while max(almacen)!=-1: #de esta forma vemos que hay algún elemento distinto de -1: 
#se va a dejar de cumplir cuando todos los elementos del almacen son -1, es decir, todos han acabado de producir
        min_prod = min(list(filter(lambda n: n!=-1,almacen)))
        indice = list(almacen).index(min_prod)
        print (f"Consumiendo el producto {min_prod} del productor {indice}")
        consum_list.append((min_prod,indice))
        almacen[indice] = -2 #para indicar que hemos consumido el producto
        valores[indice] = min_prod
        print('Almacén tras consumir: ', almacen[:])
        notfull_lst[indice].release()
        notempty_lst[indice].acquire()
        

def main():
    almacen = Array('i', NPROD) #se inicializan todos a -2 porque el almacen empieza vacío (No ha empezado a producir)
    for i in range(NPROD):
        almacen[i] = -2 #indicamos que el almacén de ese productor está vacío; puede producir otro elementos
    print ("Almacén inicial", almacen[:])
    valores = Array('i', NPROD) #se inicializan todos a 0
    notfull_lst = [Lock() for i in range(NPROD)]
    notempty_lst = [Semaphore(0) for i in range(NPROD)]
    man = Manager()
    consum_list = man.list() #lista compartida vacía
    prodlst = [ Process(target=producer,
                        name=f'prod_{i}',
                        args=(almacen, notfull_lst, notempty_lst, valores))
                for i in range(NPROD) ]
    consumidor = Process(target=consumer_merge, name= "consumidor", 
                         args=(almacen, notfull_lst, notempty_lst, consum_list, valores))
    procs = [consumidor] + prodlst
    for p in procs:
        p.start()
    
    for p in procs:
        p.join()
    
    print("\n************************************************************\n")
    print("Almacén final", almacen[:])
    print('\nLista de los productos consumidos expresada de la forma: (product, from_producer)')
    print("Lista de los productos consumidos:", consum_list[:])

if __name__ == '__main__':
    main()
        
        
        