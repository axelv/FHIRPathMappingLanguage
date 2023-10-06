import click
import logging
from pprint import pprint
from fhirpathpy import evaluate
import colorlog
import json

LOGGER = logging.getLogger(__name__)
LOGGER.handlers = []
# handler = colorlog.StreamHandler()
# handler.setFormatter(
# colorlog.ColoredFormatter("%(blue)s%(levelname)s:%(name)s:%(message)s")
# )
# LOGGER.addHandler(handler)


def strip_fhirpath(key: str):
    return key.strip("{{").strip("}}").strip()


def evaluate_expression(expression: str, qr: dict, **context):
    fhirpath_expr = strip_fhirpath(expression)
    result = evaluate(qr, fhirpath_expr, context)
    LOGGER.debug(
        f'Expression "{fhirpath_expr}" evaluated to {result}.\ncontext {context}'
    )
    assert isinstance(result, list)
    return result


def postprocess_result(result):
    match len(result):
        case 0:
            return None
        case 1:
            return result[0]
        case _:
            return result


def has_expression_key(d: dict):
    for key in d.keys():
        if is_expression(key):
            return key
    return False


def is_expression(value: str):
    return value.startswith("{{") and value.endswith("}}")


def map_value(d: dict | list | int | bool | str, qr: dict, **context):
    match d:
        case dict():
            return map_dict_value(d, qr, **context)
        case list():
            return map_list_value(d, qr, **context)
        case str():
            if is_expression(d):
                return postprocess_result(evaluate_expression(d, qr, **context))
            else:
                return d
        case _:
            return d


def map_list_value(l: list, qr: dict, **context):
    mapped_values = [map_value(item, qr, **context) for item in l]
    return [item for item in mapped_values if item is not None]


def map_dict_value(d: dict, qr: dict, **context):
    maybe_has_expression_key = has_expression_key(d)
    if maybe_has_expression_key:
        value = d[maybe_has_expression_key]
        result = evaluate_expression(maybe_has_expression_key, qr, **context)
        if len(result) == 1 and result[0] is True:
            LOGGER.debug(f"Expression evaluated to True")
            return map_value(value, qr, **context)
        if len(result) == 1 and result[0] is False:
            LOGGER.debug(f"Expression evaluated to False")
            return None
        if len(result) > 0:
            LOGGER.debug(f"Expression evaluated to a list")
            return [map_value(value, qr, **context, **item) for item in result]
        raise NotImplementedError(f"Expression returned a value of type {type(result)}")
    else:
        mapped_d = dict()
        for key, value in d.items():
            mapped_value = map_value(value, qr, **context)
            LOGGER.debug(f"Resolved {key} to {mapped_value}")
            if mapped_value is not None:
                mapped_d[key] = mapped_value
        return mapped_d


@click.command()
@click.argument("input", type=click.File("r"))
@click.option("--output", type=click.File("w"))
@click.option("--mapper", type=click.File("r"))
def main(input, output, mapper):
    logging.basicConfig(level=logging.DEBUG)
    mapper_dict = json.load(mapper)
    qr_dict = json.load(input)

    mapper_output = map_dict_value(mapper_dict, qr_dict)
    if output:
        json.dump(mapper_output, output)
    else:
        pprint(mapper_output)
