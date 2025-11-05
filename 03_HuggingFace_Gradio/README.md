# ModeloIA Deporte/Juegos olímpicos 🏟

Predicción de la probabilidad de obtener una medalla olímpica en función de características demográficas y físicas del atleta y del tipo de deporte.

## 🏊 Elección del dataset

### Dataset: 120 years of Olympic history: athletes and results
https://www.kaggle.com/datasets/heesoo37/120-years-of-olympic-history-athletes-and-results/data

2 archivos .csv: athlete_events.csv que contiene información de los atletas y eventos y noc_regions.csv para mapear los códigos NOC a regiones/países. El dataset cubre los Juegos Olímpicos desde 1896 hasta 2016.

### ¿Por qué?
Los Juegos Olímpicos son uno de los eventos deportivos más importantes del mundo, seguidos por millones de personas. Poder predecir la probabilidad de que un atleta gane una medalla, considerando sus características físicas y demográficas resulta un problema atractivo tanto para el público general como para la investigación académica. Es un tema transversal y multidisciplinar: combina historia, geopolítica, economía, cultura y deporte.

### Posibles aplicaciones:
•	Aplicaciones en el ámbito deportivo

 	Detección de talento: ayudar a identificar atletas con mayor potencial según sus características físicas y demográficas.
 	Planificación de entrenamientos basados en perfiles de atletas que históricamente han tenido más éxito.
 	Tomar decisiones sobre en qué disciplinas invertir más recursos, considerando los perfiles típicos de ganadores.
  
•	Aplicaciones en tecnología e IA

 	Desarrollo de sistemas de recomendación: según perfil físico y demográfico.
 	Entrenadores virtuales inteligentes: sistemas que ajusten estrategias de entrenamiento según la probabilidad estimada de éxito.
  
•	Aplicaciones en investigación y análisis

 	Análisis de desigualdades: explorar cómo el género o el país afectan las oportunidades de ganar medallas.
 
## 🎾 Definición del problema

¿Es posible predecir si un atleta ganará una medalla olímpica utilizando como variables explicativas su sexo, edad, estatura, peso, el deporte en que compite y su país de origen?
Clasificación binaria.

El objetivo es clasificar cada atleta, utilizando las características físicas y demográficas:

1.	Clase 1: Gana Medalla (Gold, Silver, Bronze)
 
2.	Clase 0: No Gana Medalla (NA)

## Selección de la variable dependiente y explicativas

### Variable objetivo:
ganar medalla (sí/no)

### Variables de entrada/Features explicativas:
 	Sexo – categórica
 	Edad – numérica
 	Estatura - numérica
 	Peso - numérica
 	País de origen - categórica
	Deporte - categórica
 
## 🤼 Exploración inicial de datos (EDA)

El dataset tiene 15 columnas y 271.116 filas (participaciones individuales).

### Análisis de la variable objetivo
0 (No Medalla)	  	231.333	  		85,3%

1 (Ganó Medalla)	39.783	  		14,7% 

Este desequilibrio se origina en el hecho de que la cantidad de participantes en los Juegos Olímpicos es considerablemente mayor que la de ganadores de medallas.

### Análisis de datos faltantes (Nulos)
Años	  	9.484	  		3,5%

Altura		60.171			22%

Peso	  	62.875			23%

La cantidad de nulos en la variable años de baja, se puede imputar o ignorar.
De altura y peso es moderada y relevante para el análisis de atletas.

### Exploración de Variables Numéricas (Age, Height, Weight)
Variable	Media aprox.	Mediana aprox.	Desviación Estándar aprox.   Min-Max

Años	    25,6 años	    25 años	        6,4 años					10 - 97/72

Altura	  	175,3 cm	    175,0 cm	    10,5 cm						127 - 236

Peso	    70,7 kg	      	70,0 kg	        14,3 kg						25 - 214

Las distribuciones son relativamente normales, pero con una gran variación, (ej. la participación de atletas muy jóvenes y muy mayores, la diversidad de tipos de cuerpos requeridos para diferentes deportes).

### Variable	Comparación Ganó Medalla
0 vs. 1	Implicación Predictiva

Años
La mediana de edad de los ganadores de medalla es a menudo ligeramente superior a la de los no ganadores.	La experiencia es un factor. Atletas muy jóvenes o muy mayores tienen menor probabilidad.

Altura
La mediana de altura de los ganadores es ligeramente superior a la de los no ganadores.	No hay una altura "óptima" general, pero en deportes clave (baloncesto, natación), la altura alta es un fuerte predictor.

