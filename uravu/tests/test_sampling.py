"""
Tests for sampling module
"""

# Copyright (c) Andrew R. McCluskey
# Distributed under the terms of the MIT License
# author: Andrew R. McCluskey

import unittest
import numpy as np
import uncertainties
from numpy.testing import assert_equal
from scipy.stats import norm
from uravu import sampling, utils
from uravu.relationship import Relationship
from uravu.distribution import Distribution


class TestSampling(unittest.TestCase):
    """
    Unit tests for optimize module.
    """

    def test_mcmc_a(self):
        """
        Test mcmc function.
        """
        test_x = np.linspace(0, 99, 10)
        test_y = (
            np.linspace(1, 199, 10)
            + np.linspace(1, 199, 10) * np.random.randn(10) * 0.05
        )
        test_y_e = test_y * 0.2
        test_rel = Relationship(utils.straight_line, test_x, test_y, test_y_e,)
        test_rel.max_likelihood()
        actual_variables = sampling.mcmc(test_rel, n_burn=10, n_samples=10)
        assert_equal(isinstance(actual_variables[0], Distribution), True)
        assert_equal(isinstance(actual_variables[1], Distribution), True)
        assert_equal(actual_variables[0].size, 1000)
        assert_equal(actual_variables[1].size, 1000)

    def test_mcmc_b(self):
        """
        Test mcmc function with custom prior.
        """
        test_x = np.linspace(0, 99, 10)
        test_y = (
            np.linspace(1, 199, 10)
            + np.linspace(1, 199, 10) * np.random.randn(10) * 0.05
        )
        test_y_e = test_y * 0.2
        test_rel = Relationship(utils.straight_line, test_x, test_y, test_y_e,)
        test_rel.max_likelihood()

        def other_prior(array):
            """
            Another potential prior.
            """
            broad = np.copy(array)
            for i, variable in enumerate(test_rel.variables):
                loc = variable - variable * 5
                scale = (variable + variable * 5) - loc
                broad[i] = norm.ppf(broad[i], loc=loc, scale=scale)
            return broad

        actual_variables = sampling.mcmc(
            test_rel, prior_function=other_prior, n_burn=10, n_samples=10
        )
        assert_equal(isinstance(actual_variables[0], Distribution), True)
        assert_equal(isinstance(actual_variables[1], Distribution), True)
        assert_equal(actual_variables[0].size, 1000)
        assert_equal(actual_variables[1].size, 1000)

    def test_nested_sampling_a(self):
        """
        Test nested sampling.
        """
        test_y = np.ones(10) * np.random.randn(10)
        test_y_e = np.ones(10) * 0.1
        test_x = np.linspace(1, 10, 10)
        test_rel = Relationship(utils.straight_line, test_x, test_y, test_y_e)
        actual_ln_evidence = sampling.nested_sampling(test_rel, maxiter=10)
        assert_equal(
            isinstance(actual_ln_evidence, uncertainties.core.Variable), True
        )

    def test_nested_sampling_b(self):
        """
        Test nested_sampling function with custom prior.
        """
        test_y = np.ones(10) * np.random.randn(10)
        test_y_e = np.ones(10) * 0.1
        test_x = np.linspace(1, 10, 10)
        test_rel = Relationship(utils.straight_line, test_x, test_y, test_y_e)
        test_rel.max_likelihood()

        def other_prior(array):
            """
            Another potential prior.
            """
            broad = np.copy(array)
            for i, variable in enumerate(test_rel.variables):
                loc = variable
                scale = 1
                broad[i] = norm.ppf(broad[i], loc=loc, scale=scale)
            return broad

        actual_ln_evidence = sampling.nested_sampling(
            test_rel, prior_function=other_prior, maxiter=10
        )
        assert_equal(
            isinstance(actual_ln_evidence, uncertainties.core.Variable), True
        )
