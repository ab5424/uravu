"""
This is the Distribution class, where information about probability
distributions may be stored.
"""

# Copyright (c) Andrew R. McCluskey
# Distributed under the terms of the MIT License
# author: Andrew R. McCluskey

import numpy as np
from scipy.stats import shapiro
from uncertainties import ufloat
from uravu import UREG


class Distribution:
    """
    The container for probability distribution information.

    Attributes:
        name (str): A name for the distribution.
        unit (pint.UnitRegistry(), optional): The unit for the
            abscissa.
        size (int): Number of samples in distribution.
        samples (array_like): Samples in the distribution.
        n (float): Median of distribution (using the vocabulary of the
            `uncertainties` package).
        s (float): Symetrical uncertainty on value, taken as 95 %
            confidence interval (using the vocabulary of the `uncertainties`
            package). `None` if distribution is not normal.
        ci_points (tuple): A tuple of two. The percentiles to be stored as
            confidence interval.
        con_int (array_like): Confidence interval values.
        normal (bool): Distribution normally distributed.
    """

    def __init__(
        self,
        samples,
        name="Distribution",
        ci_points=None,
        unit=UREG.dimensionless,
    ):
        """
        Args:
            samples (array_like): Sample for the distribution.
            name (str, optional): A name to identify the distribution.
                Default is `Distribution`.
            ci_points (array_like, optional): The percentiles at which
                confidence intervals should be found. Default is
                `[2.5, 97.5]` (a 95 % confidence interval).
            unit (pint.UnitRegistry(), optional) The unit for the
                distribution. Default is dimensionless.
        """
        self.name = name
        self.unit = unit
        self.size = 0
        self.samples = np.array([])
        self.n = None
        self.s = None
        if ci_points is None:
            self.ci_points = [2.5, 97.5]
        else:
            if len(ci_points) != 2:
                raise ValueError(
                    "The ci_points must be an array or tuple of length two."
                )
            self.ci_points = ci_points
        self.con_int = np.array([])
        self.normal = False
        self.add_samples(np.array(samples))

    def __repr__(self):  # pragma: no cover
        """
        A custom representation, which is the same as the custom string
        representation.

        Returns:
            (str): String representation.
        """
        return self.__str__()

    def __str__(self):  # pragma: no cover
        """
        A custom string.

        Returns:
            (str): Detailed string representation.
        """
        representation = "Distribution: {}\nSize: {}\n".format(
            self.name, self.size
        )
        representation += "Samples: "
        if self.size > 5:
            representation += "[{:.2e} {:.2e} ... {:.2e} {:.2e}]\n".format(
                self.samples[0],
                self.samples[1],
                self.samples[-2],
                self.samples[-1],
            )
        else:
            representation += "["
            representation += " ".join(
                ["{:.2e}".format(i) for i in self.samples]
            )
            representation += "]\n"
        representation += "Median: {:.2e}\n".format(self.n)
        if self.check_normality():
            representation += "Symetrical Error: {:.2e}\n".format(self.s)
        representation += "Confidence intervals: ["
        representation += " ".join(["{:.2e}".format(i) for i in self.con_int])
        representation += "]\n"
        representation += "Confidence interval points: ["
        representation += " ".join(["{}".format(i) for i in self.ci_points])
        representation += "]\n"
        if self.n is not None:
            representation += "Reporting Value: "
            if self.check_normality():
                representation += "{}\n".format(ufloat(self.n, self.s))
            else:
                representation += "{:.2e}+{:.2e}-{:.2e}\n".format(
                    self.n, self.con_int[1], self.con_int[0]
                )
        representation += "Unit: {}\n".format(self.unit)
        representation += "Normal: {}\n".format(self.normal)
        return representation

    def check_normality(self, alpha=0.05):
        """
        Uses a Shapiro-Wilks statistical test to evaluate if samples are
        normally distributed.

        Args:
            alpha (float): Threshold value for the statistical test. Default
                is `0.05` (5 %).

        Returns:
            (bool): If the distribution is normal.
        """
        if self.size <= 3:
            self.normal = False
            self.s = None
            return False
        sampled = np.random.choice(self.samples, size=500)
        p_value = shapiro(sampled)[1]
        if p_value > alpha:
            self.normal = True
            self.s = np.std(self.samples)
            return True
        self.normal = False
        self.s = None
        return False

    def add_samples(self, samples):
        """
        Add samples to the distribution and update values such as median and
        uncertainties as appropriate.

        Args:
            samples (array_like): Samples to be added to the distribution.
        """
        self.samples = np.append(self.samples, np.array(samples).flatten())
        self.size = self.samples.size
        self.n = np.percentile(self.samples, 50.0)
        if self.size > 1:
            self.con_int = np.array(
                [np.percentile(self.samples, i) for i in self.ci_points]
            )
        self.check_normality()
