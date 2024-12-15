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