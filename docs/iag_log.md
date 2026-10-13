# AI Usage Log (Registro de Uso de IA)

Registro de interacciones con herramientas de inteligencia artificial generativa durante el desarrollo del proyecto ResumeLens, en cumplimiento de los requisitos de la asignatura Computación y Estructuras Discretas 3.

---

## Sesión 1 — 2026-10-09 (Edwar Estacio)

- **Fecha:** 2026-10-09
- **Herramienta:** Gemini 3.8 Flash (High) (asistente de código Antigravity)
- **Objetivo:** Auditoría inicial del repositorio, diseño de la gramática libre de contexto para el lenguaje de perfil de candidato (textX) e implementación del módulo `dsl.py`.
- **Prompt base:** Auditoría completa del repositorio, verificación de contratos de interfaz, propuesta de plan de contribuciones e implementación de la gramática DSL (`candidate.tx`), funciones `to_dsl` y `validate`, junto con su suite de pruebas unitarias.
- **Aportes y contexto del estudiante:**
  - Definición de restricciones de diseño de la gramática respetando el contrato de interfaces (`docs/contracts.md`, Sección 6.5).
  - Verificación de la no inclusión de comentarios meta sobre planes dentro de los archivos de código fuente.
  - Configuración del entorno de pruebas y revisión de los casos de borde para serialización y deserialización.
- **Resultados generados y utilizados:**
  - Gramática formal textX en `src/resumelens/candidate.tx`.
  - Módulo `src/resumelens/dsl.py` con `get_metamodel()`, `to_dsl()` y `validate()`.
  - Integración en `src/resumelens/__init__.py`.
  - Suite de 15 pruebas automatizadas en `tests/test_dsl.py`.
- **Adaptaciones y cambios realizados:**
  - Se eliminaron encabezados y comentarios meta que hacían referencia a tareas del plan de trabajo en los archivos fuente.
  - Se ajustó el manejo de excepciones para mapear `textx.exceptions.TextXError` a `DSLValidationError` preservando línea y columna.

---

## Sesión 2 — 2026-10-09 (Edwar Estacio)

- **Fecha:** 2026-10-09
- **Herramienta:** Gemini 3.8 Flash (High) (asistente de código Antigravity)
- **Objetivo:** Formalización matemática y en notación ISO/IEC 14977 EBNF de la gramática libre de contexto de la Etapa 4, definición de la 4-tupla formal, justificación teórica y documentación de diseño modular en `docs/formalization.md` y `docs/design_modules.md`.
- **Prompt base:** Formalización de la gramática libre de contexto en EBNF, terminales, no terminales, justificación teórica y diseño arquitectónico de módulos.
- **Aportes y contexto del estudiante:**
  - Coordinación de secciones de responsabilidades en documentos compartidos preservando los espacios de Alejo y Diego.
  - Verificación de la correspondencia exacta entre las producciones EBNF y las reglas implementadas en `candidate.tx`.
  - Gestión de contribuciones respetando la separación mínima de 2 horas entre commits.
- **Resultados generados y utilizados:**
  - Sección 4 de `docs/formalization.md`: 4-tupla $G=(V, \Sigma, R, S)$, producciones EBNF formales, terminales, no terminales y justificación de Chomsky Tipo 2 frente a lenguajes regulares.
  - Documento de diseño arquitectónico `docs/design_modules.md` que detalla las responsabilidades, entradas y salidas de cada módulo.
- **Adaptaciones y cambios realizados:**
  - Redacción técnica formal en inglés de todos los documentos dentro de `docs/`, conforme a la convención global del proyecto.

---

## Sesión 3 — 2026-10-09 (Edwar Estacio)

