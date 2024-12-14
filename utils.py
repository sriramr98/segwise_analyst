from datetime import date, datetime
from typing import Any, Type
from fastapi import HTTPException
from sqlalchemy import Column
from models import AggregateFunction, Aggregation, Filter, Condition
import hashlib

def parseDate(input):
    try:
        return datetime.strptime(input, "%b %d, %Y").date()
    except:
        # it is possible that sometimes there's no date in the input
        return datetime.strptime(input, "%b %Y").date()

def parseBool(input):
    if input == True:
        return 'true'
    
    return 'false'

def parseValue(value: Any, type: Type[Any]) -> Any:
    if type is date:
        return parseDate(value)
    if type is bool:
        return parseBool(value)

    return value


operations = {
    Condition.EQ: {
        'operator': '=',
        'disallowed_types': [],
        'quoted_types': [ str, date ]
    },
    Condition.LTE: {
        'operator': '<=',
        'disallowed_types': [str, bool],
        'quoted_types': [ date ]
    },
    Condition.GTE: {
        'operator': '>=',
        'disallowed_types': [str, bool],
        'quoted_types': [ date ]
    },
    Condition.LT: {
        'operator': '<',
        'disallowed_types': [str, bool],
        'quoted_types': [ date ]
    },
    Condition.GT: {
        'operator': '>',
        'disallowed_types': [str, bool],
        'quoted_types': [ date ]
    }
}

def getFilter(filter: Filter, col_name_map: dict[str, Column]) -> str:
    column = col_name_map.get(filter.column)
    if column is None:
        raise HTTPException(400, f'Unknown column {filter.column}')

    result = f"{column.name} "
    value = parseValue(filter.value, column.type.python_type)

    condition_config = operations.get(filter.condition)
    if condition_config is None:
        raise HTTPException(400, "Invalid condition")
    value_has_quotes = column.type.python_type in condition_config.get('quoted_types')

    if filter.condition == Condition.EQ:
        if column.type.python_type is str:
            result += f"LIKE '%{value}'%"
        elif column.type.python_type is list:
            result = f"'{value}' = ANY({column.name})"
        else:
            if value_has_quotes:
                result += f"= '{value}'"
            else:
                result += f"= {value}"
    else:
        if value_has_quotes:
            result += f" {condition_config.get('operator')} '{value}'"
        else:
            result += f" {condition_config.get('operator')} {value}"
    return result

def createAggregation(function: AggregateFunction, column: str) -> str:
    if function == AggregateFunction.COUNT:
        return f"COUNT({column})"
    if function == AggregateFunction.SUM:
        return f"SUM({column})"

    raise HTTPException(400, f"Unknown aggreegation function {function}")

def getAggregateFunc(aggregate: Aggregation, col_name_map: dict[str, Column[Any]]):
    column = col_name_map.get(aggregate.column)
    if column is None:
        raise HTTPException(400, f"Unknown column {aggregate.column}")

    return f"{createAggregation(aggregate.function, column.name)} AS {aggregate.alias}"

def getAggregateFilter(aggregate: Aggregation, col_name_map: dict[str, Column[Any]]):
    column = col_name_map.get(aggregate.column)
    if column is None:
        raise HTTPException(400, f"Unknown column {aggregate.column}")

    aggregation_clause = createAggregation(aggregate.function, column.name)
    condition = operations.get(aggregate.filterCondition)

    return f"{aggregation_clause} {condition.get('operator')} {aggregate.filterCriteria}"

def hashString(input: str) -> str:
    return hashlib.md5(input.encode()).hexdigest()
