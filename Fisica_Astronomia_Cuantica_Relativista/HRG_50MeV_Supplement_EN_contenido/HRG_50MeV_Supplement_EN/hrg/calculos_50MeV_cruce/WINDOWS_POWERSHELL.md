# Ejecutar el cálculo HRG en Windows

PowerShell organiza la ejecución y comprueba los archivos. Python realiza las
integrales y los cálculos numéricos. El paquete incluye los inventarios de
partículas, los datos calculados y la figura.

## 1. Instalar PowerShell 7

Abre **Inicio**, escribe **Windows PowerShell** y ábrelo. Copia este comando y
presiona Enter:

```powershell
winget install --id Microsoft.PowerShell --source winget
```

Sigue los mensajes del instalador. Al terminar, cierra esa ventana, busca
**PowerShell 7** en Inicio y ábrelo. Comprueba la versión:

```powershell
$PSVersionTable.PSVersion
```

La columna `Major` debe mostrar **7**. PowerShell 7 se instala junto a Windows
PowerShell 5.1.

Si Windows no reconoce `winget`, usa la instalación oficial de Microsoft:
<https://learn.microsoft.com/powershell/scripting/install/install-powershell-on-windows>.

## 2. Instalar Python 3.12

Descarga **Python Install Manager** desde la página oficial:
<https://www.python.org/downloads/windows/>. Abre el instalador y sigue sus
indicaciones. Después, cierra y vuelve a abrir PowerShell 7.

Instala la versión usada para verificar este cálculo:

```powershell
pymanager install 3.12
```

Comprueba que está disponible:

```powershell
py -3.12 --version
```

Debe aparecer `Python 3.12` seguido del número de actualización. Si ya tienes
Python 3.12 y ese comando funciona, puedes continuar con el paso siguiente.

## 3. Extraer el paquete completo

Descarga el ZIP del artículo o del cálculo. En el Explorador de archivos, haz clic derecho sobre
él y selecciona **Extraer todo**. No ejecutes el cálculo dentro del ZIP.

Entra en la carpeta **`calculos_50MeV_cruce`**, que contiene estos archivos:

- `ejecutar_50MeV.ps1`
- `comparar_50MeV.py`
- `requirements.txt`
- `provenance.json`

Windows puede crear una carpeta exterior adicional durante la extracción.
Necesitas la carpeta que contiene los cuatro archivos anteriores.

Copia su ruta completa desde la barra de direcciones del Explorador. En
PowerShell 7, sustituye el texto del ejemplo por esa ruta; conserva las comillas:

```powershell
Set-Location -LiteralPath 'PEGAR_AQUI_LA_RUTA_COMPLETA'
```

Las comillas permiten usar rutas que contienen espacios.

## 4. Ejecutar el cálculo

Primera ejecución:

```powershell
.\ejecutar_50MeV.ps1 -InstalarDependencias
```

El archivo comprueba los SHA-256 de los inventarios, crea un entorno Python
local llamado `.venv`, instala las versiones fijadas de las dependencias y
ejecuta el cálculo. Esta instalación inicial requiere conexión a Internet.

Para repetir después, desde la misma carpeta:

```powershell
.\ejecutar_50MeV.ps1
```

El cálculo utiliza los inventarios incluidos; no consulta páginas web.

## 5. Verificar la salida

Entre los resultados PDG2025 deben aparecer, al redondeo mostrado:

| Magnitud | Resultado esperado |
|---|---:|
| Bariones a 50 MeV, por cm³ | 2.726090 × 10³⁰ |
| Antibariones a 50 MeV, por cm³ | 2.717213 × 10³⁰ |
| Antibariones / exceso neto a 50 MeV | 306.114688 |
| Temperatura del cruce R = 1 | 38.203739 MeV |

Los resultados completos quedan en **`data`**, las verificaciones numéricas en
**`data/validacion.json`** y la figura en **`figures`**. Los números son resultados
de equilibrio HRG bajo los supuestos descritos en `README.md`.

Si aparece un error, conserva su texto completo y el comando que ejecutaste.
Esta guía no cambia las políticas de ejecución de Windows.

## Alcance de la verificación

Los cálculos y sus comprobaciones se ejecutaron localmente en Python 3.12 sobre
Linux. El archivo PowerShell se revisó estáticamente; **no se ha ejecutado ni
certificado en Windows** en este entorno.

## Documentación oficial

- Microsoft, instalación de PowerShell en Windows:
  <https://learn.microsoft.com/powershell/scripting/install/install-powershell-on-windows>
- Python, descargas para Windows:
  <https://www.python.org/downloads/windows/>
- Python, instalación y selección de versiones en Windows:
  <https://docs.python.org/3/using/windows.html>
