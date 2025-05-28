import subprocess

class SEOMetaData:
  def __init__(self, sitetitle, description, image):
    self.sitetitle = sitetitle
    self.description = description
    self.toolname = subprocess.check_output('whoami',text=True).strip()    
    self.url = "https://%s.pythonanywhere.com" % self.toolname
    self.favicon = "%s/%s" % (self.url,'static/favicon.png')
    self.image = "%s/static/preview.png" % self.url