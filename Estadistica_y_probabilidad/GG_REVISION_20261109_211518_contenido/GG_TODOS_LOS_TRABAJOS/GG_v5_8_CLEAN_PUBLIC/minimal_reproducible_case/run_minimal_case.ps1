$ErrorActionPreference = "Stop"

$caseDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Split-Path -Parent $caseDir

Set-Location $repoRoot

if (Get-Command py -ErrorAction SilentlyContinue) {
    & py -3 "$caseDir\generate_minimal_case.py"
    & py -3 "$repoRoot\validation_twins\angular_momentum_trajectory_test.py" `
        --input "$caseDir\minimal_orbit_input.csv" `
        --columns x1,x2,x3 `
        --json-out "$caseDir\minimal_orbit_result.json" `
        --csv-out "$caseDir\minimal_orbit_points.csv" `
        --center-radius 20
} else {
    & python "$caseDir\generate_minimal_case.py"
    & python "$repoRoot\validation_twins\angular_momentum_trajectory_test.py" `
        --input "$caseDir\minimal_orbit_input.csv" `
        --columns x1,x2,x3 `
        --json-out "$caseDir\minimal_orbit_result.json" `
        --csv-out "$caseDir\minimal_orbit_points.csv" `
        --center-radius 20
}

Write-Host ""
Write-Host "Expected reading: stable_rotational_structure_candidate"
Write-Host "See: $caseDir\EXPECTED_READING.md"

