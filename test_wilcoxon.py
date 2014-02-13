# -*- coding: utf-8 -*-
"""
Created on Thu Jan 23 14:33:54 2014

@author: Adrián
"""

import math
import scipy as sp
import scipy.stats as st

#Para cuando el tamaño muestral N sea menor o igual a 25, se puede hacer el test de Wilcoxon
#examinando la tabla que nos da los valores críticos (el intervalo) para cada valor de N y
#nivel de significancia (0.10,0.05,0.02,0.01,0.005,0.001) dado. Si tenemos en cuenta que T
#será el valor mínimo de (suma rangos positivos, suma rangos negativos), se utilizan los límites
#inferiores de los intervalos y el contraste será estadísticamente significativo si: T <= límite
#inferior correspondiente.
tabla_wilcoxon = {0.10:{5:0,6:2,7:3,8:5,9:8,10:10,11:13,12:17,13:21,14:25,15:30,16:35,17:41,
                    18:47,19:53,20:60,21:67,22:75,23:83,24:91,25:100},
                  0.05:{6:0,7:2,8:3,9:5,10:8,11:10,12:13,13:17,14:21,15:25,16:29,17:34,18:40,
                    19:46,20:52,21:58,22:65,23:73,24:81,25:89},
                  0.02:{7:0,8:1,9:3,10:5,11:7,12:9,13:12,14:15,15:19,16:23,17:27,18:32,19:37,
                    20:43,21:49,22:55,23:62,24:69,25:76},
                  0.01:{8:0,9:1,10:3,11:5,12:7,13:9,14:12,15:15,16:19,17:23,18:27,19:32,20:37,
                    21:42,22:48,23:54,24:61,25:68},
                  0.005:{9:0,10:1,11:3,12:5,13:7,14:9,15:12,16:15,17:19,18:23,19:27,20:32,
                    21:37,22:42,23:48,24:54,25:60},
                  0.001:{11:0,12:1,13:2,14:4,15:6,16:8,17:11,18:14,19:18,20:21,21:25,22:30,
                    23:35,24:40,25:45}}

