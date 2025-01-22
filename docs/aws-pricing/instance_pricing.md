# AWS Instance Pricing

| Instance Type | Family | vCPU | Memory (GB) | Network          | EBS Bandwidth | EBS IOPS | GPU     | GPU Memory (GB) | Architecture | Processor | Clock (GHz) | On-Demand Price/hr | Spot Price/hr |
| :------------ | :----- | ---: | ----------: | :--------------- | :------------ | :------- | :------ | :-------------- | :----------- | :-------- | ----------: | :----------------- | :------------ |
| t3.large      | t3     |    2 |           8 | Up to 5 Gigabit  | 695 Mbps      | 4,000    | N/A     | N/A             | x86_64       | Intel     |         2.5 | $0.083             | $0.025        |
| m5.large      | m5     |    2 |           8 | Up to 10 Gigabit | 650 Mbps      | 3,600    | N/A     | N/A             | x86_64       | Intel     |         3.1 | $0.096             | $0.029        |
| t3.2xlarge    | t3     |    8 |          32 | Up to 5 Gigabit  | 695 Mbps      | 4,000    | N/A     | N/A             | x86_64       | Intel     |         2.5 | $0.333             | $0.100        |
| m5.2xlarge    | m5     |    8 |          32 | Up to 10 Gigabit | 2300 Mbps     | 12,000   | N/A     | N/A             | x86_64       | Intel     |         3.1 | $0.519             | $0.156        |
| t3.xlarge     | t3     |    4 |          16 | Up to 5 Gigabit  | 695 Mbps      | 4,000    | N/A     | N/A             | x86_64       | Intel     |         2.5 | $0.646             | $0.194        |
| m5.xlarge     | m5     |    4 |          16 | Up to 10 Gigabit | 1150 Mbps     | 6,000    | N/A     | N/A             | x86_64       | Intel     |         3.1 | $0.672             | $0.202        |
| g4dn.2xlarge  | g4dn   |    8 |          32 | Up to 25 Gigabit | 1150 Mbps     | 6,000    | 1x T4   | 16              | x86_64       | Intel     |         2.5 | $0.752             | $0.226        |
| g5.xlarge     | g5     |    4 |          16 | Up to 10 Gigabit | 700 Mbps      | 3,000    | 1x A10G | 24              | x86_64       | AMD       |         3.3 | $1.006             | $0.302        |
| g4dn.4xlarge  | g4dn   |   16 |          64 | Up to 25 Gigabit | 4750 Mbps     | 20,000   | 1x T4   | 16              | x86_64       | Intel     |         2.5 | $1.204             | $0.361        |
| g5.2xlarge    | g5     |    8 |          32 | Up to 10 Gigabit | 850 Mbps      | 3,500    | 1x A10G | 24              | x86_64       | AMD       |         3.3 | $1.212             | $0.364        |
| r5.2xlarge    | r5     |    8 |          64 | Up to 10 Gigabit | 2300 Mbps     | 12,000   | N/A     | N/A             | x86_64       | Intel     |         3.1 | $1.464             | $0.439        |
| g5.4xlarge    | g5     |   16 |          64 | Up to 25 Gigabit | 4750 Mbps     | 20,000   | 1x A10G | 24              | x86_64       | AMD       |         3.3 | $1.624             | $0.487        |
| g4dn.8xlarge  | g4dn   |   32 |         128 | 50 Gigabit       | 9500 Mbps     | 40,000   | 1x T4   | 16              | x86_64       | Intel     |         2.5 | $2.176             | $0.653        |
| m5.12xlarge   | m5     |   48 |         192 | 12 Gigabit       | 9500 Mbps     | 40,000   | N/A     | N/A             | x86_64       | Intel     |         3.1 | $2.304             | $0.691        |
| r5.4xlarge    | r5     |   16 |         128 | Up to 10 Gigabit | 4750 Mbps     | 18,750   | N/A     | N/A             | x86_64       | Intel     |         3.1 | $2.928             | $0.878        |
| p3.2xlarge    | p3     |    8 |          61 | Up to 10 Gigabit | 1750 Mbps     | 10,000   | 1x V100 | 16              | x86_64       | Intel     |         2.7 | $3.060             | $0.918        |
| g4dn.12xlarge | g4dn   |   48 |         192 | 50 Gigabit       | 9500 Mbps     | 40,000   | 4x T4   | 16              | x86_64       | Intel     |         2.5 | $3.912             | $1.174        |
| r5.8xlarge    | r5     |   32 |         256 | 10 Gigabit       | 6800 Mbps     | 30,000   | N/A     | N/A             | x86_64       | Intel     |         3.1 | $5.856             | $1.757        |
| m5.24xlarge   | m5     |   96 |         384 | 25 Gigabit       | 19000 Mbps    | 80,000   | N/A     | N/A             | x86_64       | Intel     |         3.1 | $6.230             | $1.869        |
| m5.4xlarge    | m5     |   16 |          64 | Up to 10 Gigabit | 4750 Mbps     | 18,750   | N/A     | N/A             | x86_64       | Intel     |         3.1 | $6.768             | $2.030        |
| p3.8xlarge    | p3     |   32 |         244 | 10 Gigabit       | 7000 Mbps     | 40,000   | 4x V100 | 16              | x86_64       | Intel     |         2.7 | $12.240            | $3.672        |

Last updated: 2025-01-12T19:08:20.121402