- **Fecha:** 2026-10-09
- **Herramienta:** Gemini 3.8 Flash (High) (asistente de código Antigravity)
- **Objetivo:** Implementación del renderizador de visualización (Etapa 4b) en `src/resumelens/render.py` (`to_markdown` y `to_html`) a partir del modelo textX validado, escape estricto de seguridad de entidades HTML y suite de pruebas en `tests/test_render.py`.
- **Prompt base:** Implementación de la visualización en HTML y Markdown consumiendo el modelo validado de textX, gestión de estados vacíos y pruebas unitarias.
- **Aportes y contexto del estudiante:**
  - Definición de los formatos de salida visual (Markdown estructurado y documento HTML autocontenido con CSS semántico).
  - Enfoque preventivo de seguridad: escape obligatorio con `html.escape` para nombres, descripciones y contactos para evitar rotura de maquetación o inyección en el visor.
  - Diseño de estados vacíos y manejo de plurales/fracciones en la experiencia cuando el candidato omite secciones opcionales.
- **Resultados generados y utilizados:**
  - Funciones `to_markdown()` y `to_html()` en `src/resumelens/render.py`.
  - Exportación en `src/resumelens/__init__.py`.
  - Suite de pruebas en `tests/test_render.py` (6 pruebas nuevas, 53 pruebas totales pasando).
- **Adaptaciones y cambios realizados:**
  - Código sin comentarios sobre planes ni tareas.
  - Manejo de tipos para asegurar que solo instancias válidas de modelos textX sean procesadas por el renderizador.

---

## Sesión 4 — 2026-10-09 (Edwar Estacio)

- **Fecha:** 2026-10-09
- **Herramienta:** Gemini 3.8 Flash (High) (asistente de código Antigravity)
- **Objetivo:** Orquestación integral del pipeline en `src/resumelens/pipeline.py` (`run`), resolución dinámica de etapas y soporte de inyección de dependencias para desacoplamiento y pruebas unitarias/de integración, con suite en `tests/test_pipeline.py`.
- **Prompt base:** Implementación de la orquestación del pipeline conectando extracción, normalización, clasificación, DSL y renderizado, verificando invariantes del contrato.
- **Aportes y contexto del estudiante:**
  - Diseño de resolución dinámica para conectar automáticamente los módulos de Alejo y Diego (`extraction.py`, `normalization.py`, `recognition.py`, `profiles.py`) cuando estén listos sin modificar sus archivos.
  - Implementación de fallbacks basados en `vocabulary.json` y perfiles por defecto del contrato para permitir ejecución end-to-end inmediata.
  - Verificación estricta de invariantes 1, 2, 5, 6 y 7 del contrato.
- **Resultados generados y utilizados:**
  - Módulo `src/resumelens/pipeline.py` con función principal `run()`.
  - Exportación en `src/resumelens/__init__.py`.
  - Suite de 6 pruebas unitarias y de integración en `tests/test_pipeline.py` (59 pruebas totales pasando).
- **Adaptaciones y cambios realizados:**
  - Estructuración limpia del orquestador, tipado estricto y manejo de errores con `ExtractionError`.

---

## Sesión 5 — 2026-10-09 (Edwar Estacio)

- **Fecha:** 2026-10-09
- **Herramienta:** Gemini 3.8 Flash (High) (asistente de código Antigravity)
- **Objetivo:** Desarrollo de la interfaz de usuario por línea de comandos (CLI) en `src/resumelens/app.py`, soporte para ejecución como módulo (`python -m resumelens`), exportación de artefactos a disco (`.dsl`, `.html`, `.md`), registro en `pyproject.toml` y suite de pruebas en `tests/test_app.py`.
- **Prompt base:** Implementación de la aplicación de consola (CLI) para procesar archivos de CV, visualización en terminal y exportación de reportes.
- **Aportes y contexto del estudiante:**
  - Definición de parámetros de la CLI (`--output-dir`, `--format`, `--quiet`).
  - Diseño de reporte en terminal con resumen claro de habilidades y veredictos por perfil.
  - Control de códigos de salida del proceso (0 para éxito, códigos no nulos para errores controlados).
  - Pruebas exhaustivas con captura de salida estándar (`capsys`) y directorios temporales (`tmp_path`).
