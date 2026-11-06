import unittest
import numpy as np
from cea.demand.ventilation_schedule import ventilation_schedule


class TestVentilationSchedule(unittest.TestCase):
    def test_people_preserves_schedule(self):
        np.testing.assert_array_equal(ventilation_schedule([0, 2, 5], 7, 1500), [0, 14, 35])

    def test_area_includes_unoccupied_hours_without_mutating_people(self):
        people = np.array([0., 2., 5.])
        np.testing.assert_allclose(ventilation_schedule(people, 7, 1500, "area", .35), [525]*3)
        np.testing.assert_array_equal(people, [0, 2, 5])

    def test_area_zero(self):
        np.testing.assert_array_equal(ventilation_schedule([0, 3], 7, 0, "area"), [0, 0])
        np.testing.assert_array_equal(ventilation_schedule([0, 3], 7, 500, "area", 0), [0, 0])

    def test_invalid_configuration(self):
        for rate in [-1, np.nan, np.inf]:
            with self.subTest(rate=rate), self.assertRaises(ValueError):
                ventilation_schedule([1], 7, 500, "area", rate)
        for area in [-1, np.nan, np.inf]:
            with self.subTest(area=area), self.assertRaises(ValueError):
                ventilation_schedule([1], 7, area, "area")
        with self.assertRaises(ValueError):
            ventilation_schedule([1], 7, 500, "typo")
