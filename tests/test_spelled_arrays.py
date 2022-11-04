from unittest import TestCase
from unittest.mock import patch

from pitchtypes.spelled_array import *
import numpy as np
import numpy.testing as nptest

# adapted from test_spelled.jl in Pitches.jl
class TestSpelledArray(TestCase):
    def arrayEqual(self, a, b):
        return self.assertIsNone(nptest.assert_array_equal(a, b))

    def test_constructors(self):
        self.assertEqual(SpelledIntervalArray(np.arange(5)-2, np.arange(5)-2),
                         asi(["-M2:3", "-P5:1", "P1:0", "P5:1", "M2:3"]))
        self.assertEqual(SpelledIntervalClassArray(np.arange(5)),
                         asic(["P1", "P5", "M2", "M6", "M3"]))
        self.assertEqual(SpelledPitchArray(np.arange(5)-2, 4-np.arange(5)),
                         asp(["Bb2", "F2", "C2", "G1", "D1"]))
        self.assertEqual(SpelledPitchClassArray(np.arange(5)-2),
                         aspc(["Bb", "F", "C", "G", "D"]))
        
        self.assertEqual(SpelledIntervalArray.from_independent(np.arange(5)-2, np.zeros(5, dtype=np.int_)),
                         asi(["m7:0", "P4:0", "P1:0", "P5:0", "M2:0"]))
        self.assertEqual(SpelledPitchArray.from_independent(np.arange(5)-2, 4-np.arange(5)),
                         asp(["Bb4", "F3", "C2", "G1", "D0"]))

    def test_parsing(self):
        self.assertEqual(asi(["M3:1", "-M3:0"]), asi([4, -4], [-1, 2]))
        self.assertEqual(asic(["m3", "-m3"]), asic([-3, 3]))
        self.assertEqual(asp(["C♭4", "Cb4"]), asp([-7,-7], [8,8]))
        self.assertEqual(aspc(["C#", "C♯"]), aspc([7,7]))

    def test_accessors(self):
        i = asi(["M3:1", "-M3:1"])
        self.arrayEqual(i.octaves(), [1, -2])
        self.arrayEqual(i.internal_octaves(), [-1, 1])
        self.arrayEqual(i.fifths(), [4, -4])
        self.arrayEqual(i.degree(), [2, 5])
        self.arrayEqual(i.generic(), [2, -2])
        self.arrayEqual(i.diatonic_steps(), [9, -9])
        manyis = ["M3:1", "-M3:1", "-P4:0", "-M7:0", "a4:0", "m7:0", "-a4:0", "-m7:0"]
        self.arrayEqual(asi(manyis).alteration(),
                        [0, 0, 0, 0, 1, -1, 1, -1])
        self.arrayEqual(asi(manyis).name(), manyis)

        ic = asic(["a5", "d4"])
        self.arrayEqual(ic.octaves(), [0, 0])
        self.arrayEqual(ic.internal_octaves(), [0, 0])
        self.arrayEqual(ic.fifths(), [8, -8])
        self.arrayEqual(ic.degree(), [4, 3])
        self.arrayEqual(ic.generic(), [4, 3])
        self.arrayEqual(ic.diatonic_steps(), [4, 3])
        manyics = ["a5", "d4", "P4", "M7", "a4", "m7"]
        self.arrayEqual(asic(manyics).alteration(),
                        [1, -1, 0, 0, 1, -1])
        self.arrayEqual(asic(manyics).name(), manyics)

        p = asp(["Ebb5", "D#-1"])
        self.arrayEqual(p.octaves(), [5, -1])
        self.arrayEqual(p.internal_octaves(), [11, -6])
        self.arrayEqual(p.fifths(), [-10, 9])
        self.arrayEqual(p.degree(), [2, 1])
        self.assertRaises(NotImplementedError, p.generic)
        self.assertRaises(NotImplementedError, p.diatonic_steps)
        manyps = ["Ebb5", "D#-1", "F4", "B3", "F#4", "Bb3"]
        self.arrayEqual(asp(manyps).alteration(),
                        [-2, 1, 0, 0, 1, -1])
        self.arrayEqual(asp(manyps).name(), manyps)
        self.arrayEqual(asp(manyps).letter(), ['E', 'D', 'F', 'B', 'F', 'B'])

        pc = aspc(["Ebb", "D#"])
        self.arrayEqual(pc.octaves(), [0, 0])
        self.arrayEqual(pc.internal_octaves(), [0, 0])
        self.arrayEqual(pc.fifths(), [-10, 9])
        self.arrayEqual(pc.degree(), [2, 1])
        self.assertRaises(NotImplementedError, pc.generic)
        self.assertRaises(NotImplementedError, pc.diatonic_steps)
        manypcs = ["Ebb", "D#", "F", "B", "F#", "Bb"]
        self.arrayEqual(aspc(manypcs).alteration(),
                        [-2, 1, 0, 0, 1, -1])
        self.arrayEqual(aspc(manypcs).name(), manypcs)
        self.arrayEqual(aspc(manypcs).letter(), ['E', 'D', 'F', 'B', 'F', 'B'])

    def test_printing(self):
        self.assertEqual(str(asi(["m3:1", "-m7:0"])), "[m3:1 -m7:0]")
        self.assertEqual(str(asic(["m3", "-m7"])), "[m3 M2]")
        self.assertEqual(str(asp(["Eb4", "D##-1"])), "[Eb4 D##-1]")
        self.assertEqual(str(aspc(["Eb", "D##"])), "[Eb D##]")
        self.assertEqual(repr(asi(["m3:1", "-m7:0"])), "asi(['m3:1', '-m7:0'])")
        self.assertEqual(repr(asic(["m3", "-m7"])), "asic(['m3', 'M2'])")
        self.assertEqual(repr(asp(["Eb4", "D##-1"])), "asp(['Eb4', 'D##-1'])")
        self.assertEqual(repr(aspc(["Eb", "D##"])), "aspc(['Eb', 'D##'])")
        
    def test_intervals(self):
        # for checking constants
        zs = np.zeros((3,5), dtype=np.int_)
        os = zs + 1

        self.assertEqual(asi(["m3:0", "m3:0", "P5:0", "-m3:0", "m3:0"]) +
                         asi(["M3:0", "M7:0", "P5:0", "M3:0", "-M3:0"]),
                         asi(["P5:0", "M2:1", "M2:1", "a1:0", "-a1:0"]))
        self.assertEqual(asi(["m3:0", "m3:0"]) - asi(["M3:0", "M6:0"]),
                         asi(["-a1:0", "-a4:0"]))
        self.assertEqual(-asi(["P4:0", "P4:0", "P5:0"]),
                         asi(["-P4:0", "P5:-1", "-P5:0"]))

        self.assertEqual(SpelledIntervalArray.unison((3,5)), asi(zs, zs))
        self.assertEqual(SpelledIntervalArray.octave((3,5)), asi(zs, os))
        self.assertEqual(SpelledIntervalArray.chromatic_semitone((3,5)), asi(os * 7, os * -4))

        self.assertEqual(asi(["P5:0", "M2:0", "-m3:0", "M3:0", "M2:0", "-M3:0"]) *
                         np.array([2, 4, 4, -3, 4, 4]),
                         asi(["M2:1", "a5:0", "-d2:1", "-a7:0", "a5:0", "-aa2:1"]))
        self.assertEqual(5 * asi(["M3:0"]), asi(["aaa4:1"]))

        self.arrayEqual(asi(["m2:0", "P1:0", "d1:0", "a1:0", "-m3:0"]).direction(),
                        [1, 0, 0, 0, -1])
        self.assertEqual(asi(["m2:0", "P1:0", "d1:0", "a1:0", "-m3:0"]).abs(),
                         asi(["m2:0", "P1:0", "d1:0", "a1:0", "m3:0"]))

        self.assertEqual(asi(["M3:3", "-M3:1"]).to_class(), asic(["M3", "m6"]))
        self.assertEqual(asi(["M3:3", "-M3:1"]).ic(), asic(["M3", "m6"]))
        self.assertEqual(asi(["M3:3", "-M3:1"]).embed(), asi(["M3:3", "-M3:1"]))

        self.assertTrue(asi(["d1:0","P1:0","a1:0","d2:0","m2:0","M2:0",
                                  "a2:0","-d2:0","-m2:0","-M2:0","-a2:0"]).is_step().all())
        self.assertFalse(asi(["d3:0", "-d3:0", "M7:0", "-M7:0",
                                   "P1:1", "-P1:1", "m2:1", "-m2:1"]).is_step().any())

    def test_ics(self):
        # for checking constants
        zs = np.zeros((3,5), dtype=np.int_)
        os = zs + 1

        self.assertEqual(asic(["m3", "m3", "P5", "-m3", "m3"]) +
                         asic(["M3", "M7", "P5", "M3", "-M3"]),
                         asic(["P5", "M2", "M2", "a1", "-a1"]))
        self.assertEqual(asic(["m3", "m3"]) - asic(["M3", "M6"]),
                         asic(["-a1", "-a4"]))
        self.assertEqual(-asic(["P4", "P4", "P5"]),
                         asic(["-P4", "P5", "-P5"]))

        self.assertEqual(SpelledIntervalClassArray.unison((3,5)), asic(zs))
        self.assertEqual(SpelledIntervalClassArray.octave((3,5)), asic(zs))
        self.assertEqual(SpelledIntervalClassArray.chromatic_semitone((3,5)), asic(os * 7))

        self.assertEqual(asic(["P5", "M2", "-m3", "M3", "M2", "-M3"]) *
                         np.array([2, 4, 4, -3, 4, 4]),
                         asic(["M2", "a5", "-d2", "-a7", "a5", "-aa2"]))
        self.assertEqual(5 * asic(["M3"]), asic(["aaa4"]))

        self.arrayEqual(asic(["m2", "P1", "d1", "a1", "-m3"]).direction(),
                        [1, 0, 0, 0, -1])
        self.assertEqual(asic(["m2", "P1", "d1", "a1", "-m3"]).abs(),
                        asic(["m2", "P1", "d1", "a1", "m3"]))

        self.assertEqual(asic(["M3", "-M3"]).to_class(), asic(["M3", "m6"]))
        self.assertEqual(asic(["M3", "-M3"]).ic(), asic(["M3", "m6"]))
        self.assertEqual(asic(["M3", "-M3"]).embed(), asi(["M3:0", "m6:0"]))

        self.assertTrue(asic(["d1","P1","a1","d2","m2","M2",
                              "a2","-d2","-m2","-M2","-a2", "M7", "-M7"]).is_step().all())
        self.assertFalse(asic(["d3", "-d3"]).is_step().any())

    def test_pitches(self):
        self.assertEqual(asp(["Eb4", "Eb4"]) + asi(["P5:0", "-m3:0"]),
                         asp(["Bb4", "C4"]))
        self.assertEqual(asp(["Eb4", "Eb4"]) - asi(["P5:0", "-m3:0"]),
                         asp(["Ab3", "Gb4"]))
        self.assertEqual(asp(["G4", "Eb4"]) - asp(["C#4", "G4"]),
                         asi(["d5:0", "-M3:0"]))

        self.arrayEqual(asp(["Ab-1", "A#-1"]).alteration(), [-1, 1])

        self.assertEqual(asp(["Ab-1", "Eb4", "D##100"]).to_class(), aspc(["Ab", "Eb", "D##"]))
        self.assertEqual(asp(["Ab-1", "Eb4", "D##100"]).pc(), aspc(["Ab", "Eb", "D##"]))
        self.assertEqual(asp(["Ab-1", "Eb4", "D##100"]).embed(),
                         asp(["Ab-1", "Eb4", "D##100"]))

    def test_pcs(self):
        self.assertEqual(aspc(["Eb", "Eb"]) + asic(["P5", "-m3"]),
                         aspc(["Bb", "C"]))
        self.assertEqual(aspc(["Eb", "Eb"]) - asic(["P5", "-m3"]),
                         aspc(["Ab", "Gb"]))
        self.assertEqual(aspc(["G", "Eb"]) - aspc(["C#", "G"]),
                         asic(["d5", "-M3"]))

        self.arrayEqual(aspc(["Ab", "A#"]).alteration(), [-1, 1])

        self.assertEqual(aspc(["Ab", "Eb", "D##"]).to_class(), aspc(["Ab", "Eb", "D##"]))
        self.assertEqual(aspc(["Ab", "Eb", "D##"]).pc(), aspc(["Ab", "Eb", "D##"]))
        self.assertEqual(aspc(["Ab", "Eb", "D##"]).embed(),
                         asp(["Ab0", "Eb0", "D##0"]))
        
    def test_indexing(self):
        # helper for testing exceptions
        def try_assign(a, b):
            a[0] = b
        
        i = asi(["m6:0", "m7:8", "dd1:3"])
        self.assertEqual(i[0], SpelledInterval("m6:0"))
        self.assertEqual(i[[1,2]], asi(["m7:8", "dd1:3"]))
        self.assertEqual(i[[1,2,1,2]], asi(["m7:8", "dd1:3", "m7:8", "dd1:3"]))
        self.assertEqual(i[[True, False, True]], asi(["m6:0", "dd1:3"]))
        i[0] = SpelledInterval("M6:0")
        self.assertEqual(i, asi(["M6:0", "m7:8", "dd1:3"]))
        i[[1,2]] = asi(["m7:0", "dd1:0"])
        self.assertEqual(i, asi(["M6:0", "m7:0", "dd1:0"]))
        i[[0,1]] = SpelledInterval("P1:0")
        self.assertEqual(i, asi(["P1:0", "P1:0", "dd1:0"]))
        self.assertRaises(TypeError, lambda: try_assign(i, SpelledPitch("C4")))
        self.assertTrue(SpelledInterval("dd1:0") in i)
        self.assertFalse(SpelledInterval("d1:0") in i)
        self.assertFalse("x" in i)

        ic = asic(["m6", "m7", "dd1"])
        self.assertEqual(ic[0], SpelledIntervalClass("m6"))
        self.assertEqual(ic[[1,2]], asic(["m7", "dd1"]))
        self.assertEqual(ic[[1,2,1,2]], asic(["m7", "dd1", "m7", "dd1"]))
        self.assertEqual(ic[[True, False, True]], asic(["m6", "dd1"]))
        ic[0] = SpelledIntervalClass("M6")
        self.assertEqual(ic, asic(["M6", "m7", "dd1"]))
        ic[[1,2]] = asic(["m7", "dd1"])
        self.assertEqual(ic, asic(["M6", "m7", "dd1"]))
        ic[[0,1]] = SpelledIntervalClass("P1")
        self.assertEqual(ic, asic(["P1", "P1", "dd1"]))
        self.assertRaises(TypeError, lambda: try_assign(ic, SpelledPitchClass("C")))
        self.assertTrue(SpelledIntervalClass("dd1") in ic)
        self.assertFalse(SpelledIntervalClass("d1") in ic)
        self.assertFalse("x" in ic)

        p = asp(["A4", "Gb9", "E###3"])
        self.assertEqual(p[0], SpelledPitch("A4"))
        self.assertEqual(p[[1,2]], asp(["Gb9", "E###3"]))
        self.assertEqual(p[[1,2,1,2]], asp(["Gb9", "E###3", "Gb9", "E###3"]))
        self.assertEqual(p[[True, False, True]], asp(["A4", "E###3"]))
        p[0] = SpelledPitch("Ab4")
        self.assertEqual(p, asp(["Ab4", "Gb9", "E###3"]))
        p[[1,2]] = asp(["G3", "G4"])
        self.assertEqual(p, asp(["Ab4", "G3", "G4"]))
        p[[0,1]] = SpelledPitch("C3")
        self.assertEqual(p, asp(["C3", "C3", "G4"]))
        self.assertRaises(TypeError, lambda: try_assign(p, SpelledInterval("M2:0")))
        self.assertTrue(SpelledPitch("G4") in p)
        self.assertFalse(SpelledPitch("D4") in p)
        self.assertFalse("x" in p)

        pc = aspc(["A", "Gb", "E###"])
        self.assertEqual(pc[0], SpelledPitchClass("A"))
        self.assertEqual(pc[[1,2]], aspc(["Gb", "E###"]))
        self.assertEqual(pc[[1,2,1,2]], aspc(["Gb", "E###", "Gb", "E###"]))
        self.assertEqual(pc[[True, False, True]], aspc(["A", "E###"]))
        pc[0] = SpelledPitchClass("Ab")
        self.assertEqual(pc, aspc(["Ab", "Gb", "E###"]))
        pc[[1,2]] = aspc(["G", "G"])
        self.assertEqual(pc, aspc(["Ab", "G", "G"]))
        pc[[0,1]] = SpelledPitchClass("C")
        self.assertEqual(pc, aspc(["C", "C", "G"]))
        self.assertRaises(TypeError, lambda: try_assign(pc, SpelledIntervalClass("M2")))
        self.assertTrue(SpelledPitchClass("G") in pc)
        self.assertFalse(SpelledPitchClass("D") in pc)
        self.assertFalse("x" in pc)

    def test_copy(self):
        i = asi(["P1:0", "M2:0"])
        i2 = i.copy()
        i3 = i.deepcopy()
        self.assertEqual(i, i2)
        self.assertEqual(i, i3)
        i2[0] = SpelledInterval("a1:0")
        i3[0] = SpelledInterval("a1:0")
        self.assertNotEqual(i, i2)
        self.assertNotEqual(i, i3)
        
        ic = asic(["P1", "M2"])
        ic2 = ic.copy()
        ic3 = ic.deepcopy()
        self.assertEqual(ic, ic2)
        self.assertEqual(ic, ic3)
        ic2[0] = SpelledIntervalClass("a1")
        ic3[0] = SpelledIntervalClass("a1")
        self.assertNotEqual(ic, ic2)
        self.assertNotEqual(ic, ic3)
        
        p = asp(["E4", "B4"])
        p2 = p.copy()
        p3 = p.deepcopy()
        self.assertEqual(p, p2)
        self.assertEqual(p, p3)
        p2[0] = SpelledPitch("C4")
        p3[0] = SpelledPitch("C4")
        self.assertNotEqual(p, p2)
        self.assertNotEqual(p, p3)
        
        pc = aspc(["E", "B"])
        pc2 = pc.copy()
        pc3 = pc.deepcopy()
        self.assertEqual(pc, pc2)
        self.assertEqual(pc, pc3)
        pc2[0] = SpelledPitchClass("C")
        pc3[0] = SpelledPitchClass("C")
        self.assertNotEqual(pc, pc2)
        self.assertNotEqual(pc, pc3)

    def test_conversion(self):
        def wrap(things):
            return list(map(lambda x: [x], things))
            
        i = [SpelledInterval("P1:0"), SpelledInterval("M2:1")]
        i2 = ["P1:0", "M2:1"]
        self.assertEqual(asi(i), asi(i2))
        self.assertEqual(list(asi(i2)), i)
        self.assertEqual(list(asi(wrap(i))), list(map(asi, wrap(i2))))
        
        ic = [SpelledIntervalClass("P1"), SpelledIntervalClass("M2")]
        ic2 = ["P1", "M2"]
        self.assertEqual(asic(ic), asic(ic2))
        self.assertEqual(list(asic(ic2)), ic)
        self.assertEqual(list(asic(wrap(ic))), list(map(asic, wrap(ic2))))
        
        p = [SpelledPitch("C4"), SpelledPitch("D5")]
        p2 = ["C4", "D5"]
        self.assertEqual(asp(p), asp(p2))
        self.assertEqual(list(asp(p2)), p)
        self.assertEqual(list(asp(wrap(p))), list(map(asp, wrap(p2))))
        
        pc = [SpelledPitchClass("C"), SpelledPitchClass("D")]
        pc2 = ["C", "D"]
        self.assertEqual(aspc(pc), aspc(pc2))
        self.assertEqual(list(aspc(pc2)), pc)
        self.assertEqual(list(aspc(wrap(pc))), list(map(aspc, wrap(pc2))))
    
    @patch.multiple(SpelledArray, __abstractmethods__=set())
    def test_notimplemented(self):
        self.assertRaises(NotImplementedError, SpelledArray().name)
        self.assertRaises(NotImplementedError, SpelledArray().fifths)
        self.assertRaises(NotImplementedError, SpelledArray().octaves)
        self.assertRaises(NotImplementedError, SpelledArray().internal_octaves)
        self.assertRaises(NotImplementedError, SpelledArray().generic)
        self.assertRaises(NotImplementedError, SpelledArray().diatonic_steps)
        self.assertRaises(NotImplementedError, SpelledArray().alteration)
        self.assertRaises(NotImplementedError, SpelledArray().copy)
        self.assertRaises(NotImplementedError, SpelledArray().deepcopy)
        self.assertRaises(NotImplementedError, lambda: SpelledArray()[0])
        def test_setitem():
            SpelledArray()[0] = 1
        self.assertRaises(NotImplementedError, test_setitem)
        self.assertRaises(NotImplementedError, lambda: 1 in SpelledArray())
        self.assertRaises(NotImplementedError, lambda: list(SpelledArray()))
        self.assertRaises(NotImplementedError, lambda: len(SpelledArray()))

        self.assertFalse(asi("M3:0") == 1)
        self.assertFalse(asic("M3") == 1)
        self.assertFalse(asp("Ebb4") == 1)
        self.assertFalse(aspc("Ebb") == 1)

        self.assertRaises(TypeError, lambda: asi("M3:0") + 1)
        self.assertRaises(TypeError, lambda: asic("M3") + 1)
        self.assertRaises(TypeError, lambda: asp("Ebb4") + 1)
        self.assertRaises(TypeError, lambda: aspc("Ebb") + 1)

        self.assertRaises(TypeError, lambda: asi("M3:0") - 1)
        self.assertRaises(TypeError, lambda: asic("M3") - 1)
        self.assertRaises(TypeError, lambda: asp("Ebb4") - 1)
        self.assertRaises(TypeError, lambda: aspc("Ebb") - 1)
        self.assertRaises(TypeError, lambda: asp("Ebb4").interval_from(1))
        self.assertRaises(TypeError, lambda: aspc("Ebb").interval_from(1))

        self.assertRaises(TypeError, lambda: asi("M3:0") * "a")
        self.assertRaises(TypeError, lambda: asic("M3") * "a")
        
    def test_exceptions(self):
        self.assertRaises(ValueError, lambda: asi(["M3"]))
        self.assertRaises(ValueError, lambda: asic(["M3:0"]))
        self.assertRaises(ValueError, lambda: asp(["Ebb"]))
        self.assertRaises(ValueError, lambda: aspc(["Ebb4"]))

        self.assertRaises(ValueError, lambda: asi([0, 0], [0]))
        self.assertRaises(ValueError, lambda: asp([0, 0], [0]))
