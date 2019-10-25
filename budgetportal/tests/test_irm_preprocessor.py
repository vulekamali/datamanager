from tablib import Dataset
import unittest
from budgetportal.irm_preprocessor import (
    preprocess,
    InputException,
    BASE_HEADERS,
    REPEATED_IMPLEMENTOR_HEADER,
    get_row_implementors,
)


class PreprocessHeaderTestCase(unittest.TestCase):
    def test_incorrect_first_header(self):
        with self.assertRaises(InputException) as context:
            preprocess(Dataset(headers=["badheader"]))
        expected_message = "Expected header Project ID in column 1 but got badheader"
        self.assertEqual(expected_message, context.exception.message)

    def test_incorrect_other_base_header(self):
        with self.assertRaises(InputException) as context:
            preprocess(Dataset(headers=["Project ID", "badheader"]))
        expected_message = "Expected header Project No in column 2 but got badheader"
        self.assertEqual(expected_message, context.exception.message)

    def test_incorrect_first_project_contractor_header(self):
        with self.assertRaises(InputException) as context:
            headers = BASE_HEADERS + ["badheader"]
            preprocess(Dataset(headers=headers))
        expected_message = (
            "Expected header Project Contractor in column 37 but got badheader"
        )
        self.assertEqual(expected_message, context.exception.message)

    def test_incorrect_other_project_contractor_header(self):
        with self.assertRaises(InputException) as context:
            headers = BASE_HEADERS + [REPEATED_IMPLEMENTOR_HEADER] * 3 + ["badheader"]
            preprocess(Dataset(headers=headers))
        expected_message = (
            "Expected header Project Contractor in column 40 but got badheader"
        )
        self.assertEqual(expected_message, context.exception.message)

    def test_correct_header(self):
        headers = BASE_HEADERS + [REPEATED_IMPLEMENTOR_HEADER] * 20
        preprocess(Dataset(headers=headers))


class PreprocessImplementorTestCase(unittest.TestCase):
    def test_get_row_implementors(self):
        row = [1] * len(BASE_HEADERS) + [
            "Main Contractor: C",
            "Principal Agent: B",
            "Program Implementing Agent: A",
        ]
        offset = len(BASE_HEADERS)
        implementor_column_indexes = [offset, offset + 1, offset + 2]
        import pdb; pdb.set_trace()
        implementors = get_row_implementors(row, implementor_column_indexes)
        self.assertEqual(implementors[0], "A")
        self.assertEqual(implementors[1], "B")
        self.assertEqual(implementors[2], "C")
