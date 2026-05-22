#Proyecto de Automatización Sprint 9 sobre: Urban Routes
# Este proyecto contiene pruebas automatizadas diseñada para validar de principio a fin el flujo de reservación y solicitud de taxis en la aplicación web Urban Route.

El objetivo principal es asegurar que los usuarios puedan configurar su viaje, personalizar sus opciones y pedir un vehículo sin experimentar bugs.

---

#Descripción — ¿Qué hace el proyecto?

La automatización se encarga de realizar de forma autónoma las siguientes acciones en la web:

1.Configurar la ruta: Ingresa las direcciones (`East 2nd Street, 601`) y destino (`1300 1st St`).
2.Seleccionar tarifa: Elige la opción de tarifa Comfort.
3. Validación telefónica: Registra un número de teléfono e intercepta de forma inteligente el código SMS de confirmación directamente desde el backend.
4. Método de pago: Agrega una tarjeta de crédito, maneja la pérdida de enfoque (focus) mediante la tecla `TAB` para activar el botón de guardado y enlaza la tarjeta.
5. Notas especiales: Escribe un mensaje personalizado para el conductor.
6. Servicios adicionales:Activa la casilla para pedir mantas/pañuelos e incrementa el contador para ordenar exactamente 2 helados.
7. Confirmación Presiona el botón final, valida que aparezca el modal de búsqueda y espera a que el sistema asigne un conductor.

Toda la lógica de las interacciones vive en la clase `UrbanRoutesPage`, mientras que las comprobaciones reales (`assert`) se ejecutan cronológicamente dentro de `TestUrbanRoutes`.


#Tecnologías y herramientas usadas

Para este proyecto utilizamos un stack moderno enfocado en QA Automation:

Python
Selenium WebDriver
Pytest
Chrome


# Instrucciones para ejecutar las pruebas

Sigue estos sencillos pasos:

 1. Preparar el entorno (Consola/Terminal)
2. Verificar los archivos
Asegúrate de que en la misma carpeta tengas los archivos clave:
data.py: Contiene las direcciones, URL, tarjetas y textos de prueba.
main.py: Contiene los Page Objects, el código y las pruebas en si.