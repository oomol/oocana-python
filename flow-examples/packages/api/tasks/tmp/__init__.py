from oocana import Context
import sys

#region generated meta
import typing
import os
class Inputs(typing.TypedDict):
  input: str
class Outputs(typing.TypedDict):
  output: str
#endregion

def main(params: Inputs, context: Context) -> Outputs:
  assert(context.tmp_dir is not None)
  assert(context.tmp_pkg_dir is not None)

  # Check if tmp_dir is exist
  assert os.path.exists(context.tmp_dir), f"tmp_dir does not exist at {context.tmp_dir}"
  assert os.path.isdir(context.tmp_dir), f"tmp_dir is not a directory at {context.tmp_dir}"

  # Also check tmp_pkg_dir
  assert os.path.exists(context.tmp_pkg_dir), f"tmp_pkg_dir does not exist at {context.tmp_pkg_dir}"
  assert os.path.isdir(context.tmp_pkg_dir), f"tmp_pkg_dir is not a directory at {context.tmp_pkg_dir}"

  # Write a file in tmp_dir
  test_file_path = os.path.join(context.tmp_dir, "test_file.txt")
  with open(test_file_path, "w") as f:
    f.write("This is a test file")

  # Check if the file exists
  assert os.path.exists(test_file_path), f"File was not created at {test_file_path}"

  # You can also write a file in tmp_pkg_dir
  pkg_test_file_path = os.path.join(context.tmp_pkg_dir, "pkg_test_file.txt")
  with open(pkg_test_file_path, "w") as f:
    f.write("This is a package test file")

  # Check if the file exists
  assert os.path.exists(pkg_test_file_path), f"File was not created at {pkg_test_file_path}"

  print(sys.path)
  context.logger.info(sys.path)

  return { "output": "output_value" }