- **Resultados generados y utilizados:**
  - `src/resumelens/app.py` con `main()`, `build_parser()` y `format_summary()`.
  - `src/resumelens/__main__.py` para habilitar `python -m resumelens`.
  - `src/resumelens/__init__.py` exportando `main`.
  - Configuración `[project.scripts]` en `pyproject.toml`.
  - Suite de 5 pruebas unitarias en `tests/test_app.py` (64 pruebas totales pasando).
- **Adaptaciones y cambios realizados:**
  - Código sin comentarios meta de tareas y tipado estricto.

---

## Sesión 6 — 2026-10-10 (Edwar Estacio)

- **Fecha:** 2026-10-10
- **Herramienta:** Gemini 3.8 Flash (High) (asistente de código Antigravity)
- **Objetivo:** Creación de conjunto de datos de prueba realistas en `samples/`, documentación de escenarios de prueba e invariantes formales en `docs/test_cases.md` y suite de pruebas de integración end-to-end en `tests/test_integration.py`.
- **Prompt base:** Creación de casos de prueba realistas en samples/, formalización de escenarios de prueba e invariantes en docs/test_cases.md y pruebas de integración end-to-end.
- **Aportes y contexto del estudiante:**
  - Diseño de 5 currículums representativos en `samples/` cubriendo los 4 perfiles profesionales (Full Stack, ML Engineer, DevOps, Data Engineer) y un caso negativo (candidato con habilidades no técnicas/desconocidas).
  - Verificación formal de invariantes (partición de habilidades, invarianza ante permutación del orden de habilidades en el CV).
  - Documentación técnica estructurada en `docs/test_cases.md` con entradas y veredictos esperados.
- **Resultados generados y utilizados:**
  - 5 archivos de prueba en `samples/`: `wednesday_addams.txt`, `mary_jane_watson.txt`, `linus_torvalds.txt`, `grace_hopper.txt`, `rejected_candidate.txt`.
  - Documento `docs/test_cases.md` formalizando los 5 escenarios y los 7 invariantes.
  - Suite de integración en `tests/test_integration.py` (7 pruebas nuevas, 87 pruebas totales pasando en el repositorio).
- **Adaptaciones y cambios realizados:**
  - Validación de integración exitosa con el módulo `extraction.py` implementado por Alejo tras el merge de la rama remota.

---

## Sesión 7 — 2026-10-10 (Edwar Estacio)

- **Fecha:** 2026-10-10
- **Herramienta:** Gemini 3.8 Flash (High) (asistente de código Antigravity)
- **Objetivo:** Actualización completa del `README.md` (manual de usuario de la CLI, opciones de exportación, tabla de modelos formales, 101 pruebas automatizadas e índice de documentación) y creación de diagramas de arquitectura y secuencia en `docs/diagrams/diagram.md`.
- **Prompt base:** Actualización integral del README principal con guía de CLI, ejemplos con los CVs de muestra y formalización de diagramas del sistema.
- **Aportes y contexto del estudiante:**
  - Estructuración de ejemplos claros de ejecución para cada uno de los cuatro perfiles profesionales.
  - Documentación de opciones de salida (resumen en consola y exportación de archivos `.dsl`, `.html`, `.md`).
  - Definición de diagramas Mermaid para visualización del pipeline y la interacción secuencial de módulos.
- **Resultados generados y utilizados:**
  - `README.md` actualizado con instrucciones de instalación, guía de CLI y tabla de modelos formales.
  - `docs/diagrams/diagram.md` con diagramas de flujo y secuencia en sintaxis Mermaid.
  - 101 pruebas ejecutadas y pasando al 100%.
- **Adaptaciones y cambios realizados:**
  - Redacción en inglés siguiendo las convenciones del repositorio.

---

## Sesión 8 — 2026-10-10 (Edwar Estacio)

