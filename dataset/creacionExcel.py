import pandas as pd
from openpyxl import load_workbook

# Lista de encabezados extraídos del texto
headers = [
    "Motivo de no atención", "Fecha de clasificación", "Número de documento del paciente",
    "Nombre completo del paciente", "Tipo de documento", "Edad (años)", "Nivel educativo",
    "Sexo", "Prioridad inmediata", "Consumo de SPA", "Interacción SPA y medicamento",
    "Diagnóstico psiquiátrico", "Conocimiento enfermedad/tratamiento",
    "Hospitalización en últimos 6 meses", "1. Enfermedad cardiovascular",
    "2. Hipertensión arterial", "3. Diabetes mellitus", "4. Enfermedad renal",
    "5. Enfermedad hepática", "6. Osteoporosis / Artrosis / Osteoartrosis",
    "7. Enfermedad gastrointestinal", "8. Hipotiroidismo / Hipertiroidismo", "9. Cáncer",
    "10. Otros", "¿Cuáles otras?", "Clasificación comorbilidades", "Aplica clinimetría",
    "DAS28 (AR)", "SLEDAI (LES)", "ASDAS (EAS)", "Polifarmacia (>5 medicamentos)",
    "Cambio de medicación", "Inicio del tratamiento", "Inicio de síntomas",
    "Adherencia biológico", "Adherencia inhibidor JAK", "Adherencia tratamiento convencional DMARDs",
    "Adherencia general", "Dispensación parenteral", "Dispensación oral",
    "¿Interacciones identificadas?", "Relevancia de interacciones", "Mecanismo de interacción",
    "Tipo de interacción", "Descripción moléculas que interactúan", "¿RAM presente?",
    "Severidad RAM", "Medicamento sospechoso", "Estado actual de la RAM",
    "¿Fallo terapéutico?", "Tipo de fallo terapéutico", "Definido por comité FV",
    "¿Problema relacionado con medicamento?", "Tipo de problema relacionado con medicamento"
]

# Crear un DataFrame vacío con los encabezados
df = pd.DataFrame(columns=headers)

# Ruta local válida en Windows (modifica si lo quieres en otro sitio)
excel_path = r"C:\Users\sergi\OneDrive\Escritorio\formato_clinico_autoinmune.xlsx"

# Guardar el DataFrame vacío en Excel
df.to_excel(excel_path, index=False)

# Ajustar ancho de columnas con openpyxl
wb = load_workbook(excel_path)
ws = wb.active

for col in ws.columns:
    max_length = 0
    column = col[0].column_letter
    for cell in col:
        try:
            if cell.value:
                max_length = max(max_length, len(str(cell.value)))
        except:
            pass
    adjusted_width = max_length + 2
    ws.column_dimensions[column].width = adjusted_width

wb.save(excel_path)

print("Archivo Excel creado y columnas ajustadas correctamente.")
