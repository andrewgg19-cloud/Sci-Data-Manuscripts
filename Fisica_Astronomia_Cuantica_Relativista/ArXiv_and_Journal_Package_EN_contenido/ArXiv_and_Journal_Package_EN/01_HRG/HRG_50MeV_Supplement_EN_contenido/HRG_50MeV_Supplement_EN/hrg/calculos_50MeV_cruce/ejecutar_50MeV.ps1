# Ejecuta el calculo local, verifica los datos y muestra el resultado.
# Compatible por diseno con Windows PowerShell 5.1 y PowerShell 7.
# Python realiza las integrales y las raices; PowerShell controla la ejecucion.
[CmdletBinding()]
param([switch]$InstalarDependencias)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$analysisRoot = $PSScriptRoot

Push-Location -LiteralPath $analysisRoot
try {
    $sourceManifest = Get-Content -LiteralPath (Join-Path $analysisRoot 'provenance.json') -Raw -Encoding UTF8 | ConvertFrom-Json
    foreach ($catalogName in @('PDG2014', 'PDG2020', 'PDG2025')) {
        $catalogPath = Join-Path $analysisRoot ('catalogs/' + $catalogName + '_list.dat')
        $expectedHash = $sourceManifest.catalogs.$catalogName.sha256
        $actualHash = (Get-FileHash -LiteralPath $catalogPath -Algorithm SHA256).Hash.ToLowerInvariant()
        if ($actualHash -ne $expectedHash) {
            throw ('El SHA-256 no coincide para ' + $catalogName + '. Revise el archivo antes de calcular.')
        }
    }
    Write-Host 'Inventarios de particulas: SHA-256 verificado.'

    $pythonLauncher = $null
    $launcherArgs = @()
    $candidates = @(
        @{ Name = 'py'; Arguments = @('-3.12') },
        @{ Name = 'py'; Arguments = @('-3') },
        @{ Name = 'python'; Arguments = @() },
        @{ Name = 'python3'; Arguments = @() }
    )
    foreach ($candidate in $candidates) {
        $candidateCommand = Get-Command -Name $candidate.Name -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($null -eq $candidateCommand) { continue }
        $candidateArgs = @($candidate.Arguments)
        try {
            & $candidateCommand.Source @candidateArgs -c 'import sys; sys.exit(0 if sys.version_info >= (3, 11) else 2)' 2>$null
        } catch {
            continue
        }
        if ($LASTEXITCODE -eq 0) {
            $pythonLauncher = $candidateCommand.Source
            $launcherArgs = $candidateArgs
            break
        }
    }
    if ($null -eq $pythonLauncher) {
        throw 'Se necesita Python 3.11 o posterior; la corrida incluida fue verificada con Python 3.12.'
    }

    $venvRoot = Join-Path $analysisRoot '.venv'
    $windowsPython = Join-Path $venvRoot 'Scripts/python.exe'
    $unixPython = Join-Path $venvRoot 'bin/python'
    if (-not (Test-Path -LiteralPath $windowsPython) -and -not (Test-Path -LiteralPath $unixPython)) {
        & $pythonLauncher @launcherArgs -m venv $venvRoot
        if ($LASTEXITCODE -ne 0) { throw 'No se pudo crear el entorno local de Python.' }
    }
    if (Test-Path -LiteralPath $windowsPython) {
        $analysisPython = $windowsPython
    } else {
        $analysisPython = $unixPython
    }
    & $analysisPython -c 'import sys; sys.exit(0 if sys.version_info >= (3, 11) else 2)'
    if ($LASTEXITCODE -ne 0) {
        throw 'El entorno .venv existente usa un Python incompatible; use una carpeta nueva del paquete con Python 3.11 o posterior.'
    }

    if ($InstalarDependencias) {
        & $analysisPython -m pip install -r (Join-Path $analysisRoot 'requirements.txt')
        if ($LASTEXITCODE -ne 0) { throw 'Fallo la instalacion de dependencias en el entorno local.' }
    }
    & $analysisPython -c 'import numpy, scipy, matplotlib'
    if ($LASTEXITCODE -ne 0) {
        throw 'Faltan dependencias. Ejecute este archivo con -InstalarDependencias; solo esa instalacion inicial puede requerir Internet.'
    }

    & $analysisPython (Join-Path $analysisRoot 'comparar_50MeV.py')
    if ($LASTEXITCODE -ne 0) { throw 'El calculo o sus verificaciones numericas no se completaron.' }

    $summaryPath = Join-Path $analysisRoot 'data/resumen.json'
    $summary = Get-Content -LiteralPath $summaryPath -Raw -Encoding UTF8 | ConvertFrom-Json
    $at50 = $summary.point_50MeV_PDG2025
    $cross = $summary.crossover_PDG2025
    Write-Host ''
    Write-Host 'Resultados PDG2025 a 50 MeV:'
    Write-Host ('Bariones / cm^3:       {0:E6}' -f $at50.n_B_cm3)
    Write-Host ('Antibariones / cm^3:   {0:E6}' -f $at50.n_antiB_cm3)
    Write-Host ('Exceso neto / cm^3:    {0:E6}' -f $at50.n_net_cm3)
    Write-Host ('Antibariones / exceso: {0:F6}' -f $at50.R_antibaryon_to_net)
    Write-Host ('Cruce R=1:             {0:F6} MeV' -f $cross.T_MeV)
    Write-Host ('Diferencia vs 38.2:    {0:F6} MeV' -f $summary.numerical_difference_to_38p2_MeV)
    Write-Host 'Interpretacion: reconstruccion de equilibrio condicionada a los datos y supuestos del modelo.'
    Write-Host ('Datos y figura: ' + (Join-Path $analysisRoot 'data') + ' ; ' + (Join-Path $analysisRoot 'figures'))
}
finally {
    Pop-Location
}
