import unittest

from budgetportal.infra_projects.irm_preprocessor import (
    BASE_HEADERS,
    REPEATED_IMPLEMENTOR_HEADER,
    InputException,
    get_row_implementors,
    preprocess,
)
from tablib import Dataset


class PreprocessHeaderTestCase(unittest.TestCase):
    def test_incorrect_first_header(self):
        with self.assertRaises(InputException) as context:
            preprocess(Dataset(headers=["badheader"]))
        expected_message = "Expected header Project ID in column 1 but got badheader"
        self.assertEqual(expected_message, str(context.exception))

    def test_incorrect_other_base_header(self):
        with self.assertRaises(InputException) as context:
            preprocess(Dataset(headers=["Project ID", "badheader"]))
        expected_message = "Expected header Project No in column 2 but got badheader"
        self.assertEqual(expected_message, str(context.exception))

    def test_incorrect_first_project_contractor_header(self):
        with self.assertRaises(InputException) as context:
            headers = BASE_HEADERS + ["badheader"]
            preprocess(Dataset(headers=headers))
        expected_message = (
            "Expected header Project Contractor in column 38 but got badheader"
        )
        self.assertEqual(expected_message, str(context.exception))

    def test_incorrect_other_project_contractor_header(self):
        with self.assertRaises(InputException) as context:
            headers = BASE_HEADERS + [REPEATED_IMPLEMENTOR_HEADER] * 3 + ["badheader"]
            preprocess(Dataset(headers=headers))
        expected_message = (
            "Expected header Project Contractor in column 41 but got badheader"
        )
        self.assertEqual(expected_message, str(context.exception))

    def test_correct_header(self):
        headers = BASE_HEADERS + [REPEATED_IMPLEMENTOR_HEADER] * 20
        preprocess(Dataset(headers=headers))


class PreprocessImplementorTestCase(unittest.TestCase):
    def test_get_row_implementors(self):
        """Regardless of order in input, they are output in IMPLEMENTOR_HEADERS order"""
        row = [1] * len(BASE_HEADERS) + [
            "Main Contractor: C",
            "Principal Agent: B",
            "Program Implementing Agent: A",
            "Unexpected Implementor: D",
        ]
        offset = len(BASE_HEADERS)
        implementor_column_indexes = list(range(offset, offset + 4))
        implementors = get_row_implementors(row, implementor_column_indexes)
        self.assertEqual(implementors[0], "A")
        self.assertEqual(implementors[1], "B")
        self.assertEqual(implementors[2], "C")
        self.assertEqual(implementors[3], "Unexpected Implementor: D")

    def test_get_row_implementors_blanks(self):
        row = [1] * len(BASE_HEADERS) + [
            "Main Contractor: C",
            "",
            "Principal Agent: B",
            None,
            "Program Implementing Agent: A",
            "",
            "Unexpected Implementor: D",
        ]
        offset = len(BASE_HEADERS)
        implementor_column_indexes = list(range(offset, offset + 7))
        implementors = get_row_implementors(row, implementor_column_indexes)
        self.assertEqual(implementors[0], "A")
        self.assertEqual(implementors[1], "B")
        self.assertEqual(implementors[2], "C")
        self.assertEqual(implementors[3], "Unexpected Implementor: D")

    def test_get_row_implementors_multiple(self):
        row = [1] * len(BASE_HEADERS) + [
            "Main Contractor: A",
            "Main Contractor: B",
            "Principal Agent: C",
            "Principal Agent: D",
            "Program Implementing Agent: E",
            "Program Implementing Agent: F",
            "Unexpected Implementor: G",
            "Unexpected Something: H",
        ]
        offset = len(BASE_HEADERS)
        implementor_column_indexes = list(range(offset, offset + 8))
        implementors = get_row_implementors(row, implementor_column_indexes)
        self.assertEqual(implementors[0], "E\nF")  # Prog Impl Agent
        self.assertEqual(implementors[1], "C\nD")  # Principal Agent
        self.assertEqual(implementors[2], "A\nB")  # Main Contractor
        self.assertEqual(
            implementors[3], "Unexpected Implementor: G\nUnexpected Something: H"
        )

    def test_get_row_implementors_just_one(self):
        row = [1] * len(BASE_HEADERS) + ["Main Contractor: C"]
        offset = len(BASE_HEADERS)
        implementor_column_indexes = list(range(offset, offset + 1))
        implementors = get_row_implementors(row, implementor_column_indexes)
        self.assertEqual(implementors[0], "")
        self.assertEqual(implementors[1], "")
        self.assertEqual(implementors[2], "C")
        self.assertEqual(implementors[3], "")


class PreprocessEmptyRowTestCase(unittest.TestCase):
    def test_empty_rows_removed(self):
        headers = BASE_HEADERS + [REPEATED_IMPLEMENTOR_HEADER] * 20
        dataset = Dataset(headers=headers)
        non_empty_row = [1] * len(BASE_HEADERS) + [""] * 20
        dataset.append(non_empty_row)
        # There is only one row
        num_nonempty_rows = dataset.height

        # Insert 100 empty rows
        num_of_empty_rows = 100
        empty_row = [None] * len(headers)
        for i in range(num_of_empty_rows):
            dataset.append(empty_row)

        # There must be 100 empty + 1 non empty rows
        total_rows = num_nonempty_rows + num_of_empty_rows
        self.assertEqual(101, total_rows)

        # There must be only non empty row left
        dataset = preprocess(dataset)
        self.assertEqual(1, num_nonempty_rows)
