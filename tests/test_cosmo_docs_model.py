"""
Automatic tests of the cosmo_model example in the documentation,
to make sure it remains up to date.
"""

from __future__ import division
import os
from contextlib import contextmanager
import sys
import numpy as np
from imageio import imread
import pytest

from cobaya.conventions import _path_install
from install_for_tests import process_modules_path

tests_folder = os.path.dirname(os.path.realpath(__file__))
docs_folder = os.path.join(tests_folder, "../docs")
docs_src_folder = os.path.join(docs_folder, "src_examples/cosmo_model/")
docs_img_folder = os.path.join(docs_folder, "img")

# Number of possible different pixels
pixel_tolerance = 0.995

# Capture stdout in string
if (sys.version_info > (3, 0)):
    from io import StringIO
else:
    from StringIO import StringIO


@contextmanager
def stdout_redirector(stream):
    old_stdout = sys.stdout
    sys.stdout = stream
    try:
        yield
    finally:
        sys.stdout = old_stdout


@pytest.mark.py3incompatible
def test_cosmo_docs_model(modules):
    modules = process_modules_path(modules)
    # Go to the folder containing the python code
    cwd = os.getcwd()
    os.chdir(docs_src_folder)
    globals_example = {}
    exec (open(os.path.join(docs_src_folder, "1.py")).read(), globals_example)
    globals_example["info"][_path_install] = modules
    exec (open(os.path.join(docs_src_folder, "2.py")).read(), globals_example)
    stream = StringIO()
    with stdout_redirector(stream):
        exec (open(os.path.join(docs_src_folder, "3.py")).read(), globals_example)
    # Comparing text output for this cell -- only derived parameter values
    out_filename = "3.out"
    derived_line_old, derived_line_new = map(
        lambda lines: next(line for line in lines[::-1] if line),
        [open(os.path.join(docs_src_folder, out_filename)).readlines(),
         stream.getvalue().split("\n")])
    derived_params_old, derived_params_new = map(
        lambda x: eval(x[x.find("{"):]), [derived_line_old, derived_line_new])
    assert np.allclose(derived_params_old.values(), derived_params_new.values()), (
            "Wrong derived parameters line:\nBEFORE: %s\nNOW:    %s" %
            (derived_line_old, derived_line_new))
    # Compare plots
    pre = "cosmo_model_"
    for filename, imgname in zip(["4.py", "5.py"], ["cltt.png", "omegacdm.png"]):
        exec (open(os.path.join(docs_src_folder, filename)).read(), globals_example)
        old_img = imread(os.path.join(docs_img_folder, pre + imgname)).astype(float)
        new_img = imread(imgname).astype(float)
        npixels = (lambda x: x.shape[0] + x.shape[1])(old_img)
# Image tests disabled
#        assert np.count_nonzero(old_img == new_img) / (4 * npixels) >= pixel_tolerance, (
#                "Images '%s' are too different!" % imgname)
    # Back to the working directory of the tests, just in case, and restart the rng
    os.chdir(cwd)
