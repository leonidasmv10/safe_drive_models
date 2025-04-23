# Safe Drive Models

Este repositorio contiene modelos de inteligencia artificial para la detección de sonidos críticos para la conducción segura.

## Descripción

Safe Drive Models utiliza técnicas de deep learning para detectar sonidos relevantes para la seguridad vial como:
- Sirenas de emergencia
- Bocinas de vehículos
- Otros sonidos de alerta

El objetivo es potenciar sistemas de asistencia a la conducción que puedan alertar a conductores sobre sonidos importantes en el entorno.

## Estructura del Proyecto

- `critical_sound_detector_model.ipynb`: Notebook principal con el modelo de detección de sonidos críticos
- `critical_sound_detector_model.h5`: Modelo entrenado guardado en formato H5
- `datasets/`: Contiene los datasets de audio organizados por categorías
- `audio_test/`: Muestras de audio para probar el modelo
- `EDA_*.ipynb`: Notebooks de análisis exploratorio de diferentes datasets

## Instalación

1. Clona este repositorio
2. Ejecuta el script de instalación de dependencias:
   ```
   ./install_dependencies.bat
   ```
3. Activa el entorno virtual:
   ```
   .\env\Scripts\activate
   ```

## Recursos Externos

- [Audiomentations](https://github.com/iver56/audiomentations): Librería para augmentación de datos de audio
- [Dataset de sonidos urbanos](https://data.mendeley.com/datasets/y5stjsnp8s/2)
