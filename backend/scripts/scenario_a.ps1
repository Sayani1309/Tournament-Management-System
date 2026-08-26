$base = "http://localhost:5000/api/v1"

$org = Invoke-RestMethod -Uri "$base/auth/register" -Method Post -ContentType "application/json" -Body (@{name="Integ Organizer";email="integA_org@example.com";password="password123";role="ORGANIZER"} | ConvertTo-Json)
Write-Host "Organizer registered: is_verified=$($org.is_verified)"

$login = Invoke-RestMethod -Uri "$base/auth/login" -Method Post -ContentType "application/json" -Body (@{email="integA_org@example.com";password="password123"} | ConvertTo-Json)
$orgHeaders = @{ Authorization = "Bearer $($login.access_token)" }

for ($i = 1; $i -le 5; $i++) {
    $email = "integA_player$i@example.com"
    $reg = Invoke-RestMethod -Uri "$base/auth/register" -Method Post -ContentType "application/json" -Body (@{name="Player $i";email=$email;password="password123";role="PLAYER";participation_type="INDIVIDUAL"} | ConvertTo-Json)
    Write-Host "Player $i registered: id will be resolved via /players"
    
}

$tournament = Invoke-RestMethod -Uri "$base/tournaments" -Method Post -Headers $orgHeaders -ContentType "application/json" -Body (@{name="Integ RR Full Test";sport="Chess";format="ROUND_ROBIN";participant_type="INDIVIDUAL"} | ConvertTo-Json)
$tid = $tournament.id
Write-Host "Tournament created: id=$tid status=$($tournament.status)"

$guestCheck = Invoke-RestMethod -Uri "$base/tournaments/$tid" -Method Get
Write-Host "Guest can view tournament without auth: status=$($guestCheck.status)"

$tournament = Invoke-RestMethod -Uri "$base/tournaments/$tid/open-registration" -Method Post -Headers $orgHeaders
Write-Host "After open-registration: $($tournament.status)"

$playersList = Invoke-RestMethod -Uri "$base/players?per_page=100" -Method Get
$playerIds = $playersList.items | Where-Object { $_.name -like "Player *" } | Select-Object -ExpandProperty id
Write-Host "Found player IDs: $($playerIds -join ', ')"

foreach ($playerId in $playerIds) {
    $reg = Invoke-RestMethod -Uri "$base/tournaments/$tid/participants" -Method Post -Headers $orgHeaders -ContentType "application/json" -Body (@{player_id=$playerId} | ConvertTo-Json)
    Write-Host "Registered participant_id=$($reg.participant_id) for player_id=$playerId"
}

$tournament = Invoke-RestMethod -Uri "$base/tournaments/$tid/start" -Method Post -Headers $orgHeaders
Write-Host "After start: $($tournament.status)"

$matches = Invoke-RestMethod -Uri "$base/tournaments/$tid/fixtures" -Method Post -Headers $orgHeaders
Write-Host "Fixtures generated: $($matches.Count) matches (expect 10 for 5 players)"

$guestMatches = Invoke-RestMethod -Uri "$base/tournaments/$tid/matches" -Method Get
Write-Host "First match participants: $($guestMatches[0].participants | ConvertTo-Json -Compress)"

foreach ($match in $matches) {
    $participantIds = $match.participants | Select-Object -ExpandProperty id
    $body = @{
        result_type = "WIN"
        winner_participant_id = $participantIds[0]
        scores = @(
            @{participant_id=$participantIds[0]; score=1},
            @{participant_id=$participantIds[1]; score=0}
        )
    } | ConvertTo-Json -Depth 5
    $result = Invoke-RestMethod -Uri "$base/matches/$($match.id)/result" -Method Post -Headers $orgHeaders -ContentType "application/json" -Body $body
    Write-Host "Match $($match.id) result submitted: winner=$($result.winner.name)"
}

$finalTournament = Invoke-RestMethod -Uri "$base/tournaments/$tid" -Method Get
Write-Host "FINAL TOURNAMENT STATUS: $($finalTournament.status) (expect COMPLETED)"

$standings = Invoke-RestMethod -Uri "$base/tournaments/$tid/standings" -Method Get
Write-Host "Standings:"
$standings | ForEach-Object { Write-Host "  $($_.name): points=$($_.points) played=$($_.played) diff=$($_.score_difference)" }