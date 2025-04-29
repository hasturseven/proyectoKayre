import json
import pandas as pd
import re

# Cargar los datos desde el archivo JSON
with open("datos_pacientes.json", "r", encoding="utf-8") as file:
    data = json.load(file)

# Lista para almacenar los datos de cada paciente
pacientes_data = []

# Diccionario de categorías de enfermedades
categorias = {
    "1. Enfermedad cardiovascular": ["cardiovascular", "infarto", "angina", "coronaria", "hta"],
    "2. Hipertensión arterial": ["hipertensión", "hipertension", "hta"],
    "3. Diabetes mellitus": ["diabetes"],
    "4. Enfermedad renal": ["renal", "riñón", "insuficiencia renal", "nefropatía"],
    "5. Enfermedad hepatica": ["hepática", "hígado", "cirrosis", "esteatosis"],
    "6. Osteoporosis/ Artrosis/ Osteoartrosis": ["osteoporosis", "artrosis", "osteoartrosis", "coxartrosis", "gonartrosis"],
    "7. Enfermedad gastrointestinal": ["gastro", "colon", "gastritis", "úlceras", "gastrointestinal", "reflujo", "sucralfato"],
    "8. Hipotiroidismo/Hipertiroidismo": ["hipotiroidismo", "hipertiroidismo", "tiroid"],
    "9. Cancer": ["cáncer", "tumor", "neoplasia", "carcinoma"]
}

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
    elif sustancias != "NIEGA":
        consumo_spa = 3
    else:
        consumo_spa = 0

    # Columna vacía de interacción alcohol/drogas
    interaccion_medicamento = ""

    # Trastornos mentales: 0 para todos
    trastornos_mentales = 0

    # Factores trato paciente: 0 para todos
    trato_paciente = 0

    # Hospitalización últimos 6 meses
    hospitalizacion_6_meses = str(paciente_info.get("hospitalizacion_ultimos_6_meses", "")).strip().lower()
    if hospitalizacion_6_meses in ["no", "no especificado"]:
        ultimos_6_meses = 0
    else:
        ultimos_6_meses = 4

    # Clasificación de enfermedades
    otro_diag = str(paciente_info.get("otro_diagnostico", "")).lower()
    clasificacion = {key: 0 for key in categorias}
    otros_enfermedades = []

    for enfermedad in re.split(r'[;,.\n]+', otro_diag):
        enfermedad = enfermedad.strip()
        clasificada = False
        for categoria, palabras in categorias.items():
            if any(p in enfermedad for p in palabras):
                clasificacion[categoria] = 1
                clasificada = True
                break
        if enfermedad and not clasificada and enfermedad != "niega":
            otros_enfermedades.append(enfermedad)

    # -------------------------
    # COMORBILIDADES (categorías del 1 al 9)
    comorbilidades = sum(clasificacion[c] for c in list(categorias.keys()))
    if comorbilidades == 1:
        presenta_comorbilidades = 2
    elif comorbilidades >= 2:
        presenta_comorbilidades = 4
    else:
        presenta_comorbilidades = ""

    # -------------------------
    # APLICA CLINIMETRÍA
    clinimetria_tipo = str(paciente_info.get("clinimetria_tipo", "")).strip().lower()
    if clinimetria_tipo and clinimetria_tipo != "no aplica":
        aplica_clinimetria = 4
    else:
        aplica_clinimetria = 0
    # -------------------------
    # COMORBILIDADES (categorías del 1 al 9)
    comorbilidades = sum(clasificacion[c] for c in list(categorias.keys()))
    if comorbilidades == 1:
        presenta_comorbilidades = 2
    elif comorbilidades >= 2:
        presenta_comorbilidades = 4
    else:
        presenta_comorbilidades = ""

    # -------------------------
    # APLICA CLINIMETRÍA
    clinimetria_tipo = str(paciente_info.get("clinimetria_tipo", "")).strip().lower()
    if clinimetria_tipo and clinimetria_tipo != "no aplica":
        aplica_clinimetria = 4
    else:
        aplica_clinimetria = 0


    # Guardar los datos del paciente
    fila_paciente = {
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
        "hospitalizacion ultimos 6 meses": ultimos_6_meses,
        "10. Otros": 1 if otros_enfermedades else 0,
        "¿Cuáles otras?": ", ".join(otros_enfermedades),
        "4. Presenta más de 2 comorbilidades de la lista \n2. Presenta 1 comorbilidad de la lista": presenta_comorbilidades,
        "APLICA CLINIMETRÍA\n0. No, requiere de otro parametro\n4. Si, pero es > a 2 meses": aplica_clinimetria

    }

    # Agregar columnas de clasificación
    fila_paciente.update(clasificacion)

    # Añadir al conjunto de datos
    pacientes_data.append(fila_paciente)

# Ordenar las columnas
columnas_ordenadas = [
    "1. Enfermedad cardiovascular",
    "2. Hipertensión arterial",
    "3. Diabetes mellitus",
    "4. Enfermedad renal",
    "5. Enfermedad hepatica",
    "6. Osteoporosis/ Artrosis/ Osteoartrosis",
    "7. Enfermedad gastrointestinal",
    "8. Hipotiroidismo/Hipertiroidismo",
    "9. Cancer",
    "10. Otros",
    "¿Cuáles otras?",
    "4. Presenta más de 2 comorbilidades de la lista \n2. Presenta 1 comorbilidad de la lista",
    "APLICA CLINIMETRÍA\n0. No, requiere de otro parametro\n4. Si, pero es > a 2 meses"
]
# Crear DataFrame
df = pd.DataFrame(pacientes_data)

# Ordenar las columnas
columnas_ordenadas = [
    "1. Enfermedad cardiovascular",
    "2. Hipertensión arterial",
    "3. Diabetes mellitus",
    "4. Enfermedad renal",
    "5. Enfermedad hepatica",
    "6. Osteoporosis/ Artrosis/ Osteoartrosis",
    "7. Enfermedad gastrointestinal",
    "8. Hipotiroidismo/Hipertiroidismo",
    "9. Cancer",
    "10. Otros",
    "¿Cuáles otras?",
    "4. Presenta más de 2 comorbilidades de la lista \n2. Presenta 1 comorbilidad de la lista",
    "APLICA CLINIMETRÍA\n0. No, requiere de otro parametro\n4. Si, pero es > a 2 meses"
]

# Mantener también las otras columnas (como nombre, edad, etc.)
otras_columnas = [col for col in df.columns if col not in columnas_ordenadas]
columnas_finales = otras_columnas + columnas_ordenadas

# Reordenar el DataFrame
df = df[columnas_finales]

# Guardar a Excel
df.to_excel("pacientes_detallado.xlsx", index=False)

