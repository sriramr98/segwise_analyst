# DATA ANALYSIS API

This is the backend code for a data analysis API capable of creating tables from CSV files and performing queries on it over HTTP

TECH STACK
* Python
* Docker and DockerCompose
* PostgreSQL

> Make sure postgres is installed locally if you want to build docker locally.

API BASE URL - https://zonal-nourishment-production.up.railway.app
API DOCS - https://zonal-nourishment-production.up.railway.app/docs

To install Postgres for Mac users, try `brew install postgresql`

# Requirements
1. AWS CLI
2. Python
3. Docker
4. Postgres

## FEATURES
* Filters ( all data types )
    * All filters are applied with `AND` only.
* Group By and Aggregations
* Aggregation Filters

## FUTURE SCOPE
* Better input validation
* Support for complex filters ( `(A AND B) OR (C AND D)`)
* More aggregation functions
* Window functions
* Handling Generic CSVs
* Handling arbitrarily large CSVs
* GROUP BY support for list columns
* Unit Testing

## ASSUMPTIONS
* No GROUP BY support for list columns like `Genres`, `Supported Languages` etc
* All filters are applied with `AND`
* Limited Aggregation Functions
    * count
    * sum
* Service works for only one schema
* Any empty values are filled with defaults ( int -> 0, boolean -> false, string -> '')

## RUN LOCALLY
### Docker
If you have docker installed, you can just execute `docker-compose up --build`. The docker compose files comes with Postgresql, so no setup necessary

### Remote Postgres
If you want to connect to a remote postgres, create a `.env` file ( `.env.sample` for keys ) and add the db confihg.

## API DOCS
API docs are embedded with the server. In your browser, just open `http://{host}:8000/docs` for detailed API docs.

## API DOCUMENTATION
> All API's except `/health` expect a `password` header.The hash of this should be present in `.env` file as `ADMIN_PASSWORD_HASH`

1. `/health/` - (Health Check Endpoint)
2. `/upload-csv/` ( POST )
    Request Body - `{ "csv_link": "url" }`
    Response - `{"message": "Uploaded 100 records successfully"}`
3. `/explore/` - (GET)
    Request Body
    ```json
    {
        "filters": [
            { 
                "column": "Linux",
                "condition": eq, 
                "value": true 
            }
        ],
        "group_bys": [ "Mac" ],
        "aggregations": [
            {
                "column": "Positive",
                "function": "count",
                "alias": "positive_count"
            }
        ]
    }
    ```

    For each filter
    1. `column` -> The original column name from the CSV
    2. `condition` ->
        1. EQUALS (eq)
        2. LESS THAN (lt)
        3. LESS THAN OR EQUAL TO ( lte )
        4. GREATER THAN ( gt )
        5. GREATER THAN OR EQUAL TO ( gte )
    3. `value` -> Accepts string, int, float and boolean.
        1. For date columns, send string with format `MMM DD, YY` or `MMM YY` ( date will be 1 in the second case )

    Group Bys
    1. List of original column names from the CSV
    2. List columns like Supported languages, Categories, Genres,Tags not supported
    
    Aggregations
    1. `column` -> Original column name from the CSV
    2. `function` -> The aggreagtion to be done
        1. `count` -> Count occurences
        2. `sum` -> Sum of all values
    3. `alias` -> The output column name in the result
    4. `filter` -> Boolean denoting whether to filter the results based on the aggregation
    5. `filterCondition` -> Same as filters section above (eq, lt, lte, gt, gte)
    6. `filterCriteria` -> The criteria to fitler the aggregation with ( same as value in filter section )
        1. Only integers supported

## SAMPLE EXPLORE REQUEST BODY

1. List all games supported by the linux platform
```json
{
  "filters": [
    {
      "column": "Linux",
      "condition": "eq",
      "value": true
    }
  ],
  "group_bys": [ ],
  "aggregations": [
    
  ]
}
```

2. List all games supported by Linux and Mac
```json
{
  "filters": [
    {
      "column": "Linux",
      "condition": "eq",
      "value": true
    },
    {
      "column": "Mac",
      "condition": "eq",
      "value": true
    }
  ],
  "group_bys": [ ],
  "aggregations": [
    
  ]
}
```

3. List all games supported by Linux and supports Russian

```json
{
  "filters": [
    {
      "column": "Linux",
      "condition": "eq",
      "value": true
    },
    {
      "column": "Supported languages",
      "condition": "eq",
      "value": "Russian"
    }
  ],
  "group_bys": [ ],
  "aggregations": [
    
  ]
}
```

4. What is the total price of all games per developer?
```json
{
  "filters": [
  ],
  "group_bys": [ "Developers" ],
  "aggregations": [
    {
      "column": "Price",
      "function": "sum",
      "alias": "total_price"
    }
  ]
}
```

4. What is the total price of all games per developer?
```json
{
  "filters": [
  ],
  "group_bys": [ "Developers" ],
  "aggregations": [
    {
      "column": "Price",
      "function": "sum",
      "alias": "total_price"
    }
  ]
}
```

5. How many developers released atleast one game in linux platform?

```json
{
  "filters": [
    {
      "column": "Linux",
      "condition": "eq",
      "value": true
    }
  ],
  "group_bys": [ "Developers" ],
  "aggregations": [
    {
      "column": "AppId",
      "function": "count",
      "alias": "game_count",
      "filter": true,
      "filterCondition": "gte",
      "filterCriteria": 1
    }
  ]
}
```

## PRODUCTION COST ANALYSIS

