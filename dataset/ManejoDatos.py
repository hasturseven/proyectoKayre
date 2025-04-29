import json
import pandas as pd

# Cargar los datos desde el archivo JSON
with open("datos_pacientes.json", "r", encoding="utf-8") as file:
    data = json.load(file)

# Lista para almacenar los datos de cada paciente
pacientes_data = []

for paciente_id, paciente_info in data.items():
    if not isinstance(paciente_info, dict):
        continue

    nombre = str(paciente_info.get("nombre", "")).strip()

    # Edad y tipo identificación
    edad = paciente_info.get("edad")
    if isinstance(edad, int):
        tipo_identificacion = 1 if edad >= 18 else 2
    else:
        edad = None
        tipo_identificacion = None

    escolaridad = str(paciente_info.get("nivel_escolaridad", "")).strip()

    # Género: 1 = femenino, 2 = masculino, 0 = desconocido
    observaciones = str(paciente_info.get("observaciones", "")).strip().upper()
    if "FEMENINO" in observaciones:
        genero = 1
    elif "MASCULINO" in observaciones:
        genero = 2
    else:
        genero = 0

    # Gestación: 0 para todos
    gestacion = 0

    # Consumo de SPA: verificamos alcohol, tabaco, sustancias
    alcohol = str(paciente_info.get("consumo_alcohol", "")).strip().strip('"').upper()
    tabaco = str(paciente_info.get("consumo_tabaco", "")).strip().strip('"').upper()
    sustancias = str(paciente_info.get("consumo_sustancias", "")).strip().strip('"').upper()

    if alcohol == "NIEGA" and tabaco == "NIEGA" and sustancias == "NIEGA":
        consumo_spa = 0
    elif tabaco != "NIEGA":
        consumo_spa = 1
    elif alcohol != "NIEGA":
        consumo_spa = 2
    elif sustancias != "NIEGA" :
        consumo_spa = 3
    else:
        consumo_spa = 0

    # Columna vacía de interacción alcohol/drogas
    interaccion_medicamento = ""

    # Trastornos mentales: 0 para todos
    trastornos_mentales = 0

    # Factores trato paciente: 0 para todos
    trato_paciente = 0

    #HOSPITALIZACION ULTIMOS 6 MESES
    hospitalizacion_6_meses = str(paciente_info.get("hospitalizacion_ultimos_6_meses", "")).strip().lower()

    if hospitalizacion_6_meses in ["no", "no especificado"]:
        ultimos_6_meses = 0
    else:
        ultimos_6_meses = 4

    pacientes_data.append({
        "Nombre": nombre,
        "Tipo Identificación": tipo_identificacion,
        "Edad": edad,
        "Grado Escolaridad": escolaridad,
        "Género": genero,
        "Gestación": gestacion,
        "Consumo de SPA": consumo_spa,
        "4. Consumo de alcohol o drogas que interacciona con medicamento": interaccion_medicamento,
        "Trastornos mentales": trastornos_mentales,
        "Factores relacionados con el trato paciente": trato_paciente,
        "hospitalizacion ultimos 6 meses":ultimos_6_meses
    })

# Crear DataFrame
df = pd.DataFrame(pacientes_data)

# Guardar a Excel
df.to_excel("pacientes_detallado.xlsx", index=False)
