# QR Code Byte-Mode Capacity (Error Correction Level L)

Max data characters per version at EC Level L (lowest redundancy, smallest QR for given payload).

| v  | modules | bytes | v  | modules | bytes | v  | modules | bytes |
|----|---------|-------|----|---------|-------|----|---------|-------|
| 1  | 21×21   | 25    | 11 | 57×57   | 236   | 21 | 101×101 | 943   |
| 2  | 25×25   | 44    | 12 | 61×61   | 261   | 22 | 105×105 | 1044  |
| 3  | 29×29   | 70    | 13 | 65×65   | 294   | 23 | 109×109 | 1152  |
| 4  | 33×33   | 100   | 14 | 69×69   | 326   | 24 | 113×113 | 1258  |
| 5  | 37×37   | 134   | 15 | 77×77   | 518   | 25 | 117×117 | 1368  |
| 6  | 41×41   | 172   | 16 | 81×81   | 555   | 26 | 121×121 | 1490  |
| 7  | 45×45   | 196   | 17 | 85×85   | 592   | 27 | 125×125 | 1612  |
| 8  | 49×49   | 242   | 18 | 89×89   | 633   | 28 | 129×129 | 1736  |
| 9  | 53×53   | 280   | 19 | 93×93   | 674   | 29 | 133×133 | 1866  |
| 10 | 57×57   | 321   | 20 | 97×97   | 716   | 30 | 137×137 | 1994  |

Higher EC levels (M/Q/H) reduce capacity by ~10-25% per level step.

## Inflation multipliers

| Encoding method | Multiplier |
|----------------|------------|
| Only `<` → `%3C`, `>` → `%3E` | ~1.05x |
| `data:text/html;base64,` + base64 | ~1.3x |
| `data:text/html,` + `quote()` | ~1.7x |
