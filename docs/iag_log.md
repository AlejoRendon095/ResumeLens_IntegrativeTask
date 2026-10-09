# AI Usage Log (Registro de Uso de IA)

Registro de interacciones con herramientas de inteligencia artificial generativa durante el desarrollo del proyecto ResumeLens, en cumplimiento de los requisitos de la asignatura Computación y Estructuras Discretas 3.

---

## Sesión 1 — (Edwar Estacio)

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