Peso
La mediana de peso de los ganadores es ligeramente superior a la de los no ganadores.	La relación peso/altura (IMC) podría ser más predictiva que el peso solo.

### Exploración de Variables Categóricas (Sex, NOC, Sport)
Sexo
Sexo	Tasa de éxito
M (Male)	  	13%
F (Female)		16%

Las mujeres tienen una tasa de éxito por participación ligeramente superior a la de los hombres. Esto puede deberse a la menor variedad de eventos de participación femenina en los primeros años del historial olímpico.


País de Origen

País (NOC)				Total de medallas		Tasa de éxito
USA	                  		5238	    			18%
URS (Unión Soviética)		3371	    			21%
GDR (Alemania Oriental)		2855	  				20%
UK							1709					12%

El país de origen es un predictor extremadamente fuerte. Países como la antigua Alemania Oriental o la Unión Soviética, a pesar de tener menos participaciones totales que EE. UU., tienen una tasa de éxito por participación mucho mayor debido a sus políticas deportivas intensivas.


Deporte

La variable Sport es el predictor más fuerte de ganar una medalla, ya que la probabilidad depende del tipo de competencia (individual vs. equipo) y el número de eventos. Un atleta tiene una probabilidad mucho mayor de ganar una medalla si participa en un deporte de equipo en comparación con un deporte individual.


## 🛶 Preprocesamiento de datos	
### Valores nulos:
		
			Columna Medal - Todos los valores NaN (Not a Number, que son los valores faltantes) reemplazados con el texto 'NoMedal'. Creada una nueva columna llamada Medaled. Asignado 1 si el valor es 'Medal' y 0 si es 'NoMedal'.
			
			Columnas Height y Weight - Imputación Segmentada por Deporte. Rellena los valores nulos de Height/Weight con la mediana de Height/Weight calculada solo para el deporte de esa fila.
			
			Columna Age - Imputación Global. Rellena los valores nulos con la mediana de la columna Age completa.
		
### Definición de variables:
		
			Columnas numéricas  ['Age', 'Height', 'Weight']
			
			Columnas categóricas ['Sex', 'Sport', 'Team']
			
			Creada la matriz de features (X), que contiene todas las variables de entrada combinadas y el vector objetivo (y), que contiene la variable que el modelo debe predecir (1 gana medalla, 0 no).

### División en train/test:
		
			Train - 70% de los datos para entrenar el modelo, una división aleatoria.
			
			Test - 30% de los datos para probarlo, división aleatoria.
			
			Dado el desbalance de clases (15% medallas, 85% no medallas) está asegurado que la proporción de medallas vs. no medallas sea la misma en el conjunto de entrenamiento y en el de prueba.
			
			RSEED (42) para garantizar la reproducibilidad del modelo.

## 🏋️ Entrenamiento de modelos

		Pipeline de scikit-learn - transformaciones que se ejecutan automáticamente en orden.
	
		Random Forest - 200 árboles predice un resultado (Medalla o No Medalla).
	
## 🤺 Evaluación del modelo
	
		Precision (Precisión)	(0,50)	De todos los atletas que modelo selecciona como posibles ganadores (predicciones positivas), uno de cada dos es, en realidad, un medallista. El modelo es propenso a las alertas falsas.
		
		Recall (Sensibilidad)	(0,46)	De todos los atletas que realmente ganaron medalla, el modelo logró identificar al 46%.	El modelo no es bueno capturando todos los casos positivos.
		
		F1-Score				(0,48)	Bajo, pero buen resultado para un problema tan desbalanceado.

		Accuracy 				(0.85)	Acierta en el 85% de las predicciones totales. A primera vista parece muy bueno. Sin embargo, esta alta exactitud está sesgado por la clase mayoritaria.

		Macro Avg (F1-Score 0.69): Calcula el promedio simple del F1-Score de las dos clases. Indica un rendimiento general moderado.
		
		Weighted Avg (F1-Score 0.84): Calcula el promedio ponderado por el número de casos (Soporte) de cada clase. Como la Clase 0 tiene un soporte mucho mayor, este promedio es mucho más alto (0.84) y se acerca al accuracy global.	
	
## 🥇 Conclusiones y comunicación de resultados
		El modelo tiene un problema de sesgo hacia la clase mayoritaria. Sus predicciones fallan en detectar a la mitad de los medallistas reales (bajo Recall de 0.46).
