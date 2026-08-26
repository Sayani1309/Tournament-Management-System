$base = "http://localhost:5000/api/v1"

$login = Invoke-RestMethod -Uri "$base/auth/login" -Method Post -ContentType "application/json" -Body (@{email="integA_org@example.com";password="password123"} | ConvertTo-Json)
$orgHeaders = @{ Authorization = "Bearer $($login.access_token)" }

for ($i = 1; $i -le 6; $i++) {
    $email = "integB_player$i@example.com"
    Invoke-RestMethod -Uri "$base/auth/register" -Method Post -ContentType "application/json" -Body (@{name="KO Player $i";email=$email;password="password123";role="PLAYER";participation_type="INDIVIDUAL"} | ConvertTo-Json) | Out-Null
    Write-Host "KO Player $i registered"
}

$tournament = Invoke-RestMethod -Uri "$base/tournaments" -Method Post -Headers $orgHeaders -ContentType "application/json" -Body (@{name="Integ Knockout Test";sport="Badminton";format="KNOCKOUT";participant_type="INDIVIDUAL"} | ConvertTo-Json)
$tid = $tournament.id
Write-Host "Tournament created: id=$tid status=$($tournament.status)"

$tournament = Invoke-RestMethod -Uri "$base/tournaments/$tid/open-registration" -Method Post -Headers $orgHeaders
Write-Host "After open-registration: $($tournament.status)"

$playersList = Invoke-RestMethod -Uri "$base/players?per_page=100" -Method Get
$playerIds = $playersList.items | Where-Object { $_.name -like "KO Player *" } | Select-Object -ExpandProperty id
Write-Host "Found KO player IDs: $($playerIds -join ', ')"

foreach ($playerId in $playerIds) {
    $reg = Invoke-RestMethod -Uri "$base/tournaments/$tid/participants" -Method Post -Headers $orgHeaders -ContentType "application/json" -Body (@{player_id=$playerId} | ConvertTo-Json)
    Write-Host "Registered participant_id=$($reg.participant_id) for player_id=$playerId"
}

$tournament = Invoke-RestMethod -Uri "$base/tournaments/$tid/start" -Method Post -Headers $orgHeaders
Write-Host "After start: $($tournament.status)"

$matches = Invoke-RestMethod -Uri "$base/tournaments/$tid/fixtures" -Method Post -Headers $orgHeaders
Write-Host "Round 1 fixtures generated: $($matches.Count) matches (expect 4: 2 byes + 2 real for 6 players -> 8 slots)"

$allMatches = Invoke-RestMethod -Uri "$base/tournaments/$tid/matches" -Method Get
foreach ($m in $allMatches) {
    Write-Host "Match id=$($m.id) round=$($m.round) status=$($m.status) participants=$($m.participants.name -join ' vs ')"
}

# Check bye results already exist
foreach ($m in $allMatches) {
    if ($m.status -eq "COMPLETED") {
        $result = Invoke-RestMethod -Uri "$base/matches/$($m.id)/result" -Method Get
        Write-Host "Match $($m.id) (likely a bye) already has result: winner=$($result.winner.name)"
    }
}

# Submit results for the real (non-bye) Round 1 matches
$round1Real = $allMatches | Where-Object { $_.round -like "Round 1-Match*" -and $_.status -eq "SCHEDULED" }
foreach ($match in $round1Real) {
    $participantIds = $match.participants | Select-Object -ExpandProperty id
    $body = @{
        result_type = "WIN"
        winner_participant_id = $participantIds[0]
        scores = @(@{participant_id=$participantIds[0]; score=21}, @{participant_id=$participantIds[1]; score=15})
    } | ConvertTo-Json -Depth 5
    $result = Invoke-RestMethod -Uri "$base/matches/$($match.id)/result" -Method Post -Headers $orgHeaders -ContentType "application/json" -Body $body
    Write-Host "Round 1 match $($match.id) result: winner=$($result.winner.name)"
}

# Check Round 2 (semifinal) got populated
Start-Sleep -Seconds 1
$allMatches2 = Invoke-RestMethod -Uri "$base/tournaments/$tid/matches" -Method Get
$round2 = $allMatches2 | Where-Object { $_.round -like "Round 2-Match*" }
foreach ($m in $round2) {
    Write-Host "Round 2 match id=$($m.id) status=$($m.status) participants=$($m.participants.name -join ' vs ')"
}

# Submit Round 2 results
foreach ($match in ($round2 | Where-Object { $_.status -eq "SCHEDULED" })) {
    $participantIds = $match.participants | Select-Object -ExpandProperty id
    if ($participantIds.Count -eq 2) {
        $body = @{
            result_type = "WIN"
            winner_participant_id = $participantIds[0]
            scores = @(@{participant_id=$participantIds[0]; score=21}, @{participant_id=$participantIds[1]; score=18})
        } | ConvertTo-Json -Depth 5
        $result = Invoke-RestMethod -Uri "$base/matches/$($match.id)/result" -Method Post -Headers $orgHeaders -ContentType "application/json" -Body $body
        Write-Host "Round 2 match $($match.id) result: winner=$($result.winner.name)"
    }
}

# Check final
Start-Sleep -Seconds 1
$allMatches3 = Invoke-RestMethod -Uri "$base/tournaments/$tid/matches" -Method Get
$final = $allMatches3 | Where-Object { $_.round -like "Round 3-Match*" }
foreach ($m in $final) {
    Write-Host "FINAL match id=$($m.id) status=$($m.status) participants=$($m.participants.name -join ' vs ')"
}

$finalMatch = $final | Select-Object -First 1
if ($finalMatch -and $finalMatch.status -eq "SCHEDULED") {
    $participantIds = $finalMatch.participants | Select-Object -ExpandProperty id
    $body = @{
        result_type = "WIN"
        winner_participant_id = $participantIds[0]
        scores = @(@{participant_id=$participantIds[0]; score=21}, @{participant_id=$participantIds[1]; score=19})
    } | ConvertTo-Json -Depth 5
    $result = Invoke-RestMethod -Uri "$base/matches/$($finalMatch.id)/result" -Method Post -Headers $orgHeaders -ContentType "application/json" -Body $body
    Write-Host "FINAL result: CHAMPION = $($result.winner.name)"
}

$finalTournament = Invoke-RestMethod -Uri "$base/tournaments/$tid" -Method Get
Write-Host "TOURNAMENT STATUS: $($finalTournament.status) (expect COMPLETED)"