- **Fecha:** 2026-10-10
- **Herramienta:** Gemini 3.8 Flash (High) (asistente de código Antigravity)
- **Objetivo:** Redacción de la revisión de literatura académica en `docs/literature_review.md`, cubriendo fundamentos formales (Regex, FST, FSA, CFG), modelado DSL con textX, tabla comparativa de métodos formales vs. probabilísticos/LLMs y citas académicas.
- **Prompt base:** Redacción de la revisión de literatura académica para el póster y reporte técnico, fundamentando la justificación formal y ética del proyecto.
- **Aportes y contexto del estudiante:**
  - Enfoque ético y formal: justificar por qué los modelos deterministas evitan el sesgo algorítmico y la opacidad de los clasificadores de caja negra basados en machine learning o LLMs.
  - Selección y estructuración de 10 referencias académicas clásicas y contemporáneas (Chomsky, Hopcroft, Mohri, Dejanović, O'Neil, etc.).
- **Resultados generados y utilizados:**
  - `docs/literature_review.md` con revisión teórica completa, tabla comparativa y referencias académicas en formato APA/IEEE.
- **Adaptaciones y cambios realizados:**
  - Redacción en inglés formal y rigor matemático en la nomenclatura.

---

## Sesión 9 — 2026-10-09 / 2026-10-10 (Juan Diego Balanta Molina — Diego)

- **Fechas:** 2026-10-09 y 2026-10-10 (trabajo distribuido en commits separados por al menos 2 horas).
- **Herramienta:** Claude (Anthropic), en una sesión de trabajo con acceso al repositorio.
- **Objetivo:** Revisión del repositorio y corrección del andamiaje; módulos compartidos del contrato; parte de Diego: perfiles (`profiles/*.json`, `profiles.py`), ordenamiento (`sorting.py`), autómatas de reconocimiento (`recognition.py`), diagramas (`diagrams.py`), formalización de la Etapa 3, revisión de literatura, documentación de perfiles, casos de prueba y diseño de módulos.
- **Contenido propio entregado a la IA:**
  - Enunciado de la tarea integradora (PDF de la asignatura).
  - Repositorio del equipo, incluido el contrato de interfaces (`docs/contracts.md`) y el plan de división del trabajo acordado por el equipo (Alejo, Diego, Edwar).
  - Restricciones del estudiante: mínimo 10 commits por integrante con al menos 2 horas entre cada uno, commits a su nombre, trabajo de Diego en la rama `diego/profiles-recognition`, sin incluir diapositivas en el cronograma.
- **Prompts principales (literales):**
  - "Revisa y analiza el repo que tenemos hasta ahora, tengo entendido que ya mi compañero Alejandro ha avanzado y nos dividió el trabajo pero lo hizo como por persona y no por nombre exacto, revisa todo antes de empezar a codear"
  - "Arranca solucionando todos los problemas, ademas son 10 commits cada uno cada 2 horas, toma las decisiones pertinentes y subelo directo a la Main, con base a eso ya luego me colocas a mi una asignacion de commits que hacer para terminar todo lo mio con minimo 10 commits"
  - "Es que son 10 cada uno, organiza nuestro cronograma interno, no tengas en mente las diapositivas"
- **Resultados generados y utilizados:**
  - Corrección del andamiaje: `__init__.py`, `requirements.txt`, `pyproject.toml`, `.gitattributes`, `.gitignore`, `candidate.tx`; módulos compartidos `models.py`, `errors.py`, `vocabulary.py`, `vocabulary.json`.
  - Perfiles y cargador con las validaciones de la Sección 7.3 del contrato; ordenamiento por perfil; un ε-NFA por perfil construido desde los slots, DFA equivalente y DFA mínimo; exportación de la 5-tupla; diagramas Mermaid/Graphviz/SVG.
  - Documentos: sección 3 de `docs/formalization.md`, `docs/literature_review.md`, `docs/profiles.md`, sección 4 de `docs/test_cases.md`, secciones 3.3–3.6 de `docs/design_modules.md`.
  - Pruebas: `test_vocabulary.py`, `test_models.py`, `test_profiles.py`, `test_sorting.py`, `test_recognition.py`, `test_automata.py`, `test_diagrams.py`, `test_recognition_scenarios.py`.
- **Decisiones y cambios respecto a lo generado:**
  - Se quitó la atribución de coautoría de la IA de los mensajes de commit por decisión del estudiante.
  - El ejemplo de `classify` de la Sección 6.4 del contrato tenía un error (secuencia vacía para Full Stack); las pruebas lo detectaron y se corrigió en el contrato (v1.3).
  - Las referencias de la revisión de literatura se verificaron en ACL Anthology y en las páginas de los editores; se eliminaron los datos bibliográficos que no se pudieron confirmar.
  - Al integrar `main` se corrigió la ruta fija `"profiles/"` del pipeline para que funcione fuera de la raíz del repositorio.
- **Participación y verificación del estudiante:**
  - Definió las restricciones de trabajo: 10 commits por integrante con al menos 2 horas entre cada uno, commits a su nombre y sin atribución de coautoría a la IA, trabajo en la rama `diego/profiles-recognition`.
  - Aprobó el cronograma de commits y el alcance de cada uno, y pidió excluir las diapositivas del cronograma interno.
  - Hizo el push de cada commit desde su equipo y abrió y unió el Pull Request #1 (`diego/profiles-recognition` → `main`).
  - Revisó los resúmenes de avance entregados por la IA en cada paso (estado de commits, resultados de las pruebas y clasificación de las hojas de vida de `samples/`).

---

## Sesión 10 — 2026-10-12 (Edwar Estacio)

- **Fecha:** 2026-10-12
- **Herramienta:** Gemini 3.8 Flash (High) (asistente de código Antigravity)
- **Objetivo:** Creación del póster de investigación en inglés (`docs/poster.md`) que sintetiza los 4 modelos computacionales, la arquitectura del pipeline, los resultados experimentales y la justificación ética y técnica.
- **Prompt base:** Redacción del póster de investigación en inglés en cumplimiento del entregable académico de la asignatura.
- **Aportes y contexto del estudiante:**
  - Estructuración de los paneles en formato A0 vertical (Motivation, Computational Models, Pipeline Architecture, Models in Action, Results, Discussion).
  - Resumen formal de las cuatro etapas del pipeline integrando el trabajo de los tres miembros del equipo.
  - Verificación de métricas experimentales (249 pruebas pasando al 100%, invarianza ante permutación y robustez ante ruido).
- **Resultados generados y utilizados:**
  - `docs/poster.md` con el diseño completo del póster de investigación en inglés.
- **Adaptaciones y cambios realizados:**
  - Redacción en inglés formal y alineación con la literatura y formalización del repositorio.

---

## Sesión 11 — 2026-10-12 (Juan Diego Balanta Molina — Diego)

- **Fecha:** 2026-10-12
- **Herramienta:** Claude (Anthropic), en una sesión de trabajo con acceso al repositorio.
- **Objetivo:** Revisar el estado de `main` frente a la tarea integradora y corregir los problemas de documentación encontrados.
- **Prompts principales (literales):**
  - "Revisa la main para saber como estamos en completitud de la tarea"
  - "Hay algo que pueda hacer yo? (Es decir mi Claude)"
  - "Bueno, haz lo que puedas hacer tu y lo subes a main"
- **Resultados generados y utilizados:**
  - Revisión de `main`: 249 pruebas pasando y el CLI con los resultados esperados para las 5 hojas de vida de `samples/`.
  - `docs/literature_review.md`: numeración de secciones corregida tras el merge (faltaba la sección 2), cita de Sipser unificada (2012), referencias que faltaban (Chomsky 1956, Ford 2004, Friedl 2006) y datos completos de Dejanović et al. (2017). La fila de riesgo ético de la tabla comparativa se reformuló: el sistema no "elimina" el sesgo, porque la elección de perfiles, vocabulario y alias es humana.
  - `docs/formalization.md`: niveles de título de las Partes 1 y 2 alineados con las secciones 3 y 4 (sin cambios de contenido).
  - `docs/contracts.md` v1.4: cerrados los puntos abiertos ya resueltos (alias, tipo de autómata, EBNF).
  - `README.md`: número de pruebas actualizado (249) y enlaces a `profiles.md` y `literature_review.md`.
  - Este registro: la segunda "Sesión 8" pasa a ser la Sesión 9.
- **Decisiones y cambios respecto a lo generado:**
  - Los perfiles 3 y 4 siguen marcados como provisionales hasta que el profesor confirme sus requisitos.
  - No se modificó el contenido técnico de las secciones de Alejo y Edwar, solo la numeración, las citas y una afirmación de la tabla comparativa.
- **Participación y verificación del estudiante:**
  - Pidió la revisión de `main` y decidió qué correcciones hacer y subir.
  - Hizo el commit y el push de los cambios desde su equipo.

---

## Sesión 12 — 2026-10-12 (Juan Diego Balanta Molina — Diego)

- **Fecha:** 2026-10-12
- **Herramienta:** Claude (Anthropic), en una sesión de trabajo con acceso al repositorio.
- **Objetivo:** Revisar el estado del repositorio frente a los entregables y cerrar pendientes de documentación.
- **Prompts principales (literales):**
  - "Analiza el estado del repositorio y haz una tabla con lo que nos falta por hacer"
  - "No tengo mucho tiempo, haz el pendiente 3, 8 que usamos intellij, el 9 encargate tu, 10 tambien y 12... el tema de los commits en personal, 10 cada uno cada 2 horas minimos confirmado y la fecha limite la movieron para hoy 12"
- **Contenido propio entregado a la IA:** confirmación del IDE usado por el equipo (IntelliJ IDEA), de la regla de commits (10 por integrante, 2 horas entre los commits de cada uno) y de la nueva fecha límite (12 de octubre).
- **Resultados generados y utilizados:**
  - Tabla de pendientes del repositorio (presentación, póster visual, conteo y separación de commits por integrante, perfiles provisionales).
  - `docs/test_cases.md`: secciones 5 (etapas 1 y 2) y 6 (etapa 4) que documentan las pruebas existentes de Alejo y Edwar; fila de `test_normalization.py` en la tabla de módulos.
  - `README.md`: IDE usado (IntelliJ IDEA).
  - Este registro: numeración de sesiones corregida y sección de participación del estudiante completada.
  - `samples/here_dataset.md` se mantiene: aunque solo contiene un marcador, `tests/test_stage1_2.py` lo usa como caso de archivo sin hoja de vida (salida vacía).
  - Prompt adicional: "La presentacion imagino que es un video, la vamos a subir a este drive para que edites el readme o no se, donde el profe pueda ver y entrar al link: [enlace de Drive] ... el pendiente 4 ya no hay tiempo de hablar con el profesor, asi que toma decisiones y arreglalo tu, y pendiente 5 yo no se"
  - `README.md`: enlace a la carpeta de Drive con el video de la presentación y el póster; nota de que la interfaz de usuario es la aplicación de línea de comandos y el reporte HTML su salida visual.
  - `docs/contracts.md` v1.5 (decisión D11), `docs/profiles.md` y `docs/formalization.md`: los perfiles DevOps Engineer y Data Engineer quedan como definitivos.
- **Decisiones y cambios respecto a lo generado:**
  - Las secciones nuevas de `test_cases.md` describen pruebas que ya existían; no se cambió código ni pruebas.
- **Participación y verificación del estudiante:**
  - Eligió qué pendientes resolver y confirmó el IDE, la regla de commits y la fecha límite.
  - Indicó la carpeta de Drive para los entregables y delegó las decisiones sobre los perfiles propios y la interfaz.
  - Hizo el push del commit desde su equipo.
