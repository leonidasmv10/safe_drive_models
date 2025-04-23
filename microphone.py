import pyaudio
import wave
import numpy as np
import matplotlib.pyplot as plt
from IPython.display import Audio, display, clear_output
import time
import threading
import cv2
import ipywidgets as widgets


class DispositivosUSB:
    """
    Clase para gestionar cámaras USB y sus micrófonos integrados.
    Identifica los dispositivos por nombre para mantener consistencia
    incluso cuando los IDs del sistema cambian.
    """

    def __init__(self):
        """Inicializa la clase y busca los dispositivos disponibles"""
        self.microfonos = {}
        self.camaras = {}
        self.pares_dispositivos = []
        self.patrones_nombres = ["USB Camera", "2- USB Camera", "3- USB Camera"]

        # Buscar dispositivos al inicializar
        self.buscar_dispositivos()

    def buscar_dispositivos(self):
        """Busca todos los micrófonos y cámaras USB disponibles"""
        self.buscar_microfonos()
        self.buscar_camaras()
        self.emparejar_dispositivos()

        return {
            "microfonos": self.microfonos,
            "camaras": self.camaras,
            "pares": self.pares_dispositivos,
        }

    def buscar_microfonos(self):
        """Busca micrófonos por patrones de nombre específicos"""
        try:
            p = pyaudio.PyAudio()
            info = p.get_host_api_info_by_index(0)
            num_devices = info.get("deviceCount")

            microfonos_encontrados = {}

            for i in range(num_devices):
                try:
                    device_info = p.get_device_info_by_index(i)
                    if device_info.get("maxInputChannels") > 0:
                        nombre = device_info.get("name")

                        # Verificar si coincide con alguno de nuestros patrones
                        for patron in self.patrones_nombres:
                            if patron in nombre:
                                microfonos_encontrados[i] = {
                                    "id": i,
                                    "nombre": nombre,
                                    "patron": patron,
                                    "canales": device_info.get("maxInputChannels"),
                                }
                                print(
                                    f"Micrófono {i}: {nombre}, {device_info.get('maxInputChannels')} canales"
                                )
                                break
                except Exception as e:
                    print(f"Error al acceder al dispositivo {i}: {e}")

            p.terminate()
            self.microfonos = microfonos_encontrados

        except Exception as e:
            print(f"Error al buscar micrófonos: {e}")
            self.microfonos = {}

    def buscar_camaras(self):
        """Busca cámaras disponibles"""
        camaras_encontradas = {}

        for i in range(4):  # Intentamos con índices 0, 1, 2, 3
            try:
                cap = cv2.VideoCapture(i)
                if cap.isOpened():
                    # Leer propiedades
                    ancho = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                    alto = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    fps = cap.get(cv2.CAP_PROP_FPS)

                    # Capturar frame para verificar
                    ret, frame = cap.read()

                    if ret:
                        # Guardar información
                        camaras_encontradas[i] = {
                            "id": i,
                            "resolucion": f"{ancho}x{alto}",
                            "fps": fps,
                        }

                        print(f"Cámara {i} encontrada: {ancho}x{alto}, {fps} FPS")

                    cap.release()
                else:
                    print(f"No se pudo abrir la cámara {i}")
            except Exception as e:
                print(f"Error al acceder a la cámara {i}: {e}")
                try:
                    cap.release()
                except:
                    pass

        self.camaras = camaras_encontradas

    def emparejar_dispositivos(self):
        """Intenta emparejar micrófonos y cámaras basándose en patrones de nombres"""
        pares = []

        # Ordenar micrófonos por el patrón
        microfonos_ordenados = sorted(
            self.microfonos.items(),
            key=lambda x: (
                0
                if x[1]["patron"] == "USB Camera"
                else 1 if x[1]["patron"] == "2- USB Camera" else 2
            ),
        )

        # Ordenar cámaras por ID
        camaras_ordenadas = sorted(self.camaras.items(), key=lambda x: x[0])

        # Intentar emparejar
        for i, (mic_id, mic_info) in enumerate(microfonos_ordenados):
            if i < len(camaras_ordenadas):
                # Asignar la cámara correspondiente por orden
                cam_id, cam_info = camaras_ordenadas[i]
                pares.append(
                    {
                        "mic_id": mic_id,
                        "camara_id": cam_id,
                        "nombre_mic": mic_info["nombre"],
                        "info_camara": cam_info,
                    }
                )
                print(
                    f"Emparejado: Micrófono {mic_id} ({mic_info['patron']}) con Cámara {cam_id}"
                )
            else:
                # No hay suficientes cámaras
                pares.append(
                    {
                        "mic_id": mic_id,
                        "camara_id": None,
                        "nombre_mic": mic_info["nombre"],
                        "info_camara": None,
                    }
                )
                print(f"Micrófono {mic_id} ({mic_info['patron']}) sin cámara asociada")

        self.pares_dispositivos = pares

    def capturar_imagen(self, camara_id):
        """Captura una imagen de la cámara especificada"""
        try:
            cap = cv2.VideoCapture(camara_id)
            if not cap.isOpened():
                print(f"No se pudo abrir la cámara {camara_id}")
                return None

            ret, frame = cap.read()
            cap.release()

            if ret:
                # Convertir de BGR a RGB para mostrar correctamente
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                return frame_rgb
            else:
                print(f"No se pudo capturar imagen de la cámara {camara_id}")
                return None
        except Exception as e:
            print(f"Error al capturar imagen: {e}")
            try:
                cap.release()
            except:
                pass
            return None

    def grabar_audio(self, mic_id, duracion=5, nombre_archivo=None):
        """Graba audio desde el micrófono especificado"""
        if nombre_archivo is None:
            nombre_archivo = f"grabacion_mic_{mic_id}.wav"

        p = None
        stream = None

        try:
            CHUNK = 1024
            FORMAT = pyaudio.paInt16
            CHANNELS = 1
            RATE = 44100

            p = pyaudio.PyAudio()

            # Verificar si el dispositivo existe
            device_info = p.get_device_info_by_index(mic_id)
            if device_info.get("maxInputChannels") <= 0:
                print(f"El dispositivo {mic_id} no tiene canales de entrada")
                return None

            # Abrir el stream
            stream = p.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                input_device_index=mic_id,
                frames_per_buffer=CHUNK,
            )

            print(f"Grabando desde micrófono {mic_id} durante {duracion} segundos...")

            frames = []
            for i in range(0, int(RATE / CHUNK * duracion)):
                data = stream.read(CHUNK, exception_on_overflow=False)
                frames.append(data)

            print(f"Grabación completada para micrófono {mic_id}")

            # Detener y cerrar el stream
            stream.stop_stream()
            stream.close()

            # Guardar la grabación
            wf = wave.open(nombre_archivo, "wb")
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(p.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b"".join(frames))
            wf.close()

            return nombre_archivo

        except Exception as e:
            print(f"Error al grabar audio: {e}")
            return None

        finally:
            if stream is not None:
                try:
                    stream.stop_stream()
                    stream.close()
                except:
                    pass

            if p is not None:
                try:
                    p.terminate()
                except:
                    pass

    def grabar_audio_simultaneo(self, ids_microfonos, duracion=5):
        """Graba audio simultáneamente desde múltiples micrófonos"""
        # Crear hilos para grabación simultánea
        hilos = []
        archivos = {}

        for mic_id in ids_microfonos:
            nombre_archivo = f"grabacion_microfono_{mic_id}.wav"
            hilo = threading.Thread(
                target=self.grabar_audio, args=(mic_id, duracion, nombre_archivo)
            )
            hilos.append(hilo)
            archivos[mic_id] = nombre_archivo

        # Iniciar todos los hilos
        print(f"Iniciando grabación simultánea desde {len(hilos)} micrófonos...")
        for hilo in hilos:
            hilo.start()

        # Esperar a que todos terminen
        for hilo in hilos:
            hilo.join()

        print("Todas las grabaciones completadas")

        # Mostrar resultados
        for mic_id, archivo in archivos.items():
            print(f"Grabación del micrófono {mic_id}: {archivo}")
            if archivo is not None:
                display(Audio(archivo))

        return archivos

    def grabar_video_con_audio(
        self, camara_id, mic_id, duracion=5, nombre_base="grabacion"
    ):
        """Graba video y audio usando la cámara y micrófono especificados"""
        nombre_video = f"{nombre_base}_cam{camara_id}_mic{mic_id}.avi"
        nombre_audio = f"{nombre_base}_mic{mic_id}.wav"

        # Configuración para video
        fourcc = cv2.VideoWriter_fourcc(*"XVID")
        fps = 20.0

        # Abrir cámara y obtener resolución
        cap = cv2.VideoCapture(camara_id)
        if not cap.isOpened():
            print(f"No se pudo abrir la cámara {camara_id}")
            return None, None

        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        frame_size = (width, height)

        # Crear objeto VideoWriter
        video_writer = cv2.VideoWriter(nombre_video, fourcc, fps, frame_size)

        # Iniciar grabación de audio en un hilo separado
        audio_thread = threading.Thread(
            target=self.grabar_audio, args=(mic_id, duracion, nombre_audio)
        )
        audio_thread.start()

        # Grabación de video
        inicio = time.time()
        frames_capturados = 0

        try:
            while time.time() - inicio < duracion:
                ret, frame = cap.read()
                if not ret:
                    break

                # Guardar el frame
                video_writer.write(frame)
                frames_capturados += 1

                # Mostrar progreso
                if frames_capturados % 10 == 0:
                    clear_output(wait=True)
                    print(
                        f"Grabando... Tiempo transcurrido: {time.time() - inicio:.1f} segundos de {duracion}"
                    )

        except Exception as e:
            print(f"Error durante la grabación de video: {e}")

        finally:
            # Limpiar recursos
            cap.release()
            video_writer.release()

            # Esperar a que termine la grabación de audio
            audio_thread.join()

        print(f"Grabación completada. Video: {nombre_video}, Audio: {nombre_audio}")
        return nombre_video, nombre_audio

    def ver_camara_tiempo_real(self, camara_id):
        """Muestra la cámara en tiempo real"""
        # Inicializar la cámara
        cap = cv2.VideoCapture(camara_id)
        if not cap.isOpened():
            print(f"No se pudo abrir la cámara {camara_id}")
            return
    
        print(f"Mostrando video en tiempo real de la cámara {camara_id}. Presiona 'q' para salir.")
        
        try:
            while True:
                # Capturar frame por frame
                ret, frame = cap.read()
                
                if not ret:
                    print("Error al capturar el frame")
                    break
                
                # Mostrar el frame resultante
                cv2.imshow(f'Cámara {camara_id} en tiempo real', frame)
                
                # Salir si se presiona la tecla 'q'
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                
        finally:
            # Cuando todo está hecho, liberar los recursos
            cap.release()
            cv2.destroyAllWindows()
    

    def crear_interfaz(self):
        """Crea una interfaz para interactuar con los dispositivos"""
        if not self.microfonos:
            print("No se encontraron micrófonos USB. Ejecutando nueva búsqueda...")
            self.buscar_dispositivos()

            if not self.microfonos:
                print(
                    "No se pudieron encontrar micrófonos USB. Verifica que estén conectados."
                )
                return

        # Opciones para el selector de dispositivo
        opciones_dispositivo = []
        for i, par in enumerate(self.pares_dispositivos):
            if par["camara_id"] is not None:
                etiqueta = f"Mic: {par['nombre_mic']} + Cámara {par['camara_id']}"
            else:
                etiqueta = f"Mic: {par['nombre_mic']} - Sin cámara"
            opciones_dispositivo.append((etiqueta, i))

        # Widget para seleccionar dispositivo
        dispositivo_selector = widgets.Dropdown(
            options=opciones_dispositivo,
            description="Dispositivo:",
            disabled=False,
        )

        # Widget para ajustar duración
        duracion_slider = widgets.IntSlider(
            value=5, min=1, max=30, step=1, description="Duración:", disabled=False
        )

        # Botones para acciones
        boton_capturar = widgets.Button(
            description="Capturar Imagen",
            button_style="success",
            tooltip="Capturar imagen de la cámara seleccionada",
        )

        boton_grabar = widgets.Button(
            description="Grabar Audio+Video",
            button_style="info",
            tooltip="Grabar audio y video del dispositivo seleccionado",
        )

        boton_grabar_todos = widgets.Button(
            description="Grabar Todos",
            button_style="danger",
            tooltip="Grabar audio de todos los micrófonos a la vez",
        )

        # Output para mostrar resultados
        output = widgets.Output()

        # Funciones para manejar clicks en botones
        def on_boton_capturar_clicked(b):
            with output:
                clear_output()
                idx = dispositivo_selector.value
                par = self.pares_dispositivos[idx]

                if par["camara_id"] is None:
                    print("Este micrófono no tiene cámara asociada")
                    return

                print(f"Capturando imagen de la cámara {par['camara_id']}...")
                imagen = self.capturar_imagen(par["camara_id"])

                if imagen is not None:
                    plt.figure(figsize=(8, 6))
                    plt.imshow(imagen)
                    plt.title(f"Imagen de la cámara {par['camara_id']}")
                    plt.axis("off")
                    plt.show()
                else:
                    print("Error al capturar la imagen")

        def on_boton_grabar_clicked(b):
            with output:
                clear_output()
                idx = dispositivo_selector.value
                par = self.pares_dispositivos[idx]
                duracion = duracion_slider.value

                if par["camara_id"] is None:
                    print(f"Solo grabando audio del micrófono {par['mic_id']}...")
                    archivo_audio = self.grabar_audio(
                        par["mic_id"], duracion, f"solo_audio_mic{par['mic_id']}.wav"
                    )
                    if archivo_audio:
                        print("Reproduciendo audio grabado:")
                        display(Audio(archivo_audio))
                else:
                    print(f"Grabando video y audio del dispositivo #{idx+1}...")
                    print(f"Cámara {par['camara_id']} + Micrófono {par['mic_id']}")

                    video_file, audio_file = self.grabar_video_con_audio(
                        par["camara_id"],
                        par["mic_id"],
                        duracion,
                        f"grabacion_dispositivo{idx+1}",
                    )

                    if audio_file:
                        print("Reproduciendo audio grabado:")
                        display(Audio(audio_file))

        def on_boton_grabar_todos_clicked(b):
            with output:
                clear_output()
                duracion = duracion_slider.value

                # Extraer todos los IDs de micrófono
                ids_microfono = [par["mic_id"] for par in self.pares_dispositivos]

                print(
                    f"Grabando audio de los {len(ids_microfono)} micrófonos durante {duracion} segundos..."
                )
                self.grabar_audio_simultaneo(ids_microfono, duracion)

        # Conectar eventos
        boton_capturar.on_click(on_boton_capturar_clicked)
        boton_grabar.on_click(on_boton_grabar_clicked)
        boton_grabar_todos.on_click(on_boton_grabar_todos_clicked)

        # Mostrar la interfaz
        display(
            widgets.VBox(
                [
                    dispositivo_selector,
                    duracion_slider,
                    widgets.HBox([boton_capturar, boton_grabar, boton_grabar_todos]),
                    output,
                ]
            )
        )

    def obtener_microfono_por_nombre(self, patron):
        """
        Busca un micrófono específico por un patrón en su nombre
        Devuelve el ID del primer micrófono que coincida
        """
        for mic_id, info in self.microfonos.items():
            if patron in info["nombre"]:
                return mic_id
        return None

    def obtener_ids_microfonos(self):
        """Devuelve los IDs de todos los micrófonos encontrados"""
        return list(self.microfonos.keys())

    def obtener_pares_camara_microfono(self):
        """Devuelve los pares de cámara-micrófono emparejados"""
        return self.pares_dispositivos
