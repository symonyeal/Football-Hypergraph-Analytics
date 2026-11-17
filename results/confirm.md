# Confirmation: Wyscout 2017/18 five leagues

Data: Wyscout public data set (Pappalardo et al., Scientific Data 6, 236, 2019; CC BY 4.0). xG from the StatsBomb-fitted model (docs/POSTHOC.md P4). Run once under `docs/PROTOCOL.md` (tag `protocol-v1`); verdicts by its rules (`fha/report.py`, `verdicts`).

Status: confirmation (docs/PROTOCOL.md). Teams: 98. Null draws made by the fallback sampler (docs/POSTHOC.md P6): 2641.

| Hypothesis | Quantity | Estimate | 95% interval | Verdict | Family |
| --- | --- | --- | --- | --- | --- |
| R1 | player D1 ICC | 0.384 | 0.165 to 0.539 | supported | primary |
| R1 | player c2 ICC | 0.326 | 0.136 to 0.483 | supported | primary |
| R1 | player tau_0.9 ICC | 0.288 | 0.091 to 0.444 | supported | primary |
| R1 | player c2 excess over N0 ICC | 0.099 | -0.095 to 0.281 | undetermined | secondary |
| R1 | player tau_0.9 excess over N0 ICC | -0.053 | -0.240 to 0.126 | undetermined | secondary |
| R1 | role D1 ICC | 0.553 | 0.404 to 0.673 | supported | secondary |
| R1 | role c2 ICC | 0.005 | -0.118 to 0.149 | equivalent to none | secondary |
| R1 | role tau_0.9 ICC | 0.250 | 0.060 to 0.430 | supported | secondary |
| R1 | role c2 excess over N0 ICC | -0.011 | -0.197 to 0.187 | equivalent to none | secondary |
| R1 | role tau_0.9 excess over N0 ICC | 0.040 | -0.190 to 0.269 | undetermined | secondary |
| R2 | player c2 excess over N2 | 0.017 | 0.010 to 0.025 | supported | primary |
| R2 | player c3 excess over N2 | 0.014 | 0.009 to 0.020 | supported (Holm p 0.000) | secondary |
| R2 | player tau_0.9 excess over N2 | -0.145 | -0.236 to -0.055 | reversed (Holm p 0.002) | secondary |
| R2 | player o2 excess over N2 | 0.012 | 0.005 to 0.020 | supported, below the margin (Holm p 0.001) | secondary |
| R2 | player c2 excess over N1 | 0.008 | 0.001 to 0.016 | supported, below the margin (Holm p 0.027) | secondary |
| R2 | player c3 excess over N1 | 0.008 | 0.002 to 0.014 | supported, below the margin (Holm p 0.019) | secondary |
| R2 | player tau_0.9 excess over N1 | -0.121 | -0.211 to -0.030 | reversed (Holm p 0.027) | secondary |
| R2 | player o2 excess over N1 | 0.009 | 0.002 to 0.016 | supported, below the margin (Holm p 0.027) | secondary |
| R2 | player c2 excess over N0 | 0.025 | 0.018 to 0.032 | supported (Holm p 0.000) | secondary |
| R2 | player c3 excess over N0 | 0.023 | 0.017 to 0.029 | supported (Holm p 0.000) | secondary |
| R2 | player tau_0.9 excess over N0 | -0.297 | -0.403 to -0.191 | reversed (Holm p 0.000) | secondary |
| R2 | player o2 excess over N0 | 0.014 | 0.007 to 0.021 | supported (Holm p 0.000) | secondary |
| R2 | role c2 excess over N2 | 0.000 | -0.000 to 0.000 | equivalent to none (Holm p 1.000) | secondary |
| R2 | role tau_0.9 excess over N2 | -0.007 | -0.076 to 0.062 | undetermined (Holm p 1.000) | secondary |
| R2 | role o2 excess over N2 | 0.001 | -0.002 to 0.004 | equivalent to none (Holm p 1.000) | secondary |
| R2 | role c2 excess over N0 | 0.008 | 0.007 to 0.009 | supported, below the margin (Holm p 0.000) | secondary |
| R2 | role tau_0.9 excess over N0 | -0.002 | -0.082 to 0.077 | undetermined (Holm p 0.958) | secondary |
| R2 | role o2 excess over N0 | 0.002 | -0.001 to 0.005 | equivalent to none (Holm p 0.429) | secondary |
| R3 | b = 1: exact minus involvement | 0.000 | 0.000 to 0.000 | equivalent to none | secondary |
| R3 | b = 1: exact minus shapley | -0.010 | -0.026 to 0.002 | undetermined | secondary |
| R3 | b = 1: exact minus pass strength | 0.167 | 0.131 to 0.202 | supported | secondary |
| R3 | b = 2: exact minus involvement | -0.007 | -0.020 to 0.006 | undetermined | primary |
| R3 | b = 2: exact minus shapley | -0.010 | -0.024 to 0.002 | undetermined | secondary |
| R3 | b = 2: exact minus pass strength | 0.223 | 0.187 to 0.262 | supported | secondary |
| R3 | b = 3: exact minus involvement | -0.014 | -0.028 to 0.003 | undetermined | secondary |
| R3 | b = 3: exact minus shapley | -0.018 | -0.033 to -0.003 | reversed | secondary |
| R3 | b = 3: exact minus pass strength | 0.242 | 0.209 to 0.275 | supported | secondary |
| R3 | b = 4: exact minus involvement | -0.007 | -0.024 to 0.010 | undetermined | secondary |
| R3 | b = 4: exact minus shapley | -0.009 | -0.027 to 0.007 | undetermined | secondary |
| R3 | b = 4: exact minus pass strength | 0.219 | 0.188 to 0.253 | supported | secondary |
| R3 | b = 5: exact minus involvement | -0.011 | -0.021 to 0.000 | undetermined | secondary |
| R3 | b = 5: exact minus shapley | -0.015 | -0.025 to -0.004 | reversed | secondary |
| R3 | b = 5: exact minus pass strength | 0.189 | 0.162 to 0.218 | supported | secondary |
| R4 | beta | -0.459 | -3.072 to 1.982 | descriptive (no verdict; protocol R4) | descriptive |
| R4 | delta | 1.099 | -2.355 to 4.956 | descriptive (no verdict; protocol R4) | descriptive |
| R5 | xg: increment in LOO R^2 | -0.013 | -0.015 to 0.010 | equivalent to none | primary |
| R5 | pts: increment in LOO R^2 | -0.016 | -0.023 to 0.029 | equivalent to none | secondary |
