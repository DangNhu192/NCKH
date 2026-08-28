$ErrorActionPreference = "Continue"

function TestEndpoint {
    param($name, $url, $method, $bodyJson)
    try {
        if ($method -eq "GET") {
            $res = Invoke-WebRequest -Uri $url -Method GET -TimeoutSec 8 -UseBasicParsing
        } else {
            $res = Invoke-WebRequest -Uri $url -Method POST -Body $bodyJson -ContentType "application/json" -TimeoutSec 8 -UseBasicParsing
        }
        Write-Host "OK  [$($res.StatusCode)] $name => $($res.Content.Substring(0, [Math]::Min(120, $res.Content.Length)))"
    } catch {
        Write-Host "ERR $name => $($_.Exception.Message.Substring(0,[Math]::Min(100,$_.Exception.Message.Length)))"
    }
}

TestEndpoint "GET /api/status"    "http://127.0.0.1:8000/api/status"                     "GET"  $null
TestEndpoint "GET /api/config"    "http://127.0.0.1:8000/api/config"                     "GET"  $null
TestEndpoint "GET /api/files"     "http://127.0.0.1:8000/api/files"                      "GET"  $null
TestEndpoint "POST research/step1" "http://127.0.0.1:8000/api/research/step1"            "POST" '{"topic":"AI giao duc","num_papers":1}'
TestEndpoint "POST humanize/vn"    "http://127.0.0.1:8000/api/humanize/vietnamese"       "POST" '{"text":"Nhin chung day la van de quan trong"}'
TestEndpoint "POST humanize/orig"  "http://127.0.0.1:8000/api/humanize/original"         "POST" '{"text":"Nhin chung day la van de quan trong"}'
TestEndpoint "POST editorial/ana"  "http://127.0.0.1:8000/api/editorial/analyze"         "POST" '{"topic":"AI","user_input_type":"y tuong","purpose":"inform","audience":"cong chung","platform":"blog","need_fact_check":false}'
TestEndpoint "POST execute-gate"   "http://127.0.0.1:8000/api/editorial/execute-gate"    "POST" '{"topic":"AI trong giao duc","gate_steps":[{"id":"step_1","dept":"research","action":"Thu thap","gate":"GATE 1"}]}'
TestEndpoint "POST files/save"     "http://127.0.0.1:8000/api/files/save"                "POST" '{"rel_path":"Ban_Thao/test_diag.md","content":"Hello Test","file_format":"md"}'
