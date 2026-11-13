"""End-to-end test: build the example site and compare every output file with
the expected output checked in under test/expected/.

After an intentional change to the output, regenerate the expected files and
review the diff in git:

  UPDATE_EXPECTED=1 uv run --with pytest pytest test/test_e2e.py
"""
import datetime
import difflib
import os
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'src'))

import SiteBuilder as site_builder_module
from SiteBuilder import SiteBuilder
from SiteLoader import SiteLoader
from Utils import Date

EXAMPLE_CONFIG = os.path.join(ROOT, 'example', 'lightning.yaml')
EXPECTED = os.path.join(ROOT, 'test', 'expected')
# The build stamps feeds with the current time; pin it so output is stable.
FIXED_NOW = datetime.datetime(2020, 1, 1, 12, 0, 0)


def build_example(output_root, monkeypatch):
  monkeypatch.setattr(site_builder_module.Date, 'Now',
      staticmethod(lambda: Date(FIXED_NOW)))
  # Leave out content/staging, which deliberately shadows pages/about.md.
  loader = SiteLoader(EXAMPLE_CONFIG, include_staging=False)
  loader.Load()
  loader.build_config.output_root = output_root
  SiteBuilder(loader.build_config).BuildSite(loader.site_config)


def list_files(root):
  return sorted(os.path.relpath(os.path.join(dirpath, f), root)
      for dirpath, _, filenames in os.walk(root) for f in filenames)


def read(path):
  with open(path, 'rb') as f:
    return f.read()


def test_example_site_matches_expected(tmp_path, monkeypatch):
  output = str(tmp_path / 'www')
  build_example(output, monkeypatch)

  if os.environ.get('UPDATE_EXPECTED'):
    shutil.rmtree(EXPECTED, ignore_errors=True)
    shutil.copytree(output, EXPECTED)
    return

  assert list_files(output) == list_files(EXPECTED)

  for name in list_files(EXPECTED):
    actual, expected = read(os.path.join(output, name)), \
        read(os.path.join(EXPECTED, name))
    if actual != expected:
      diff = '\n'.join(difflib.unified_diff(
          expected.decode(errors='replace').splitlines(),
          actual.decode(errors='replace').splitlines(),
          'expected/' + name, 'actual/' + name, lineterm=''))
      raise AssertionError(f'{name} differs from expected output. If the '
          f'change is intended, rerun with UPDATE_EXPECTED=1.\n{diff[:4000]}')


def test_build_is_repeatable(tmp_path, monkeypatch):
  first, second = str(tmp_path / 'a'), str(tmp_path / 'b')
  build_example(first, monkeypatch)
  build_example(second, monkeypatch)
  assert list_files(first) == list_files(second)
  for name in list_files(first):
    assert read(os.path.join(first, name)) == read(os.path.join(second, name))
