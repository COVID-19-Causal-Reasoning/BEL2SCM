# -*- coding: utf-8 -*-

"""Test the probability DSL."""

import itertools as itt
import unittest

from bel2scm.probability_dsl import (
    ConditionalProbability, CounterfactualVariable, Fraction, Intervention, JointProbability, P, Sum, Variable,
)
from tests.probability_constants import A, B, C, D, Q, S, T, W, X, Y, Z


class TestDSL(unittest.TestCase):
    """Tests for the stringifying instances of the probability DSL."""

    def assert_latex(self, s: str, expression):
        """Assert the expression when it is converted to a string."""
        self.assertIsInstance(s, str)
        self.assertEqual(s, expression.to_latex())

    def test_variable(self):
        self.assert_latex('A', Variable('A'))
        self.assert_latex('A', A)  # shorthand for testing purposes

    def test_intervention(self):
        self.assert_latex('W*', Intervention('W', True))
        self.assert_latex('W', Intervention('W', False))
        self.assert_latex('W', Intervention('W'))  # False is the default
        self.assert_latex('W', W)  # shorthand for testing purposes

        # inversions using the unary ~ operator
        self.assert_latex('W', ~Intervention('W', True))
        self.assert_latex('W*', ~Intervention('W', False))  # False is still the default
        self.assert_latex('W*', ~Intervention('W'))
        self.assert_latex('W*', ~W)

    def test_counterfactual_variable(self):
        # Normal instantiation
        self.assert_latex('Y_{W}', CounterfactualVariable('Y', [W]))
        self.assert_latex('Y_{W*}', CounterfactualVariable('Y', [~W]))

        # Instantiation with list-based operand to matmul @ operator
        self.assert_latex('Y_{W}', Variable('Y') @ [W])
        self.assert_latex('Y_{W}', Y @ [W])
        self.assert_latex('Y_{W*}', Variable('Y') @ [~W])
        self.assert_latex('Y_{W*}', Y @ [~W])

        # Instantiation with two variables
        self.assert_latex('Y_{X,W*}', CounterfactualVariable('Y', [Intervention('X'), ~Intervention('W')]))

        # Instantiation with matmul @ operator and single operand
        self.assert_latex('Y_{W}', Y @ Intervention('W'))
        self.assert_latex('Y_{W*}', Y @ ~Intervention('W'))

        # Instantiation with matmul @ operator and list operand
        self.assert_latex('Y_{X,W*}', Y @ [X, ~W])

        # Instantiation with matmul @ operator (chained)
        self.assert_latex('Y_{X,W*}', Y @ X @ ~W)

    def test_counterfactual_errors(self):
        """Test that if two variables with the same name are given, an error is raised, regardless of star state."""
        for a, b in itt.product([True, False], [True, False]):
            with self.subTest(a=a, b=b), self.assertRaises(ValueError):
                Y @ Intervention('X', star=a) @ Intervention('X', star=b)

    def test_conditional(self):
        # Normal instantiation
        self.assert_latex('A|B', ConditionalProbability(A, [B]))

        # Instantiation with list-based operand to or | operator
        self.assert_latex('A|B', Variable('A') | [B])
        self.assert_latex('A|B', A | [B])

        # # Instantiation with two variables
        self.assert_latex('A|B,C', A | [B, C])

        # Instantiation with or | operator and single operand
        self.assert_latex('A|B', Variable('A') | B)
        self.assert_latex('A|B', A | B)

        # Instantiation with or | operator (chained)
        self.assert_latex('A|B,C', A | B | C)

        # Counterfactual uses work basically the same.
        #  Note: @ binds more tightly than |, but it's probably better to use parentheses
        self.assert_latex('Y_{W}|B', (Y @ W) | B)
        self.assert_latex('Y_{W}|B', Y @ W | B)
        self.assert_latex('Y_{W}|B,C', Y @ W | B | C)
        self.assert_latex('Y_{W,X*}|B,C', Y @ W @ ~X | B | C)
        self.assert_latex('Y_{W,X*}|B_{Q*},C', Y @ W @ ~X | B @ Intervention('Q', True) | C)

    def test_conditional_probability(self):
        self.assert_latex('P(A|B)', P(ConditionalProbability(A, [B])))
        self.assert_latex('P(A|B)', P(A | [B]))
        self.assert_latex('P(A|B,C)', P(ConditionalProbability(A, [B]) | C))
        self.assert_latex('P(A|B,C)', P(A | [B, C]))
        self.assert_latex('P(A|B,C)', P(A | B | C))

    def test_joint(self):
        self.assert_latex('A,B', JointProbability([A, B]))
        self.assert_latex('A,B', A & B)
        self.assert_latex('A,B,C', JointProbability([A, B, C]))
        self.assert_latex('A,B,C', A & B & C)

    def test_joint_probability(self):
        # Shortcut for list building
        self.assert_latex('P(A,B)', P([A, B]))
        self.assert_latex('P(A,B)', P(A & B))
        self.assert_latex('P(A,B,C)', P(A & B & C))

    def test_sum(self):
        """Test stringifying DSL instances."""
        # Sum with no variables
        self.assert_latex(
            "[ sum_{} P(A|B) P(C|D) ]",
            Sum(P(A | B) * P(C | D)),
        )
        # Sum with one variable
        self.assert_latex(
            "[ sum_{S} P(A|B) P(C|D) ]",
            Sum(P(A | B) * P(C | D), [S]),
        )
        # Sum with two variables
        self.assert_latex(
            "[ sum_{S,T} P(A|B) P(C|D) ]",
            Sum(P(A | B) * P(C | D), [S, T]),
        )

        # CRAZY sum syntax! pycharm doesn't like this usage of __class_getitem__ though so idk if we'll keep this
        self.assert_latex(
            "[ sum_{S} P(A|B) P(C|D) ]",
            Sum[S](P(A | B) * P(C | D)),
        )
        self.assert_latex(
            "[ sum_{S,T} P(A|B) P(C|D) ]",
            Sum[S, T](P(A | B) * P(C | D)),
        )

        # Sum with sum inside
        self.assert_latex(
            "[ sum_{S,T} P(A|B) [ sum_{Q} P(C|D) ] ]",
            Sum(P(A | B) * Sum(P(C | D), [Q]), [S, T])
        )

    def test_jeremy(self):
        self.assert_latex(
            '[ sum_{W} P(Y_{Z*,W},X) P(D) P(Z_{D}) P(W_{X*}) ]',
            Sum(P((Y @ ~Z @ W) & X) * P(D) * P(Z @ D) * P(W @ ~X), [W]),
        )

        self.assert_latex(
            '[ sum_{W} P(Y_{Z*,W},X) P(W_{X*}) ]',
            Sum(P(Y @ ~Z @ W & X) * P(W @ ~X), [W]),
        )

        self.assert_latex(
            '[ sum_{W} P(Y_{Z,W},X) P(W_{X*}) ] / [ sum_{Y} [ sum_{W} P(Y_{Z,W},X) P(W_{X*}) ] ]',
            Fraction(
                Sum(P(Y @ Z @ W & X) * P(W @ ~X), [W]),
                Sum(Sum(P(Y @ Z @ W & X) * P(W @ ~X), [W]), [Y]),
            ),
        )

        self.assert_latex(
            '[ sum_{D} P(Y_{Z*,W},X) P(D) P(Z_{D}) P(W_{X*}) ]',
            Sum(P(Y @ ~Z @ W & X) * P(D) * P(Z @ D) * P(W @ ~X), [D]),
        )
