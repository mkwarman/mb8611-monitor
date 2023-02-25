from datetime import datetime

class ConnectionTest:
  time = None
  timeTakenMS = None
  success = None
  error = None

  def __init__(self, timeTakenMS, success, error):
    self.time = datetime.now().isoformat()
    self.timeTakenMS = timeTakenMS if timeTakenMS is not None else -1
    self.success = success
    self.error = error if error is not None else ""

  def serialize_for_insertion(self):
    return {
      "Time": self.time,
      "TimeTakenMS": self.timeTakenMS,
      "Success": self.success,
      "Error": self.error
    }