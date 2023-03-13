#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar  4 21:35:55 2023

@author: carlosdm
"""
from multiprocessing import Process
from multiprocessing import Semaphore, Lock
from multiprocessing import current_process
from multiprocessing import Array,Manager
from random import randint,random
from time import sleep
from numpy import max


N = 30
K = 10
NPROD = 5
TOTAL = K*NPROD
'''
K -> Longitud del buffer
N -> Número de vueltas
NPROD -> Número de productores
'''

def delay(factor = 3):
    sleep(random()/factor)
    
    
def add_data(almacen, ind, last_value, lastprod_pos, mutex):
    '''
    Función que añade los productos al almacén
    '''
    mutex.acquire()
    try:
        r = lastprod_pos[ind]
        product = last_value[ind] + randint(0,5)
        almacen[ind*K+r] = product
        last_value[ind] = product
        lastprod_pos[ind] = lastprod_pos[ind] + 1
    finally:
        mutex.release()
    return product

def primeros_elems(almacen, K):
    '''
    Función auxiliar para coger los elementos que primero se han producido de cada buffer de cada productor
    '''
    lista = []
    for i in range(0,TOTAL, K):
        lista.append(almacen[i])
    return lista

def minimo_producto(almacen, mutex):
    '''
    Función auxiliar que coge el minimo elemento de una lista que sea distinto de -1, que significaría que ha terminado
    '''
    mutex.acquire()
    try:
        min_prod = min(list(filter(lambda n: n!=-1, primeros_elems(almacen, K))))
        #buscamos el mínimo valor de los primeros elementos de cada productor en el almacen que sea distinto de -1 (porque significaría que ya ha terminado - no es un producto)
        indice = list(primeros_elems(almacen, K)).index(min_prod)
    finally:
        mutex.release()
    return min_prod, indice


def get_data(almacen, consum_list, producto, ind, lastprod_pos, mutex):
    '''
    Función que coge los productos del almacén, los consume y los añade a la lista de productos consumidos
    '''
    mutex.acquire()
    try:
        consum_list.append(producto)
        for i in range(ind*K, (ind+1)*K-1):
            almacen[i] = almacen[i + 1]
        almacen[(ind+1)*K-1] = -2
        if almacen[ind*K]==-1:
            for i in range(1,K):
                almacen[ind*K + i] = -1
        lastprod_pos[ind] -= 1
    finally:
        mutex.release()


def finalizar(almacen,index , lastprod_pos, mutex):
    '''
    Función que se encarga de cambiar todos los elementos del buffer de un productor a -1 para indicar que ha terminado
    '''
    mutex.acquire()
    try:
        almacen[index*K + lastprod_pos[index] ] = -1
        if almacen[index*K]==-1:
            for i in range(1,K):
                almacen[index*K + i]=-1
            
    finally:
        mutex.release()
                

        
        
def producer(almacen, notfull_lst, notempty_lst, valores, lastprod_pos, mutex):
    '''
    Función principal que se encarga de que cada productor produzca elementos y los añada al almacen
    
    Parameters
    ----------
    almacen : [Int]
        Lista de elementos producidos
    notfull_lst : [SEMAPHORE(K)]
        Semáforos habitación
    notempty_lst : [SEMAPHORE(0)]

    valores : [Int]
        Últimos valores de los elementos producidos.
    lastprod_pos : [Int]
        Lista con los índices que indican el producto afectado de cada productor.
    mutex : Lock()
        

    Returns
    -------
    None.

    '''
    for i in range (N):
        print (f"Producer {current_process().name} produciendo")
        k = int(current_process().name.split('_')[1])
        notfull_lst[k].acquire()
        prod = add_data(almacen, k, valores, lastprod_pos, mutex)
        delay()
        notempty_lst[k].release()
        print (f"Producer {current_process().name} ha guardado {prod} en almacen")
        print('Almacén tras producir: ',almacen[:])
    
    k = int(current_process().name.split('_')[1])
    notfull_lst[k].acquire()
    finalizar(almacen,k , lastprod_pos, mutex)
    notempty_lst[k].release()  
    
        
        
def consumer_merge(almacen, notfull_lst, notempty_lst, consum_list, lastprod_pos, mutex):
    '''
    Función principal que se encarga de que el consumidor consuma los productos y los añada a una lista final de consumiciones.
    
    Parameters
    ----------
    almacen : [Int]
        Lista de elementos producidos
    notfull_lst : [SEMAPHORE(K)]
        Semáforos habitación - de K elementos
    notempty_lst : [SEMAPHORE(0)]
    
    consum_list : [Int]
        Lista con los productos consumidos por el consumidor

    lastprod_pos : [Int]
        Lista con los índices que indican el producto afectado de cada productor.
    mutex : Lock()
        

    Returns
    -------
    None.

    '''
    
    for i in range(NPROD):
        notempty_lst[i].acquire()
    while max(almacen)!=-1:
        min_prod, ind = minimo_producto(almacen, mutex)
        get_data(almacen, consum_list, min_prod, ind, lastprod_pos, mutex)
        print (f"Consumiendo el producto {min_prod} del productor {ind}")
        print ('Almacen tras consumir: ',almacen[:])
        notfull_lst[ind].release()
        notempty_lst[ind].acquire()
        

def main():
    
    almacen = Array('i', TOTAL)
    for i in range(TOTAL):
        almacen[i] = -2
    print ("Almacen inicial", almacen[:])
    
    valores = Array('i', NPROD)
    # for i in range(NPROD):
    #     valores[i] = randint(0,5)
        
    lastprod_pos = Array('i', NPROD)
    # for i in range(NPROD):
    #     lastprod_pos[i] = 0
    
    man = Manager()
    consum_list = man.list()

    notfull_lst = [Semaphore(K) for i in range(NPROD)]
    notempty_lst = [Semaphore(0) for i in range(NPROD)]
    mutex = Lock()
     
    prodlst = [ Process(target=producer,
                        name=f'prod_{i}',
                        args=(almacen, notfull_lst, notempty_lst, valores, lastprod_pos, mutex))
                for i in range(NPROD) ]

    consumidor = Process(target=consumer_merge, name= "consumidor", 
                         args=(almacen, notfull_lst, notempty_lst, consum_list, lastprod_pos, mutex))
    procs = [consumidor] + prodlst
    for p in procs:
        p.start()
    
    for p in procs:
        p.join()
    
    print("\n************************************************************\n")
    print("Almacén final", almacen[:])
    print("Lista de productos consumidos:", consum_list[:])

if __name__ == '__main__':
    main()