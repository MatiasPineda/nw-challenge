# Challenge de viajes

## Descripción
Este repositorio contiene mi solución al challenge de viajes.
La actividad consiste en crear un proceso automátizado de ingesta de data. Esta data representa los viajes hechos por diferentes vehículos e incluyen una ciudad, un punto de origen y un destino.

El [CSV entregado](initial_data/trips.csv) es una muestra de los viajes y presenta la siguiente estructura:
```json
{
	"region": "Prague",
	"origin_coord": "POINT (14.4973794438191 50.00136875782311)",
	"destination_coord": "POINT (14.43109483523321 50.04052930943241)",
	"datetime": "2018-05-28 09:03:41",
	"datasource": "funny_car"
}
```


### Requerimientos

- [x] Procesos automatizados para ingerir y almacenar los datos bajo demanda.
- [x] Los viajes que son similares en términos de origen, destino y hora del día deben agruparse.
- [x] Desarrollar un servicio que devuelve el promedio semanal de la cantidad de viajes para un área definida por un bounding box y
la región
- [ ] Desarrollar una forma de informar sobre el estado de la ingesta de datos sin utilizar una solución de polling.
- [ ] La solución debe ser escalable a 100 millones de entradas.
- [x] La solución debe estar escrita en Python
- [x] Usar una base de datos SQL.
- [x] Incluye contenedores en tu solución
- [x] Dibuja cómo configuraría la aplicación en GCP


## Instalación

#### Requerimientos:
- [Docker](https://docs.docker.com/get-docker/)


Dirigirse a la carpeta raíz del proyecto para levantar el proyecto:

```bash
cd ~/directorio-proyecto
docker-compose up
```
Se debe considerar que no funcionará si los puertos 5000 y 5432 están ocupados.


## Solución Propuesta

Se propone una solución conforme a los requerimientos del desafío:
Una api creada en Flask que expone ciertos endpoints para la ingesta de datos y la consulta de los mismos.
La base de datos utilizada es PostgreSQL.

Para la agrupación de viajes en términos de origen, destino y hora del día, se eligió una solución de clustering con el algorítmo DBSCAN, el cual permite agrupar los viajes en grupos de acuerdo a la distancia entre ellos y el tamaño mínimo de los grupo y no requiere una cantidad de grupos mímima.

### Endpoints
```bash
POST /load-csv
```
Permite la carga de un archivo CSV con los datos de los viajes. Se permite modificar los parámetros de agrupación de viajes con los parámetros eps y min_samples, aunque ya traen valores por defecto.
| Param       | Tipo   | Requerido | Descripción                                                                             |
|-------------|--------|-----------|-----------------------------------------------------------------------------------------|
| path        | string |           | Ruta a un archivo .csv que debe contener los datos a ingresar                           |
| grouping    | bool   |           | Seleccionar si se quiere hacer el proceso de agrupar viajes durante la ingesta de datos |
| eps         | float  |           | Valor épsilon para algoritmo DBSCAN                                                     |
| min_samples | int    |           | Valor de tamaños mímimos de los grupos para el algoritmo DBSCAN                         |


```bash
POST /group-trips
```
Permite que se ejecute el proceso de agrupar viajes en la base de datos. Al igual que `/load-csv`, permite modificar los parámetros de agrupación de viajes con los parámetros eps y min_samples, aunque ya traen valores por defecto.

| Param       | Tipo   | Requerido | Descripción                                                                             |
|-------------|--------|-----------|-----------------------------------------------------------------------------------------|
| eps         | float  |           | Valor épsilon para algoritmo DBSCAN                                                     |
| min_samples | int    |           | Valor de tamaños mímimos de los grupos para el algoritmo DBSCAN                         |

```bash
POST /weekly-average
```
Permite consultar el promedio semanal de la cantidad de viajes para un área definida por un bounding box y la región.
Permite la carga de un archivo CSV con los datos de los viajes.
| Param   | Tipo  | Requerido | Descripción                                                     |
|---------|-------|-----------|-----------------------------------------------------------------|
| max_lat | float |    Si      | Latitud máxima del área a describir                             |
| min_lat | float |    Si      | Latitud mínima del área a describir                             |
| max_lon | float |    Si      | Longitud máxima del área a describir                            |
| min_lon | float |    Si      | Longitud mínima del área a describir							|

Entrega un json de la siguiente forma:
```json
{
  "per_region_results": [
    {
      "region": "Prague",
      "weekly_average_trips": "4.857"
    },
    {
      "region": "Turin",
      "weekly_average_trips": "0.000"
    },
    {
      "region": "Hamburg",
      "weekly_average_trips": "4.000"
    }
  ],
  "total_weekly_average": "8.857",
  "total_trips": 62
}
```

### Supuestos clave
- El archivo CSV a ingresar tiene la misma estructura que el entregado en el desafío.
- El requerimiento devuelve el promedio semanal de la cantidad de viajes para un área definida por un bounding box y
la región no deja claro una estructura, por lo que se popone la respuesta de `/weekly-average`
- Para la expresión "origen, destino y hora del día" del primer requerimiento, se asume que hora del día es para estudiar la hora y no la fecha de salida del viaje.



### Posibles mejoras
- No se implementó una forma de informar sobre el estado de la ingesta de datos sin utilizar una solución de polling, pero se podría implementar con un sistema de colas como PubSub.
- Se podría implementar un sistema de logs para tener un mejor seguimiento de los procesos.
- No se implementaron formas de hacer escalable la solución a 100 millones de entradas. Se pensó en un sistema de particionamiento de la base de datos en conjunto al uso de funciones serverless para que los problemas que vienen con la escalabilidad vayan siendo mitigados.
- Creo que no era mi decisión elegir el algorítmo de clústeres, o quizás se debía conversar con la data science. Me parece que se podrían haber implementado más algorítmos para comparar los resultados y elegir el mejor.
- Durante el desarrollo de la solución, me encontré con PostGIS, que se especializa en el manejo de datos geográficos. No lo implementé porque no tenía experiencia con él y no quería arriesgarme a no entregar el desafío a tiempo, pero creo que es una buena opción para mejorar la solución.
- Existen otros puntos importantes a la hora de desarrollar una aplicación, no se incluyeron por el reducido tiempo de desarrollo:
	- testing
	- documentación
	- manejo de errores
	- seguridad
	- monitoreo
	- CI/CD


## Arquitectura en GCP
- Gracias a que este proyecto está en contenedores, se puede utilizar un servicio de gcp para desplegarlo.
- Alternativamente, se puede utilizar Cloud SQL para la base de datos, ya que este servicio soporta Postgres.
- Para la ingesta de datos, se puede utilizar Cloud Storage para almacenar los archivos CSV y Cloud Functions para ejecutar el proceso de ingesta.

A continuación una descripción simple de la idea
![Untitled-2023-09-25-1021](https://github.com/MatiasPineda/nw-challenge/assets/49490747/01db768e-5991-4ce6-a752-38c57e643929)