def wilcoxon_test(palabra, nombres_conj_datos, nombres_algoritmos, matriz_datos, alpha, tipo):

    #El test de Wilcoxon compara dos algoritmos.
    if len(nombres_algoritmos) != 2:
        return {"fallo" : "Test de Wilcoxon solo aplicable a dos algoritmos"}
    
    #Paso de una matriz de conjuntos de datos a dos listas: lista "a", que contiene
    #los resultados de aplicar el primer algoritmo a los datos y una lista "b" que
    #contiene los resultados de aplicar el segundo algoritmo sobre los mismos datos.
    a = []
    b = []
    for lista_datos in matriz_datos:
        a.append(lista_datos[0])
        b.append(lista_datos[1])
    
    #Cálculo del número de veces que se aplican los dos algoritmos, es decir,
    #el número de individuos o datos sobre los que se aplican los algoritmos. El
    #tamaño de a y b deben ser iguales. Se conoce como tamaño muestral. Hay
    #dos muestras: a y b.
    N = len(a)
    
    #Cálculo de las diferencias sin signos y con signos. Se excluye el 0.
    diferencias = []
    signos = []
    for i in range(N):
        diferencia = a[i]-b[i]
        if diferencia != 0:
            diferencias.append(abs(diferencia))
            signos.append(diferencia)
    
    #Tamaño muestral después de eliminar las diferencias 0.
    N = len(diferencias)

    #El tamaño de la muestra  (sin ligaduras) debe ser al menos de 5.
    if N < 5:
        return {"fallo" : "Menos de 5 conjuntos de datos sin ligaduras"}

    #Rangos de orden 1,2,...,N. Cada elemento de copia tiene un rango asociado:
    #indice(elemento) + 1. Si hay empates se calcula la media del rango de cada
    #uno de los elementos repetidos.
    copia = list(diferencias)
    copia.sort()
    rangos = []
    for i in diferencias:
        rangos.append((copia.count(i)+copia.index(i)*2+1)/2.)
    
    #Sumas de los rangos de las Di mayores que 0 y menores que 0.
    mayor0 = []
    menor0 = []
    for i in range(N):
        if signos[i] > 0:
            mayor0.append(rangos[i])
        else:
            menor0.append(rangos[i])
    T_Mas = sp.sum(mayor0)
    T_Men = sp.sum(menor0)

    #T es el valor mínimo de T_Mas y T_Men.
    T = min(T_Mas,T_Men)

    #Cálculo del ranking. Será determinado según se trate de maximizar o minimizar. Por ejemplo
    #si lo que se pretendía era minimizar al restar los resultados del primer algoritmo por los
    #del segundo si hay mas signos negativos que positivos querrá decir que en global el
    #primer algoritmo mejora al segundo.
    ranking = []
    if not tipo:
        if len(menor0) >= len(mayor0):
            ranking.append([nombres_algoritmos[0],len(menor0)])
            ranking.append([nombres_algoritmos[1],len(mayor0)])
        else:
            ranking.append([nombres_algoritmos[1],len(mayor0)])
            ranking.append([nombres_algoritmos[0],len(menor0)])
    else:
        if len(mayor0) >= len(menor0):
            ranking.append([nombres_algoritmos[0],len(mayor0)])
            ranking.append([nombres_algoritmos[1],len(menor0)])
        else:
            ranking.append([nombres_algoritmos[1],len(menor0)])
            ranking.append([nombres_algoritmos[0],len(mayor0)])

    
    print "N (sin ceros):" , N
    print "Suma de rangos positivos:" , T_Mas
    print "Suma de rangos negativos:" , T_Men
    print "Valor T:" , T
    
    #Para tamaños muestrales pequeños, se puede determinar el test de Wilcoxon mediante la comparación
    #de T con el valor crítico de la tabla de Wilcoxon. Para tamaños muestrales grandes, el test se puede
    #aproximar con la distribución normal.
    if N <= 25:
        #Límite inferior del intervalo de aceptación.
        punto_critico = tabla_wilcoxon[alpha][N]
        return {"resultado" : str(T <= punto_critico), "estadistico" : T, "suma rangos pos" : T_Mas, "suma rangos neg" : T_Men ,
        "punto critico" : punto_critico, "ranking" : ranking}
    else:
        #Cálculo del valor Z
        Z = (T-((N*(N+1))/4))/sp.sqrt((N*(N+1)*(2*N+1))/24)
        #Cálculo del punto critico de la distribución Normal (Para alpha = 0.05
        #es -1.96 en el caso de dos colas, es decir 0.025 a cada lado).
        Z_alphaDiv2 = st.norm.ppf(alpha/2)
        #Cálculo del p_valor: Probabilidad de obtener un valor al menos tan extremo
        #como el estadístico Z.
        p_valor = 2*(1-st.norm.cdf(abs(Z)))
        
        print "Valor Z:" , Z
        print "Valor Z_alphaDiv2:" , Z_alphaDiv2
        print "p_valor:" , p_valor
        
        #Si p_valor < alpha => contraste estadísticamente significativo. Otra 
        #forma de saber si el estadístico Z cae en la región de rechazo es:
        #if Z <= Z_alphaDiv2 or Z >= -Z_alphaDiv2:
            #print "Se rechaza H0."
        #else:
            #print "Se acepta HO."
        
        return {"resultado" : str(p_valor < alpha), "p_valor" : round(p_valor,5), "estadistico" : round(Z,5),
        "suma rangos pos" : T_Mas, "suma rangos neg" : T_Men, "puntos criticos" : [round(Z_alphaDiv2,2),round(-Z_alphaDiv2,2)],
        "ranking" : ranking}