### ASSUMPTIONS
1. One upload a day of a file of size 50MB
2. 100 GET queries
3. GET queries will be priced for worst case scenario for network costs
    1. No pagination in GET requests ( 1million rows are sent in the output every request )
4. GET queries will be priced for two aggregations, two group bys, two filters and one aggregated filter (determines EC2 size)
4. About the game description of 4000 characters
5. Cost analysis considering prod deployment in AWS (EC2 and RDS)
6. AWS Region - Mumbai (ap-south-1)
7. Two EC2 machines ( API server ) for fault tolerance
8. EC2 is priced on demand
9. API response will be priced for worst case scenario ( all columns and all rows for each API request )
10. Since cost is calculated for 100 requests a day, we assume no concurrent requests ( only one request at any time )
11. Infra will be overprovisioned to account for unforseen scenario's

### DATA SIZE ESTIMATION
* id (SERIAL): 4 bytes
* app_id (INTEGER): 4 bytes
* name (VARCHAR(255)): Avg 20 chars = 20 bytes
* release_date (DATE): 4 bytes
* required_age (SMALLINT): 2 bytes
* price (NUMERIC(10,2)): 4 bytes
* dlc_count (SMALLINT): 2 bytes
*about_game (TEXT): Avg 2000 chars = 4000 bytes
* supported_languages (TEXT[]): Avg 2 languages = 100 bytes
* boolean columns (3x): 3 bytes
* positive/negative reviews (INTEGER): 8 bytes
* score_rank (FLOAT): 4 bytes
* developers/publishers/categories/genres/tags (TEXT[]) - Each estimated at 200 bytes

Approximate row size:
4 + 4 + 20 + 4 + 2 + 4 + 2 + 4000 + 100 + 3 + 8 + 4 + (5 * 200) = ~4,775 bytes per row

For 1 million rows: 4,775 * 1,000,000 = 4.775 GB base table size
With indexes and overhead, estimate ~7-8 GB total

### DATABASE CONFIGURATION
RDS Postgres Instance
* 16 GB RAM
* 4 vCPUs
* 250 GB SSD Storage

1 instance(s) x 1.028 USD hourly x (100 / 100 Utilized/Month) x 730 hours in a month = 750.4400 USD
Amazon RDS PostgreSQL instances cost (monthly): 985.64 USD (with networking costs)

### API SERVER COST

* 8GB RAM + 2 vCPU ( t4g.large ) -> 65.408000 USD
* Ingestion Data Transfer = 50MB * 30 days = 1500MB = 1.5GB ~ 2GB -> 
* Outbound Data Transfer
  * Data Per Request = 1 million rows * 4,775 bytes = 4,775,000,000 bytes ≈ 4.775 GB per request
  * Daily Data Transfer = 4.775 GB * 100 = 477.5 GB per day
  * Monthly Data Transfer = 477.5 GB * 30 = 14,325 GB ≈ 14.325 TB per month ~ 15TB
* Inbound + Outbound Cost = 1,554.43 USD
* AWS Application Load Balancer
  * 15TB of processed data ( GET API responses )
  * Cost = 140 USD

TOTAL COST = API SERVER (EC2 + Data Transfer) + LOAD BALANCER + RDS = 65 + 1555 + 140 + 985 = 2745 USD per month

## COST OPTIMISATIONS
1. GET API should be paginated so that outbound is only charged for what the user views ( this will optimise both EC2 outbound and LB data processed costs significantly )
3. Since the number of GET requests is low, using Lambda can significantly reduce costs initially since we won't pay for idle time
4. Postgres EC2 can be paid with Compute Savings Plan, 1year reservation, all upfront paid

## COST AFTER ACCOUNTING FOR OPTIMISATIONS
### LAMBDA API SERVER
1. 100 invocations per month
2. 6GB RAM
3. 5s per query

COST = 0 ( not including free tier )
#### CALCULATIONS
* Amount of ephemeral storage allocated: 512 MB x 0.0009765625 GB in a MB = 0.5 GB
* Pricing calculations
* 100 requests x 5,000 ms x 0.001 ms to sec conversion factor = 500.00 total compute (seconds)
* 6 GB x 500.00 seconds = 3,000.00 total compute (GB-s)
* Tiered price for: 3,000.00 GB-s
* 3,000 GB-s x 0.0000166667 USD = 0.05 USD
* Total tier cost = 0.05 USD (monthly compute charges)
* Monthly compute charges: 0.05 USD
* 100 requests x 0.0000002 USD = 0.00 USD (monthly request charges)
* Monthly request charges: 0.00 USD
* 0.50 GB - 0.5 GB (no additional charge) = 0.00 GB billable ephemeral storage per function
* Monthly ephemeral storage charges: 0 USD
* Lambda cost (monthly): 0.05 USD ~ 0 USD

> NOTE: Load balancer isn't required since we can just call the lambda directly saving on outbound network costs

#### DATA TRANSFER COSTS
1. Assuming GET requests are paginated and 500 rows are rendered ( viewed by the user )
2. Total Requests per month = 500 rows * 100 requests * 30 days = 15,00,000
3. Total Data Transferred = 1500000 * 4,775 bytes = 7GB per month = 0.77 USD

TOTAL COST = Cost of RDS + Lambda Costs + Network Costs = 985 + 0.77 + 0 = 958 USD per month

## COST COMPARISONS
* COST BEFORE OPTIMISATION = 2745 USD
* COST AFTER OPTIMISATION = 958 USD
* SAVINGS PERCENTAGE = 65%