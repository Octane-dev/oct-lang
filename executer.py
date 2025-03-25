def execute(code_array):
  generated_python_code = "\n".join(code_array)
  exec(generated_python_code)
