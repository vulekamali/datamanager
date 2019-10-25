from tablib import Dataset
import unittest
from budgetportal import irm_preprocessor


class PreprocessTestCase(unittest.TestCase):
    def test_incorrect_first_header(self):
        with self.assertRaises(irm_preprocessor.InputException) as context:
            irm_preprocessor.preprocess(Dataset(headers=["badheader"]))
        expected_message = "Expected header Project ID in column 1 but got badheader"
        self.assertEqual(expected_message, context.exception.message)

    def test_incorrect_other_base_header(self):
        with self.assertRaises(irm_preprocessor.InputException) as context:
            irm_preprocessor.preprocess(Dataset(headers=["Project ID", "badheader"]))
        expected_message = "Expected header Project No in column 2 but got badheader"
        self.assertEqual(expected_message, context.exception.message)

    def test_incorrect_first_project_contractor_header(self):
        with self.assertRaises(irm_preprocessor.InputException) as context:
            headers = irm_preprocessor.BASE_HEADERS + ["badheader"]
            irm_preprocessor.preprocess(Dataset(headers=headers))
        expected_message = (
            "Expected header Project Contractor in column 37 but got badheader"
        )
        self.assertEqual(expected_message, context.exception.message)

    def test_incorrect_other_project_contractor_header(self):
        with self.assertRaises(irm_preprocessor.InputException) as context:
            headers = (
                irm_preprocessor.BASE_HEADERS
                + ["Project Contractor"] * 3
                + ["badheader"]
            )
            irm_preprocessor.preprocess(Dataset(headers=headers))
        expected_message = (
            "Expected header Project Contractor in column 40 but got badheader"
        )
        self.assertEqual(expected_message, context.exception.message)
