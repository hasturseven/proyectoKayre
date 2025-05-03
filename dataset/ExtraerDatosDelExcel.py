import pandas as pd

import re
import json
from fuzzywuzzy import fuzz

def extraer_datos_evaluacion(texto):
    if not isinstance(texto, str):
        return {}
    info_extraida = {}

    # Edad del paciente
    match = re.search(r'Paciente\s+de\s+(\d+)\s+años', texto, re.IGNORECASE)
    info_extraida["edad"] = int(match.group(1)) if match else None

    # Diagnóstico principal (puede ir seguido del código CIE-10)
    match = re.search(r'diagnóstico\s+de\s+(.*?)(?:\s+\(|,|\n|$)', texto, re.IGNORECASE)
    info_extraida["diagnostico"] = match.group(1).strip() if match else "No especificado"

    # Código CIE-10
    match = re.search(r'\(([A-Z]\d{2,4})\)', texto)
    info_extraida["codigo_cie10"] = match.group(1) if match else "No especificado"

    # Reacción adversa a medicamentos (RAM)
    match = re.search(r'RAM\s*[:\-]?\s*(\w+)', texto, re.IGNORECASE)
    info_extraida["ram"] = match.group(1).strip() if match else "No especificado"

    # Interacciones farmacológicas
    match = re.search(r'Interacciones\s+farmacológicas.*?[:\-]?\s*(.*?)(?=\n|$)', texto, re.IGNORECASE)
    info_extraida["interacciones_farmacologicas"] = match.group(1).strip() if match else "No especificado"

    # Adherencia global (de fase de intervención)

    # Suponiendo que 'texto' es el texto completo donde buscas
    match = re.search(
        r'\b(totalmente adherente|no adherente|parcialmente adherente|adherente)\b',
        texto, re.IGNORECASE
    )
    info_extraida["adherencia_global"] = match.group(1).strip().capitalize() if match else "No especificado"

    # ---- Nueva parte: Clasificación de dispensación ----
    texto_min = texto.lower()

    # Detectar palabras similares a "parcialmente"
    palabras = texto_min.split()
    parcial_detectado = any(fuzz.ratio(palabra, "parcialmente") >= 85 for palabra in palabras)

    # Detectar mención de problemas de entrega
    menciona_eps_ips = bool(re.search(r'\b(eps|epps|ep\s|ips|ipss|ip\s)\b', texto_min))
    problemas_dispensacion = bool(re.search(
        r'(no\s+entregado|no\s+dispensado|no\s+recibido|demora|pendiente\s+de\s+entrega|falta\s+de\s+medicamento)',
        texto_min
    ))

    # Detectar no adherencia grave
    no_dispensacion_regex = re.search(
        r'no\s+adh[eé]rente.*?(no\s+ha\s+recibido|no\s+entregado|no\s+dispensado|no\s+dispensaron)',
        texto_min
    )

    # Clasificar
    if no_dispensacion_regex:
        info_extraida["dispensacion"] = "no dispensacion"
    elif parcial_detectado and (menciona_eps_ips and problemas_dispensacion):
        info_extraida["dispensacion"] = "dispensacion parcial"
    elif "adherente" in texto_min and not problemas_dispensacion:
        info_extraida["dispensacion"] = "dispensacion completa"
    else:
        info_extraida["dispensacion"] = "No identificado"


    return info_extraida


