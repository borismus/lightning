class SiteBuilder:
  pass


def RenderTemplate(filename, data):
  env = Environment(loader=FileSystemLoader(self.template_root))
  try:
    template = env.get_template(filename)
  except Exception:
    raise Exception('Failed to find template %s.' % filename)
  try:
    out = template.render(data)
  except Exception as e:
    raise Exception('Failed to render template %s: "%s".' % (filename, e))

  return out
