$ErrorActionPreference = "Stop"

$python = "py -3"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$repo = Split-Path -Parent $root

Write-Host "German Gamma validation twins"
Write-Host "Root: $root"

function Run-Reversibility($case, $base) {
    $input = Join-Path $root "$case\$base.csv"
    $out = Join-Path $root "$case\${base}_reversibility.json"
    Write-Host "REVERSIBILITY $case $base"
    py -3 (Join-Path $repo "german_gamma_v5_8_reversibility.py") --input $input --columns x1,x2,x3 --time-column t --window-size 120 --step 120 --bins 5 --json-out $out
}

function Run-EnergyEntropy($case, $base) {
    $input = Join-Path $root "$case\$base.csv"
    $out = Join-Path $root "$case\${base}_energy_entropy.json"
    Write-Host "ENERGY_ENTROPY $case $base"
    py -3 (Join-Path $repo "german_gamma_v5_6_3d_hilbert_laplace.py") energy_entropy --input $input --columns x1,x2,x3 --filter "x1 > 0" --bins 5 --json-out $out
}

$cases = @(
    "01_null_twin",
    "02_filtered_twin",
    "03_temporal_twin",
    "04_entropy_twin",
    "05_reversibility_twin"
)

foreach ($case in $cases) {
    Run-EnergyEntropy $case "base_A"
    Run-EnergyEntropy $case "base_B"
    Run-Reversibility $case "base_A"
    Run-Reversibility $case "base_B"
}

Write-Host "Done."