def extraer_info_relevante_objetivo(texto):
    if not isinstance(texto, str):
        return {}

    info_extraida = {}
    #TODO FALTA EL OTRO DIAGNIOSTICO:
    # Otro diagnóstico (considerando "Niega" y otros diagnósticos con saltos de línea o comas)
    match = re.search(r'Otros?\s*diagnósticos?\s*[:\-]?\s*(.*?)(?=\n{2,}|\n\s*\w+:|$)', texto,
                      re.DOTALL | re.IGNORECASE)

    if match:
        # Si el diagnóstico es "Niega" o algo similar, lo manejamos adecuadamente
        diagnostico = match.group(1).strip()
        if diagnostico.lower() == "niega":
            info_extraida["otro_diagnostico"] = "Niega"
        else:
            # Limpiamos y dejamos los diagnósticos adecuados
            info_extraida["otro_diagnostico"] = re.sub(r'\s+', ' ', diagnostico)
    else:
        info_extraida["otro_diagnostico"] = "No especificado"

    # Tratamiento principal
    match = re.search(r'Tratamiento principal\s*[:\-]?\s*(.*?)(?:\n\n|\n\s*\w+:|$)', texto, re.DOTALL | re.IGNORECASE)
    info_extraida["tratamiento_principal"] = match.group(1).strip() if match else "No especificado"

    # Conciliación de medicamentos / medicamentosa
    match = re.search(r'Conciliación\s+(?:de\s+medicamentos|medicamentosa)\s*[:\-]?\s*(.*?)(?:\n\n|\n\s*\w+:|$)', texto, re.DOTALL | re.IGNORECASE)
    info_extraida["conciliacion_medicamentos"] = match.group(1).strip() if match else "No especificado"

    # Nivel de escolaridad
    match = re.search(r'Nivel\s+de\s+escolaridad\s*[:\-]?\s*(.*)', texto, re.IGNORECASE)
    info_extraida["nivel_escolaridad"] = match.group(1).strip() if match else "No especificado"

    # Consumo de alcohol
    match = re.search(r'Consumo\s+de\s+alcohol\s*[:\-]?\s*(.*)', texto, re.IGNORECASE)
    info_extraida["consumo_alcohol"] = match.group(1).strip() if match else "No especificado"

    # Consumo de tabaco
    match = re.search(r'Consumo\s+de\s+tabaco\s*[:\-]?\s*(.*)', texto, re.IGNORECASE)
    info_extraida["consumo_tabaco"] = match.group(1).strip() if match else "No especificado"

    # Consumo de sustancias psicoactivas
    match = re.search(r'Consumo\s+de\s+sustancia[s]?\s+psicoactivas\s*[:\-]?\s*(.*)', texto, re.IGNORECASE)
    info_extraida["consumo_sustancias"] = match.group(1).strip() if match else "No especificado"

    # Hospitalización en/los últimos 6 meses
    match = re.search(r'Hospitalización\s*(?:en\s*los\s*|los\s*)?últimos\s*6\s*meses\s*[:\-]?\s*(.*)', texto, re.IGNORECASE)
    info_extraida["hospitalizacion_ultimos_6_meses"] = match.group(1).strip() if match else "No especificado"

    return info_extraida







def extraer_clinimetrias(texto):
    """
    Extrae clinimetrías como DAS28 (PCR/VSG) y SLEDAI desde un texto clínico.
    Retorna un diccionario con los tipos encontrados y sus valores.
    """
    if not isinstance(texto, str):
        return {}

    clinimetrias = {}

    # Buscar DAS28 o AS28 con posibles variantes
    match_das = re.search(
        r'(DAS|AS)?\s*[-/]?\s*28\s*[-/]?\s*(PCR|VSG)?\s*[:\-]?\s*([0-9]+(?:\.[0-9]+)?)',
        texto, re.IGNORECASE)
    if match_das:
        tipo = "DAS28"
        subtipo = match_das.group(2).upper() if match_das.group(2) else "NO ESPECIFICADO"
        valor = match_das.group(3)
        clinimetrias[tipo] = {"tipo": f"{tipo} {subtipo}", "valor": float(valor)}

    # Buscar SLEDAI con número
    match_sledai = re.search(
        r'SLEDAI\s*[:\-]?\s*([0-9]+(?:\.[0-9]+)?)',
        texto, re.IGNORECASE)
    if match_sledai:
        clinimetrias["SLEDAI"] = {"tipo": "SLEDAI", "valor": float(match_sledai.group(1))}

    return clinimetrias



