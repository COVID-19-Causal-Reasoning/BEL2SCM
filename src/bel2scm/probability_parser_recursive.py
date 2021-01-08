# -*- coding: utf-8 -*-

from pyparsing import Forward, Group, OneOrMore, Optional, Suppress

from bel2scm.probability_dsl import Expression
from bel2scm.probability_parser import _make_frac, _make_product, _make_sum, probability_pe, variables_pe

expr = Forward()

product_pe = expr + OneOrMore(expr)
product_pe.setParseAction(_make_product)

sum_pe = (
    Suppress('[')
    + Suppress('sum_{')
    + Optional(Group(variables_pe).setResultsName('ranges'))
    + Suppress('}')
    + expr.setResultsName('expression')
    + Suppress(']')
)
sum_pe.setParseAction(_make_sum)

fraction_pe = (
    expr.setResultsName('numerator')
    + Suppress('/')
    + expr.setResultsName('denominator')
)
fraction_pe.setParseAction(_make_frac)

expr << (fraction_pe | sum_pe | product_pe | probability_pe)


def parse(s: str) -> Expression:
    """Parse an expression."""
    x = expr.parseString(s)
    return x.asList()[0]


if __name__ == '__main__':
    print(parse('P(A)'))
    print(parse('[ sum_{} P(A|B) ]'))
