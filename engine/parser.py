import os
import pickle
import time
import datetime

import yaml
import markdown2
import pystache

DATE_FORMAT = '%Y-%m-%d %H:%M'


class SiteBuilder:

  def __init__(self):
    self.content_root = self.find_content_root()
    self.output_root = self.find_output_root()
    self.template_root = self.find_template_root()

    self.cache_path = self.output_root + '.last_build'
    self.site_config_path = self.content_root + 'site.yaml'

  def get_items(self):
    """Gets all items in this site.

    Returns an array of item infos of files in the site, in the format:
    {
      "path": "relative/post.txt",
      "modified": NNNNNN
    }
    """
    files = []
    # Get all files that end with .txt.
    for dirpath, dirnames, filenames in os.walk(self.content_root):
      for fname in filenames:
        if fname.endswith(".txt"):
          # Get the file's path and modified time
          path = os.path.join(dirpath, fname)
          files.append({
            'path': path,
            'modified': os.stat(path).st_mtime
          })

    return files

  def get_cache(self):
    """Gets all of the files involved in the previously built version of the
    static site.
    """
    # Find the cache (it's in $ROOT/.last_build).
    if not os.path.exists(self.cache_path):
      return []
    cache_file = open(self.cache_path, 'r')
    # Load the contents of the cache.
    cache = pickle.load(cache_file)
    return cache

  def save_cache(self, cache_data):
    """Pickles the cache into the proper cache root.

    Cache should be a list of objects like the following: {
      "modified": DDDD,
      "path": "/path/to-foo.txt"
      "info": {
        "title": "My new post",
        ... (other parsed data except the content).
      }
    }"""
    cache_file = open(self.cache_path, 'w')
    pickle.dump(cache_data, cache_file)

  def find_content_root(self):
    """Finds the root of the content for this static site.
    """
    potential_pathes = ['./content/', '../content/']
    for path in potential_pathes:
      if os.path.exists(path):
        return path


  def find_output_root(self):
    """Finds the root of the output for the site."""
    path = self.content_root + '../www/'
    if not os.path.exists(path):
      os.mkdir(path)

    return path

  def find_template_root(self):
    """Finds the root of the content for this static site.
    """
    potential_pathes = ['./template/', '../template/']
    for path in potential_pathes:
      if os.path.exists(path):
        return path


  def parse_date(self, date_string):
    """Gets the permalink parameters based on the item's info."""
    print date_string
    parsed = {}
    # Parse the posted date into year, month, day.
    t_tuple = time.strptime(date_string, DATE_FORMAT)
    t = datetime.datetime(*t_tuple[:6])
    return {
      'year': t.year,
      'month': t.month,
      'day': t.day,
      'hour': t.hour,
      'minute': t.minute
    }


  def load_template(self, name):
    """Loads a template with the given name. Returns a string with the
    template's contents."""
    f = open(self.template_root + name + '.html')
    return f.read()

  def parse_item(self, path):
    """Parses markup from files like this:

      My new post
      ===========
      - type: post
      - posted: 2012-03-01 9:00
      - slug: my-new-post

      Just **testing**

    into an object like this:

      {
        "title": "My new post",
        "type": "post",
        "slug": "my-new-post",
        "posted": "2012-03-01 9:00",
        "posted_info": {
          "year": 2012,
          "month": 03,
          "day": 1,
          "hour": 9,
          "min": 0
        }
        "content": "Just <b>testing</b>"
      }
    """
    # Load the file.
    f = open(path, 'r')
    lines = f.readlines()
    # TODO: Perform some basic validation.
    # Extract the title.
    title = lines[0].strip()
    # Get the key: value pairs after the title.
    separator_index = lines.index('\n')
    yaml_lines = lines[2:separator_index]
    data = yaml.load(''.join(yaml_lines))
    # Process the rest of the post as Markdown.
    markdown_lines = lines[separator_index+1:]
    content = markdown2.markdown(''.join(markdown_lines))
    # Put everything in a dict.
    data['title'] = title
    data['content'] = content
    # Parse the date if it's specified.
    if 'posted' in data:
      data['posted_info'] = self.parse_date(data['posted'])
    # Return the dict.
    return data


  def parse_site(self):
    """Parses a site.yaml like this:

      title: My awesome blog
      permalinks:
        post: {{year}}/{{slug}}
        page: {{slug}}

    into a dict like this:

      {
        "site_title": "My awesome blog"
        "site_permalinks": {
          "post": "{{year}}/{{slug}}",
          "page": "{{slug}}"
        }
      }
    """
    # Run a YAML parser and get all the stuff as a dictionary.
    f = open(self.site_config_path, 'r')
    return yaml.load(f)

  def build_single(self, item):
    """Builds a single item."""
    info = item['info']
    # TODO: validate the item!
    # Combine the parsed information into template data.
    template_data = dict(info.items() + self.site_info.items())
    # Get the type and load the appropriate template.
    if not 'type' in info:
      print info.keys()
    type_name = info['type']
    template = self.load_template(type_name)
    # Evaluate the template with data.
    html = pystache.render(template, template_data)
    # Compute the final path based on permalink config.
    permalink_template = self.site_info['permalinks'][type_name]
    permalink_data = {'slug': info['slug']}
    # If there's date information associated, include it in the permalink data.
    if 'posted_info' in info:
      permalink_data = dict(permalink_data.items() +
          info['posted_info'].items())
    path = pystache.render(permalink_template, permalink_data)
    print path
    # Create the directory for the parsed HTML.
    # Create the index file inside the directory.
    # Copy any assets that should be copied (if applicable).

  def build_list(self, info):
    """Builds a list item that depends on the single items already being
    processed."""
    pass

  def get_list(self, type_filter, limit, order_by):
    """Gets list of posts with the given options."""
    # Only care about posts with a posted attribute.
    # Filter the list of all posts with the given parameters.

  def compare_items(self, items, cache):
    """Compares the items to the previously built items.

    Interesting things to know:
    - Was a new item added? (new path)
    - Was an item removed? (old path no longer exists)
    - Was an item updated? (same path, but updated modification time)

    Returns 3 arrays: created, updated, deleted.
    """
    # Get a list of all pathes that exist in the cache.
    cache_pathes = [c['path'] for c in cache]
    # Make it easy to look up cache mtime based on path.
    mtime_lookup = dict([(c['path'], c['modified']) for c in cache])
    # Create return arrays.
    created = []
    updated = []
    deleted = []
    # Iterate through the current items.
    for item in items:
      path = item['path']
      modified = item['modified']
      # Check if the item is in the cache.
      if path in cache_pathes:
        # If present, check if it's updated.
        cache_modified = mtime_lookup[path]
        if modified > cache_modified:
          updated.append(item)
      else:
        # If absent, it must have been just added.
        created.append(item)

      # If present, remove the checked item from the cache_pathes list.
      if path in cache_pathes:
        cache_pathes.remove(path)
        #print 'cache_pathes', cache_pathes

    # The removed items are the ones that haven't been checked.
    deleted = [i for i in cache if i['path'] in cache_pathes]

    return (created, updated, deleted)


  def build_incremental(self):
    """Performs an incremental build."""
    # Get a list of all items that exist in the site.
    items = self.get_items()
    # Look in the build directory for a saved list of files from last build.
    cache = self.get_cache()
    self.cache = cache
    print 'building incremental. cache is', len(cache)
    # Compare the two lists and get pathes that have been created/updated/etc.
    (created, updated, deleted) = self.compare_items(items, cache)
    print 'created', created, 'updated', updated, 'deleted', deleted

    # If nothing changed, we're done.
    if not created and not updated and not deleted:
      return

    # If anything was updated, parse it and update the site cache.
    for item in updated:
      path = item['path']
      new_info = self.parse_item(path)
      item['info'] = new_info
      # Remove this item in the cache.
      cache[:] = [i for i in cache if i['path'] != path]
      # Update the file entry.
      cache.append(item)

    # If something was created, parse it and add to cache.
    for item in created:
      path = item['path']
      info = self.parse_item(path)
      item['info'] = info
      # Add to cache.
      cache.append(item)

    # If something was deleted, archive from filesystem and remove
    # it from the cache.

    # Get the site info.
    self.site_info = self.parse_site()

    # Get all of the lists from the updated cache.
    lists = [i for i in cache if 'list' in i['info']]
    # Distinguish between single and lists posts.
    singles = [i for i in created + updated if 'list' not in i['info']]
    # Build all of the single files.
    for info in singles:
      self.build_single(info)
    # Build the lists.
    for info in lists:
      self.build_list(info)

    # Write out the new cache to disk.
    self.save_cache(cache)

if __name__ == '__main__':
  builder = SiteBuilder()
  builder.build_incremental()
