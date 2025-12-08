
El sistema se compone de:

API principal (FastAPI) → expone el endpoint /identify-and-answer, orquesta la verificación facial y ejecuta consultas normativas.

Clientes PP2 y PP1 → módulos dedicados a la comunicación con los servicios de verificación biométrica y con el RAG respectivo.

Pipeline de fusión (τ/δ) → proceso que unifica las respuestas de los verificadores y determina el resultado final.

Módulo MCP → permite que otros entornos consuman las herramientas del PP3 como servicios externos.

Base de datos MongoDB → almacena logs detallados tanto de accesos como de actividad de servicios.

Workflow n8n (variante opcional) → permite implementar la orquestación de forma visual mediante nodos.

Scripts, configuración y utilidades para asegurar reproducibilidad y facilidad de despliegue.

El reporte cubre desde la preparación del entorno local hasta la ejecución práctica del sistema.

Preparación del Entorno

Para el desarrollo se utilizaron tres repositorios:

PP2 (verificadores biométricos) — alojados en GitHub y ya operativos mediante endpoints /verify.

PP1 (servicio de normativa/RAG) — accesible a través del endpoint /ask.

PP3 (nuevo) — creado desde cero como proyecto principal para la orquestación.

Se creó una carpeta de trabajo llamada ufro-master y dentro de ella se configuró un entorno virtual de Python (Python 3.11) junto con un archivo requirements.txt que incluye FastAPI, Motor (MongoDB async), httpx y otras dependencias esenciales.

3. Arquitectura General

El sistema se diseñó bajo un modelo modular:

3.1 API en FastAPI

Expone dos endpoints principales:

/identify-and-answer:
Recibe una imagen y una pregunta.
● valida credenciales
● consulta a los verificadores PP2 en paralelo
● ejecuta la lógica de fusión
● si corresponde, consulta al RAG (PP1)
● registra todo en base de datos
● devuelve un resultado final al cliente

/healthz:
Verifica conectividad con MongoDB y carga del roster PP2.

3.2 Orquestador PP2

Se implementó un cliente asincrónico que consulta simultáneamente todos los verificadores configurados en registry.yaml.
Cada respuesta se registra en la colección service_logs, incluyendo latencias, códigos de estado, tamaño del payload y posibles errores.

3.3 Cliente PP1 (Normativa)

Módulo que envía la pregunta del usuario al RAG seleccionado y registra igualmente estadísticas detalladas del servicio.

3.4 Lógica de Fusión (τ / δ)

Se estableció un procedimiento simple pero efectivo:

Ordenar los verificadores según el puntaje entregado (score).

Determinar si el puntaje máximo supera un umbral fijo (τ).

Validar si la diferencia entre el primer y segundo puntaje supera la margen (δ).

El resultado se clasifica como:

identified

ambiguous

unknown

3.5 Base de Datos MongoDB

Se utilizaron dos colecciones:

access_logs: registros completos de cada solicitud del usuario.

service_logs: historial de llamadas a PP1 y PP2 con métricas técnicas.

Se definieron índices para mejorar el rendimiento de consultas agregadas.

3.6 MCP Server

Se añadió un servidor MCP que expone como herramientas:

identify_person

ask_normativa

Esto permite integrar el PP3 con plataformas externas que consuman instrucciones externas mediante MCP.

3.7 Workflow opcional n8n

Se documentó y habilitó la posibilidad de replicar toda la orquestación mediante un flujo visual con nodos Webhook, HTTP Request, Function y MongoDB Insert.

4. Configuración de Servicios PP2 (registry.yaml)

El archivo conf/registry.yaml permite definir los verificadores disponibles.
Ejemplo:

pp2_roster:
  - name: "Ana Perez"
    endpoint_verify: "http://localhost:5001/verify"
    threshold: 0.75
    active: true

  - name: "Luis Soto"
    endpoint_verify: "http://localhost:5002/verify"
    threshold: 0.75
    active: true


Cada entrada puede activarse/desactivarse y tiene su propio umbral de confianza.

5. Implementación de los Módulos del Sistema

Los directorios creados son:

api/
orchestrator/
db/
conf/
mcp_server/
n8n/
scripts/
tests/


Los archivos principales del proyecto incluyen:

api/app.py (API central)

orchestrator/pp2_client.py (cliente biométrico)

orchestrator/pp1_client.py (cliente normativa)

orchestrator/fuse.py (lógica de fusión)

db/mongo.py y db/queries.py

db/ensure_indexes.py (asegura índices)

mcp_server/server.py

conf/registry.yaml

tests/mock_pp2.py (servidores de prueba)

Cada módulo se probó de forma independiente antes de unirlos en la API.

6. Ejecución del Sistema
6.1 Levantar MongoDB (Docker)
docker run -d --name ufro-mongo -p 27017:27017 \
    -e MONGO_INITDB_ROOT_USERNAME=ufro \
    -e MONGO_INITDB_ROOT_PASSWORD=secret \
    mongo:6

6.2 Activar entorno virtual y ejecutar el servidor
uvicorn api.app:app --reload --port 8000


La documentación automática queda disponible en:

http://localhost:8000/docs

6.3 Ejemplo de request

Headers necesarios:

Authorization: Bearer secret-token-123
x-user-id: alumno123
x-user-type: external

7. Métricas y Consultas Agregadas

Se implementaron consultas en db/queries.py y endpoints en /metrics/*.
Un ejemplo de agregación es:

conteo de decisiones (“identified”, “unknown”, “ambiguous”)

latencias promedio

actividad por usuario

servicios fallidos o con timeouts

Estas métricas permiten observar rendimiento y confiabilidad del sistema completo.

8. Workflow Alternativo con n8n

Como variante, se habilitó un flujo equivalente en n8n que replica la lógica del PP3 de manera visual.
El flujo consiste en:

Webhook POST

Fan-out a PP2 mediante nodos HTTP Request

Función JS para aplicar τ/δ

Llamada condicional a PP1

Inserción en MongoDB

Respuesta final al cliente

Este enfoque permite ejecutar toda la orquestación sin escribir código adicional.

