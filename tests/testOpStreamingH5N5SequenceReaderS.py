import unittest
import contextlib
import tempfile
import shutil
import os

import h5py
import z5py
import numpy

from lazyflow.graph import Graph
from lazyflow.operators.ioOperators import OpStreamingH5N5SequenceReaderS
import vigra


@contextlib.contextmanager
def tempdir():
    d = tempfile.mkdtemp()
    yield d
    shutil.rmtree(d)


class TestOpStreamingH5N5SequenceReaderS(unittest.TestCase):

    def setUp(self):
        self.graph = Graph()

    def test_2d_vigra_along_z(self):
        """Test if 2d files generated through vigra are recognized correctly"""
        # Prepare some data set for this case
        data = numpy.random.randint(0, 255, (20, 100, 200, 3)).astype(numpy.uint8)
        axistags = vigra.defaultAxistags('yxc')
        expected_axistags = vigra.defaultAxistags('zyxc')

        h5_op = OpStreamingH5N5SequenceReaderS(graph=self.graph)
        n5_op = OpStreamingH5N5SequenceReaderS(graph=self.graph)

        with tempdir() as d:
            try:
                testDataH5FileName = '{}/test.h5'.format(d)
                testDataN5FileName = '{}/test.n5'.format(d)
                # Write the dataset to an hdf5 and a n5 file
                # (Note: Don't use vigra to do this, which may reorder the axes)
                h5File = h5py.File(testDataH5FileName)
                n5File = z5py.N5File(testDataN5FileName)
                try:
                    h5File.create_group('volumes')
                    n5File.create_group('volumes')

                    internalPathString = "subvolume-{sliceIndex:02d}"
                    for sliceIndex, zSlice in enumerate(data):
                        subpath = internalPathString.format(sliceIndex=sliceIndex)
                        h5File['volumes'].create_dataset(subpath, data=zSlice)
                        n5File['volumes'].create_dataset(subpath, data=zSlice)
                        # Write the axistags attribute
                        current_path = 'volumes/{}'.format(subpath)
                        h5File[current_path].attrs['axistags'] = axistags.toJSON()
                        n5File[current_path].attrs['axistags'] = axistags.toJSON()
                finally:
                    h5File.close()
                    n5File.close()

                # Read the data with an operator
                hdf5GlobString = "{}/volumes/subvolume-*".format(testDataH5FileName)
                n5GlobString = "{}/volumes/subvolume-*".format(testDataN5FileName)
                h5_op.SequenceAxis.setValue('z')
                n5_op.SequenceAxis.setValue('z')
                h5_op.GlobString.setValue(hdf5GlobString)
                n5_op.GlobString.setValue(n5GlobString)

                assert h5_op.OutputImage.ready()
                assert n5_op.OutputImage.ready()
                assert h5_op.OutputImage.meta.axistags == expected_axistags
                assert n5_op.OutputImage.meta.axistags == expected_axistags
                assert (h5_op.OutputImage[5:10, 50:100, 100:150].wait() == data[5:10, 50:100, 100:150]).all()
                assert (n5_op.OutputImage[5:10, 50:100, 100:150].wait() == data[5:10, 50:100, 100:150]).all()
            finally:
                h5_op.cleanUp()
                n5_op.cleanUp()

    def test_2d_vigra_along_t(self):
        """Test if 2d files generated through vigra are recognized correctly"""
        # Prepare some data set for this case
        data = numpy.random.randint(0, 255, (20, 100, 200, 3)).astype(numpy.uint8)
        axistags = vigra.defaultAxistags('yxc')

        expected_axistags = vigra.defaultAxistags('tyxc')

        h5_op = OpStreamingH5N5SequenceReaderS(graph=self.graph)
        n5_op = OpStreamingH5N5SequenceReaderS(graph=self.graph)

        with tempdir() as d:
            try:
                testDataH5FileName = '{}/test.h5'.format(d)
                testDataN5FileName = '{}/test.n5'.format(d)
                # Write the dataset to an hdf5 and a n5 file
                # (Note: Don't use vigra to do this, which may reorder the axes)
                h5File = h5py.File(testDataH5FileName)
                n5File = z5py.N5File(testDataN5FileName)
                try:
                    h5File.create_group('volumes')
                    n5File.create_group('volumes')

                    internalPathString = "subvolume-{sliceIndex:02d}"
                    for sliceIndex, zSlice in enumerate(data):
                        subpath = internalPathString.format(sliceIndex=sliceIndex)
                        h5File['volumes'].create_dataset(subpath, data=zSlice)
                        n5File['volumes'].create_dataset(subpath, data=zSlice)
                        # Write the axistags attribute
                        current_path = 'volumes/{}'.format(subpath)
                        h5File[current_path].attrs['axistags'] = axistags.toJSON()
                        n5File[current_path].attrs['axistags'] = axistags.toJSON()
                finally:
                    h5File.close()
                    n5File.close()

                # Read the data with an operator
                hdf5GlobString = "{}/volumes/subvolume-*".format(testDataH5FileName)
                n5GlobString = "{}/volumes/subvolume-*".format(testDataN5FileName)
                h5_op.SequenceAxis.setValue('t')
                n5_op.SequenceAxis.setValue('t')
                h5_op.GlobString.setValue(hdf5GlobString)
                n5_op.GlobString.setValue(n5GlobString)

                assert h5_op.OutputImage.ready()
                assert n5_op.OutputImage.ready()
                assert h5_op.OutputImage.meta.axistags == expected_axistags
                assert n5_op.OutputImage.meta.axistags == expected_axistags
                assert (h5_op.OutputImage[5:10, 50:100, 100:150].wait() == data[5:10, 50:100, 100:150]).all()
                assert (n5_op.OutputImage[5:10, 50:100, 100:150].wait() == data[5:10, 50:100, 100:150]).all()
            finally:
                h5_op.cleanUp()
                n5_op.cleanUp()

    def test_3d_vigra_along_t(self):
        """Test if 3d volumes generated through vigra are recognized correctly"""
        # Prepare some data set for this case
        data = numpy.random.randint(0, 255, (10, 15, 50, 100, 3)).astype(numpy.uint8)

        axistags = vigra.defaultAxistags('zyxc')
        expected_axistags = vigra.defaultAxistags('tzyxc')

        h5_op = OpStreamingH5N5SequenceReaderS(graph=self.graph)
        n5_op = OpStreamingH5N5SequenceReaderS(graph=self.graph)

        with tempdir() as d:
            try:
                testDataH5FileName = '{}/test.h5'.format(d)
                testDataN5FileName = '{}/test.n5'.format(d)
                # Write the dataset to an hdf5 file
                # (Note: Don't use vigra to do this, which may reorder the axes)
                h5File = h5py.File(testDataH5FileName)
                n5File = z5py.N5File(testDataN5FileName)

                try:
                    h5File.create_group('volumes')
                    n5File.create_group('volumes')

                    internalPathString = "subvolume-{sliceIndex:02d}"
                    for sliceIndex, tSlice in enumerate(data):
                        subpath = internalPathString.format(sliceIndex=sliceIndex)
                        h5File['volumes'].create_dataset(subpath, data=tSlice)
                        n5File['volumes'].create_dataset(subpath, data=tSlice)
                        # Write the axistags attribute
                        current_path = 'volumes/{}'.format(subpath)
                        h5File[current_path].attrs['axistags'] = axistags.toJSON()
                        n5File[current_path].attrs['axistags'] = axistags.toJSON()
                finally:
                    h5File.close()
                    n5File.close()

                # Read the data with an operator
                hdf5GlobString = "{}/volumes/subvolume-*".format(testDataH5FileName)
                n5GlobString = "{}/volumes/subvolume-*".format(testDataN5FileName)
                h5_op.SequenceAxis.setValue('t')
                n5_op.SequenceAxis.setValue('t')
                h5_op.GlobString.setValue(hdf5GlobString)
                n5_op.GlobString.setValue(n5GlobString)

                assert h5_op.OutputImage.ready()
                assert n5_op.OutputImage.ready()
                assert h5_op.OutputImage.meta.axistags == expected_axistags
                assert n5_op.OutputImage.meta.axistags == expected_axistags
                assert (h5_op.OutputImage[0:2, 5:10, 20:50, 40:70].wait() ==
                        data[0:2, 5:10, 20:50, 40:70]).all()
                assert (n5_op.OutputImage[0:2, 5:10, 20:50, 40:70].wait() ==
                        data[0:2, 5:10, 20:50, 40:70]).all()
            finally:
                h5_op.cleanUp()
                n5_op.cleanUp()

    def test_globStringValidity(self):
        """Check whether globStrings are correctly verified"""
        testGlobString = '/tmp/test.h5'
        with self.assertRaises(OpStreamingH5N5SequenceReaderS.NoInternalPlaceholderError):
            OpStreamingH5N5SequenceReaderS.checkGlobString(testGlobString)

        testGlobString = '/tmp/test.n5'
        with self.assertRaises(OpStreamingH5N5SequenceReaderS.NoInternalPlaceholderError):
            OpStreamingH5N5SequenceReaderS.checkGlobString(testGlobString)

        testGlobString = '/tmp/test.h5/a'+os.pathsep+'/tmp/test2.h5/a'
        with self.assertRaises(OpStreamingH5N5SequenceReaderS.NotTheSameFileError):
            OpStreamingH5N5SequenceReaderS.checkGlobString(testGlobString)

        testGlobString = '/tmp/test.n5/a'+os.pathsep+'/tmp/test2.n5/a'
        with self.assertRaises(OpStreamingH5N5SequenceReaderS.NotTheSameFileError):
            OpStreamingH5N5SequenceReaderS.checkGlobString(testGlobString)

        testGlobString = '/tmp/test*.h5/a'+os.pathsep+'/tmp/test*.h5/a'
        with self.assertRaises(OpStreamingH5N5SequenceReaderS.ExternalPlaceholderError):
            OpStreamingH5N5SequenceReaderS.checkGlobString(testGlobString)

        testGlobString = '/tmp/test*.n5/a'+os.pathsep+'/tmp/test*.n5/a'
        with self.assertRaises(OpStreamingH5N5SequenceReaderS.ExternalPlaceholderError):
            OpStreamingH5N5SequenceReaderS.checkGlobString(testGlobString)

        testGlobString = '/tmp/test.jpg/*'
        with self.assertRaises(OpStreamingH5N5SequenceReaderS.WrongFileTypeError):
            OpStreamingH5N5SequenceReaderS.checkGlobString(testGlobString)

        validGlobStrings = [
            '/tmp/test.h5/*',
            '/tmp/test.h5/data1'+os.pathsep+'/tmp/test.h5/data2',
            '/tmp/test.h5/data*',
            '/tmp/test.n5/*',
            '/tmp/test.n5/data1' + os.pathsep + '/tmp/test.n5/data2',
            '/tmp/test.n5/data*'
        ]

        # Implicit test for validity; test fails if an exception is raised
        for testGlobString in validGlobStrings:
            OpStreamingH5N5SequenceReaderS.checkGlobString(testGlobString)

        self.assertTrue(True)

    def test_expandGlobStrings(self):
        expected_datasets = ['g1/g2/data2', 'g1/g2/data3']

        with tempdir() as d:
            h5_file_name = '{}/test.h5'.format(d)
            n5_file_name = '{}/test.n5'.format(d)
            try:
                h5_file = h5py.File(h5_file_name, mode='w')
                n5_file = z5py.N5File(n5_file_name, mode='w')
                h5_g1 = h5_file.create_group('g1')
                n5_g1 = n5_file.create_group('g1')
                h5_g2 = h5_g1.create_group('g2')
                n5_g2 = n5_g1.create_group('g2')
                h5_g3 = h5_file.create_group('g3')
                n5_g3 = n5_file.create_group('g3')
                h5_g1.create_dataset('data1', data=numpy.ones((10, 10)))
                n5_g1.create_dataset('data1', data=numpy.ones((10, 10)))
                h5_g2.create_dataset('data2', data=numpy.ones((10, 10)))
                n5_g2.create_dataset('data2', data=numpy.ones((10, 10)))
                h5_g2.create_dataset('data3', data=numpy.ones((10, 10)))
                n5_g2.create_dataset('data3', data=numpy.ones((10, 10)))
                h5_g3.create_dataset('data4', data=numpy.ones((10, 10)))
                n5_g3.create_dataset('data4', data=numpy.ones((10, 10)))
                h5_file.flush()

                h5_glob_res1 = OpStreamingH5N5SequenceReaderS.expandGlobStrings(
                    h5_file, '{}/g1/g2/data*'.format(h5_file_name))
                n5_glob_res1 = OpStreamingH5N5SequenceReaderS.expandGlobStrings(
                    n5_file, '{}/g1/g2/data*'.format(n5_file_name))
                self.assertEqual(h5_glob_res1, expected_datasets)
                self.assertEqual(n5_glob_res1, expected_datasets)

            finally:
                h5_file.close()
                n5_file.close()

            h5_glob_res2 = OpStreamingH5N5SequenceReaderS.expandGlobStrings(
                h5_file_name, '{}/g1/g2/data*'.format(h5_file_name))
            n5_glob_res2 = OpStreamingH5N5SequenceReaderS.expandGlobStrings(
                n5_file_name, '{}/g1/g2/data*'.format(n5_file_name))
            self.assertEqual(h5_glob_res2, expected_datasets)
            self.assertEqual(n5_glob_res2, expected_datasets)


if __name__ == "__main__":
    import sys
    import nose
    sys.argv.append("--nocapture")    # Don't steal stdout.  Show it on the console as usual.
    sys.argv.append("--nologcapture")  # Don't set the logging level to DEBUG.  Leave it alone.
    nose.run(defaultTest=__file__)
