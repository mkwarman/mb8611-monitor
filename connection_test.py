class ConnectionTest:
  timeTakenMS = None
  success = None
  error = None

  def __init__(self, timeTakenMS, success, error):
    self.timeTakenMS = timeTakenMS if timeTakenMS is not None else -1
    self.success = success
    self.error = error if error is not None else ""