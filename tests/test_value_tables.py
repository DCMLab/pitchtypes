from unittest import TestCase
import os
from importlib import import_module
import re

import numpy as np


class TestValueTables(TestCase):

    def make_obj(self, base_type, sub_type, val):
        """
        Initialise an object of base_type.sub_type with val
        :param base_type: the base type
        :param sub_type: the sub-type
        :param val: the value
        :return: the object
        """
        if sub_type == "Pitch":
            return base_type.Pitch(val)
        elif sub_type == "Interval":
            return base_type.Interval(val)
        elif sub_type == "PitchClass":
            return base_type.PitchClass(val)
        elif sub_type == "IntervalClass":
            return base_type.IntervalClass(val)
        else:
            self.fail(f"Unknown type {sub_type}")

    def test_value_tables(self):
        # regular expression for selecting what operation to perform on what type
        type_regex = re.compile("^(?P<type>Pitch|Interval|PitchClass|IntervalClass)$")
        operation_regex = re.compile("^(?P<type1>Pitch|Interval|PitchClass|IntervalClass)"
                                     "_(?P<operation>.+)_"
                                     "(?P<type2>Pitch|Interval|PitchClass|IntervalClass)$")
        inversion_regex = re.compile("^(?P<type>Interval|IntervalClass)_inversion$")
        # go through the folders in base_dir containing value tables
        base_dir = "value_tables"
        for folder in os.listdir(base_dir):
            # remember what type checks have been done
            type_checks = {"Pitch": False,
                           "Interval": False,
                           "PitchClass": False,
                           "IntervalClass": False}
            # remember what operation checks have been done
            operation_checks = {"Pitch_plus_Interval": False,
                                "Interval_plus_Interval": False,
                                "Pitch_minus_Pitch": False,
                                "Pitch_minus_Interval": False,
                                "Interval_minus_Interval": False,
                                "PitchClass_plus_IntervalClass": False,
                                "IntervalClass_plus_IntervalClass": False,
                                "PitchClass_minus_PitchClass": False,
                                "PitchClass_minus_IntervalClass": False,
                                "IntervalClass_minus_IntervalClass": False}
            # remember what inversion checks have been done
            inversion_checks = {"Interval": False,
                                "IntervalClass": False}
            # ignore dot files
            if folder.startswith("."):
                continue
            # the folders are assumed to be named according to the base types, which are imported
            base_type = getattr(import_module('pitchtypes'), folder)
            # go through all the value tables
            for table in os.listdir(os.path.join(base_dir, folder)):
                # ignore files that don't end with ".txt" (like backup files etc)
                if not table.endswith(".txt"):
                    continue
                # load the table as string array
                arr = np.loadtxt(os.path.join(base_dir, folder, table),
                                 ndmin=2,
                                 dtype=str,
                                 delimiter='\t',
                                 comments=None)
                # the file name without extension is used for determining the check to be performed
                check = table[:-4]
                type_match = type_regex.match(check)
                op_match = operation_regex.match(check)
                inv_match = inversion_regex.match(check)
                matches = np.array([type_match is not None, op_match is not None, inv_match is not None])
                self.assertFalse(matches.sum() == 0,
                                 f"Could not match {check} against any of the regular expressions ({matches}):\n"
                                 f"{type_regex.pattern}\n{operation_regex.pattern}\n{inversion_regex.pattern}")
                self.assertTrue(matches.sum() == 1,
                                f"Found more than one match for {check} against the regular expressions ({matches}):\n"
                                f"{type_regex.pattern}\n{operation_regex.pattern}\n{inversion_regex.pattern}")
                # type checks
                if type_match is not None:
                    # go through all values (if the first dimension is of length 1; its a row vector)
                    for val in arr[0, :]:
                        # get the object
                        obj = self.make_obj(base_type=base_type, sub_type=type_match['type'], val=val)
                        # make sure it prints as the string it was initialised from
                        self.assertEqual(str(obj), val)
                    # mark type as checked
                    type_checks[type_match['type']] = True
                elif op_match is not None:
                    # otherwise it's an operation check
                    # iterate through rows (skip first)
                    for idx_1 in range(1, arr.shape[0]):
                        # initialise first object from first column
                        obj_1 = self.make_obj(base_type=base_type,
                                              sub_type=op_match['type1'],
                                              val=arr[idx_1, 0])
                        # iterate through columns (skip first)
                        for idx_2 in range(1, arr.shape[1]):
                            # initialise second object from first row
                            obj_2 = self.make_obj(base_type=base_type,
                                                  sub_type=op_match['type2'],
                                                  val=arr[0, idx_2])
                            # determine the operation to check
                            operation = op_match['operation']
                            # remember result for error reporting
                            res = None
                            # catch errors (an later re-raise) for better reporting
                            try:
                                # check that result from operations prints as indicated in the table
                                if operation == "minus":
                                    res = obj_1 - obj_2
                                    self.assertEqual(str(res), arr[idx_1, idx_2])
                                elif operation == "plus":
                                    res = obj_1 + obj_2
                                    self.assertEqual(str(res), arr[idx_1, idx_2])
                                else:
                                    self.fail(f"Unknown operation '{operation}'")
                            except:
                                # in case of error: report objects and operation for better debugging
                                print(f"{obj_1} {type(obj_1)} {operation} {obj_2} {type(obj_2)} == {res} {type(res)} "
                                      f"(should be {arr[idx_1, idx_2]})")
                                # re-raise original error
                                raise
                    # mark operation as checked
                    operation_checks[check] = True
                elif inv_match is not None:
                    self.fail()
                else:
                    self.fail()
            # make sure all sub-types were checked
            if not np.all(list(type_checks.values())):
                unchecked_types = ''.join(f"\n    {key}" for key, val in type_checks.items() if not val)
                self.fail(f"For base type {folder} some types were not checked:{unchecked_types}")
            # make sure all operations were checked
            if not np.all(list(operation_checks.values())):
                unchecked_ops = ''.join(f"\n    {key}" for key, val in operation_checks.items() if not val)
                self.fail(f"For base type {folder} some operations were not checked:{unchecked_ops}")
            # make sure all inversions were checked
            if not np.all(list(inversion_checks.values())):
                unchecked_inversions = ''.join(f"\n    {key}" for key, val in inversion_checks.items() if not val)
                self.fail(f"For base type {folder} some inversions were not checked:{unchecked_inversions}")
