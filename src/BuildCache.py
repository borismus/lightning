"""
TODO(smus): Bring back incremental builds!

Before loading every file in the site, first, do a walkthrough of all files
(just get the modification time and basic YAML header). Write that info to
disk in a $OUT/.build_cache file.  Then, in incremental mode, generate the
build_cache at the beginning and compare it to the previously created one.
Then you can know what files are created, updated, and deleted.
"""

class BuildCache:
  """Loads and saves the build cache, which speeds up incremental builds."""

  def __init__(self):
    pass

  def Load(self, cache_path):
    pass


  def Save(self, site, cache_path):
    pass