def extraer_y_organizar_datos(df, filas_por_bloque=7, tripletas_columnas=[(2, 3, 4), (7, 8, 9), (12, 13, 14)],ruta_archivo=None):
    bloques_extraidos = {}
    fila_actual = 0
    id_paciente = 0

    while fila_actual + filas_por_bloque <= df.shape[0]:
        fila_nombre = df.iloc[fila_actual]

        if fila_nombre.count() < 1:
            fila_actual += 1
            continue

        for col1, col2, col3 in tripletas_columnas:
            if col3 >= df.shape[1]:
                continue
            if fila_actual + filas_por_bloque > df.shape[0]:
                continue

            bloque_data = df.iloc[fila_actual:fila_actual + filas_por_bloque, [col1, col2, col3]]

            if bloque_data.isnull().all().all():
                continue

            clinimetria_raw = df.iloc[fila_actual + 6, col1] if fila_actual + 6 < df.shape[0] else None
            clinimetria_valor = extraer_clinimetrias(clinimetria_raw)

            clinimetria_tipo = None
            clinimetria_valor_num = None

            if clinimetria_valor:
                clave = list(clinimetria_valor.keys())[0]
                clinimetria_tipo = clinimetria_valor[clave]["tipo"]
                clinimetria_valor_num = clinimetria_valor[clave]["valor"]
            else:
                clinimetria_tipo = "No aplica"
                clinimetria_valor_num = "No aplica"

            objetivo_dict = extraer_info_relevante_objetivo(df.iloc[fila_actual + 2, col2])
            eva_ana = extraer_datos_evaluacion(df.iloc[fila_actual + 4, col1])

            paciente_dict = {
                "nombre": df.iloc[fila_actual, col1],
                "clinimetria_tipo": clinimetria_tipo,
                "clinimetria_valor": clinimetria_valor_num,
                "observaciones": df.iloc[fila_actual + 2, col3],
            }

            # Añadir cada clave del objetivo al mismo nivel
            paciente_dict.update(objetivo_dict)
            paciente_dict.update(eva_ana)
            # AGREGAR FECHA DE LAS CONSULTAS ACADA PACIENTE
            nombre_archivo = ruta_archivo.split('/')[-1]  # Obtener solo el nombre del archivo
            coincidencia = re.search(r'-(\d{2})-(\d{2})-(\d{4})\.', nombre_archivo)
            if coincidencia:
                dia = coincidencia.group(1)
                mes = coincidencia.group(2)
                anio = coincidencia.group(3)
                fecha_archivo = f"{dia}-{mes}-{anio}"
                # Agregar la fecha a cada diccionario de paciente
                paciente_dict["fecha_consulta"] = fecha_archivo

            # Guardar usando id numérico
            bloques_extraidos[id_paciente] = paciente_dict

            id_paciente += 1

        fila_actual += filas_por_bloque

    return bloques_extraidos


def mostrar_datos_organizados(bloques_extraidos):
    if not bloques_extraidos:
        print("No se encontraron datos de pacientes.")
        return

    for id_paciente, datos in bloques_extraidos.items():
        print(f"\nPaciente {id_paciente}")
        print("-" * 40)
        for clave, valor in datos.items():
            print(f"{clave}: {valor}")





def main():
    ruta_archivo = 'ENTREVISTAS\TUNJA-26-03-2025.xlsx'  # Ajusta con tu ruta
    try:
        df = pd.read_excel(ruta_archivo, header=None)
    except FileNotFoundError:
        print(f"Error: No se pudo encontrar el archivo en la ruta: {ruta_archivo}")
        return
    except Exception as e:
        print(f"Error al leer el archivo Excel: {e}")
        return

    datos_pacientes = extraer_y_organizar_datos(df,ruta_archivo=ruta_archivo)
    mostrar_datos_organizados(datos_pacientes)


    # Guardar como JSON
    ruta_salida = 'DATOSJSON\datos_pacientes.json'
    try:
        with open(ruta_salida, 'w', encoding='utf-8') as f:
            json.dump(datos_pacientes, f, ensure_ascii=False, indent=4)
        print(f"\n✅ Datos guardados exitosamente en {ruta_salida}")
    except Exception as e:
        print(f"❌ Error al guardar archivo JSON: {e}")


if __name__ == "__main__":
    main()
