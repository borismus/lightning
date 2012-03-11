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
    # Get the roots.
    self.root = self.find_root()
    self.content_root = self.root + 'content/'
    self.template_root = self.root + 'template/'
    self.output_root = self.root + 'www/'

    # Figure out the pathes.
    self.archive_path = self.output_root + '.archived/'
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
    # Find the cache (it's in /.last_build).
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

  def find_root(self):
    """Finds the root for this static site.
    """
    required_subdirs = ['content', 'template']
    potential_roots = ['./', '../']
    for root in potential_roots:
      is_root = True
      for subdir in required_subdirs:
        if not os.path.exists(root + subdir):
          is_root = False
          break

      if is_root:
        return root

    # If we get here, failed to find the path.
    raise Exception('Unable to find site root.')

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
    parsed = {}
    # Parse the posted date into year, month, day.
    t_tuple = time.strptime(date_string, DATE_FORMAT)
    t = datetime.datetime(*t_tuple[:6])
    return {
      'year': t.year,
      'month': t.month,
      'day': t.day,
      'unix': int(time.mktime(t_tuple)),
      'formatted': t.strftime(self.site_info['date_format'])
    }


  def load_template(self, name):
    """Loads a template with the given name. Returns a string with the
    template's contents."""
    # Load the special base template first.
    base = open(self.template_root + 'base.html').read()
    # Then populate the contents of the base template with the desired
    # template.
    template = open(self.template_root + name + '.html').read()
    return base.replace('{{{template}}}', template)

  def parse_item(self, path):
    """Parses markup from files like this:

      My new post
      ===========
      type: post
      posted: 2012-03-01 9:00
      slug: my-new-post

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
        "permalink": "/whatever/2012/my-new-post",
      }

      Permalink is computed based on site config too.
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
    data = yaml.load(''.join(yaml_lines)) or {}
    # Process the rest of the post as Markdown.
    markdown_lines = lines[separator_index+1:]
    content = markdown2.markdown(''.join(markdown_lines))
    # Put everything in a dict.
    data['title'] = title
    data['content'] = content
    # Infer slug and type from path.
    slug = 'slug' in data and data['slug'] or self.parse_slug(path)
    type_name = 'type' in data and data['type'] or self.parse_type(path)
    data['slug'] = slug
    data['type'] = type_name
    # Parse the date if it's specified.
    posted_info = None
    if 'posted' in data:
      posted_info = self.parse_date(data['posted'])
      data['posted_info'] = posted_info
    # Compute the permalink.
    data['permalink'] = self.compute_permalink(type_name, slug, posted_info)
    # Return the dict.
    return data

  def parse_slug(self, path):
    """Returns the slug."""
    if path.endswith('index.txt'):
      # If it ends with index, get the second last path component.
      return path.split('/')[-2]
    else:
      # Otherwise, just get the filename.
      return path.split('/')[-1].split('.')[0]

  def parse_type(self, path):
    """Return the type."""
    if path.startswith('./content/pages/'):
      return 'page'
    elif path.startswith('./content/posts/'):
      return 'post'
    elif path.startswith('./content/drafts/'):
      return 'draft'
    elif path.startswith('./content/archives/'):
      return 'archive'

  def parse_site(self):
    """Parses a site.yaml like this:

      title: My awesome blog
      permalinks_format:
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

  def compute_permalink(self, type_name, slug, posted_info=None):
    """Returns the permalink for the given item."""
    permalink_template = self.site_info['permalink_format'][type_name]
    permalink_data = {'slug': slug}
    # If there's date information associated, include it in the permalink data.
    if posted_info:
      permalink_data = dict(permalink_data.items() + posted_info.items())
    return '/' + pystache.render(permalink_template, permalink_data)

  def build(self, item):
    """Builds a single item."""
    info = item['info']
    # TODO: validate the item!
    # Combine the parsed information into template data.
    template_data = dict(info.items() + self.site_info.items())
    # If it's a list, also get the list parameters.
    if 'list' in info:
      limit = 10
      type_filter = 'filter' in info and info['filter']
      items = self.get_list(type_filter, limit)
      template_data['posts'] = items
    # Get the type and load the appropriate template.
    type_name = info['type']
    template = self.load_template(type_name)
    print template
    # Evaluate the template with data.
    html = pystache.render(template, template_data)
    # Compute the final path based on permalink config.
    path = info['permalink']
    # Create the directory for the parsed HTML.
    abs_path = self.output_root + path
    self.mkdir_parents(abs_path)
    # Create the index file inside the directory.
    f = open(abs_path + '/index.html', 'w')
    f.write(html.encode('utf-8'))
    # Copy any assets that should be copied (if applicable).

  def mkdir_parents(self, newdir):
    """Emulates mkdir -p"""
    if os.path.isdir(newdir):
      pass
    elif os.path.isfile(newdir):
      raise OSError("a file with the same name as the desired " \
          "dir, '%s', already exists." % newdir)
    else:
      head, tail = os.path.split(newdir)
      if head and not os.path.isdir(head):
        self.mkdir_parents(head)
      if tail:
        os.mkdir(newdir)

  def archive_output(self, item):
    """Moves the output specified by this item to an archive directory."""
    path = item['info']['permalink']
    # Move it from the output dir into the archive dir.
    src = self.output_root + path
    dst = self.archive_path + path
    # Ensure target archive directory exists.
    dst_dir = os.path.dirname(dst)
    if not os.path.exists(dst_dir):
      self.mkdir_parents(dst_dir)
    os.rename(src, dst)


  def get_list(self, type_filter, limit):
    """Gets list of posts with the given options."""
    # Only care about items with a posted attribute.
    out = [i['info'] for i in self.cache if 'posted' in i['info']]
    # Filter the list of all posts with the given parameters.
    if type_filter:
      out = [i for i in out if i['type'] == type_filter]
    # Order it correctly.
    out = sorted(out, cmp=lambda a, b:
        a['posted_info']['unix'] - b['posted_info']['unix'])
    # Limit the number of results.
    return out[:limit]

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
    # Get the site info.
    self.site_info = self.parse_site()
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
      print 'Nothing to do.'
      return

    # If anything was updated, parse it and update the site cache.
    for item in updated:
      # Update permalink if necessary.
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

    # If something was deleted, archive from output directory.
    for item in deleted:
      self.archive_output(item)
      # Remove this item in the cache.
      cache[:] = [i for i in cache if i['path'] != item['path']]

    # Get all of the lists from the updated cache.
    lists = [i for i in cache if 'list' in i['info']]
    # Distinguish between single and lists posts.
    singles = [i for i in created + updated if 'list' not in i['info']]
    # Build all of the single files.
    for info in singles:
      self.build(info)
    # Build the lists.
    for info in lists:
      self.build(info)

    # Write out the new cache to disk.
    self.save_cache(cache)

if __name__ == '__main__':
  builder = SiteBuilder()
  builder.build_incremental()
