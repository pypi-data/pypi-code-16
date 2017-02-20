from behave import *
import sys
import numpy as np
import tempfile

use_step_matcher("parse")


@given("parameter {} = {}")
def step_impl(context, key, value):
    """
    :param key:
    :param value:
    :type context: behave.runner.Context
    """
    #context.parser.parse_args(key, value)

    sys.argv.append(key)
    values = value.split()
    sys.argv.extend(values)
    #print(sys.argv)


@given("a matrix")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    matrix = []
    rows = context.text.split("\n")
    for i in rows:
        matrix.append(i.split(" "))
    matrix = np.array(matrix)
    context.matrix = matrix


@then("we expect the matrix")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    matrix = []
    matrix2 = []

    output = context.stdout_capture.getvalue().rstrip()
    rows = output.split("\n")
    for i in rows:
        matrix.append(i.split())
    rows = context.text.split("\n")
    for i in rows:
        matrix2.append(i.split())

    assert matrix == matrix2


@given("last parameter {}")
def step_impl(context, param):
    """
    :type context: behave.runner.Context
    """
    sys.argv.append(param)


@given("the file {} containing")
def step_impl(context, file_name):
    """
    :type context: behave.runner.Context
    """
    matrix = []
    rows = context.text.split("\n")
    for i in rows:
        matrix.append(i.split(" "))
    matrix = np.array(matrix)
    tf = tempfile.NamedTemporaryFile(delete=False)
    # print(tf.name, flush=True)
    # for i in context.text.split("\n"):
    #    tf.write(bytes(i,'UTF-8'))
    text = context.text.replace(" ", "\t")

    tf.write(bytes(text, 'UTF-8'))
    tf.close()
    setattr(context, file_name, tf.name)
    context.tmp_files.append(tf.name)


@given("file {} as parameter")
def step_impl(context, file_name):
    """
    :type context: behave.runner.Context
    """
    sys.argv.append(getattr(context, file_name))


@given("file parameter {} = {}")
def step_impl(context, key, file_name):
    """
    :param key:
    :param file_name:
    :type context: behave.runner.Context
    """
    # context.parser.parse_args(key, value)

    sys.argv.append(key)
    sys.argv.append(getattr(context, file_name))

    # print(sys.argv)

