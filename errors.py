class SyntaxError(Exception):
  def __init__(self, message, line_number, filename):
      self.message = message
      self.line_number = line_number
      self.filename = filename

  def __str__(self):
      return f"SyntaxError: {self.message} at line {self.line_number} in file {self.filename}"
