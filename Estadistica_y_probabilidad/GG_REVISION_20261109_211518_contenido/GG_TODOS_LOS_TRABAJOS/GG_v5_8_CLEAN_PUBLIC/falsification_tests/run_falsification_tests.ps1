$ErrorActionPreference = "Stop"

$testDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Split-Path -Parent $testDir

Set-Location $repoRoot

function Invoke-Python {
    param([Parameter(ValueFromRemainingArguments=$true)][string[]]$Args)
    if (Get-Command py -ErrorAction SilentlyContinue) {
        & py -3 @Args
    } else {
        & python @Args
    }
}

Invoke-Python "$testDir\generate_falsification_cases.py"

Invoke-Python "$repoRoot\validation_twins\angular_momentum_trajectory_test.py" `
    --input "$testDir\01_positive_orbit.csv" `
    --columns x1,x2,x3 `
    --json-out "$testDir\01_positive_orbit_result.json" `
    --csv-out "$testDir\01_positive_orbit_points.csv"

Invoke-Python "$repoRoot\validation_twins\angular_momentum_trajectory_test.py" `
    --input "$testDir\02_negative_radial.csv" `
    --columns x1,x2,x3 `
    --json-out "$testDir\02_negative_radial_result.json" `
    --csv-out "$testDir\02_negative_radial_points.csv"

Invoke-Python "$repoRoot\validation_twins\angular_momentum_trajectory_test.py" `
    --input "$testDir\03_noise_random_walk.csv" `
    --columns x1,x2,x3 `
    --json-out "$testDir\03_noise_random_walk_result.json" `
    --csv-out "$testDir\03_noise_random_walk_points.csv"
