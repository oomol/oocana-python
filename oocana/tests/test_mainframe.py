import unittest
from oocana import Mainframe
from oocana import JobDict
class TestMainframe(unittest.TestCase):

  __mainframe: Mainframe
  __job_info: JobDict = {
    #  broker 里对这两个字段的 send 做了特殊兼容，需要固定值。
    'session_id': '123',
    'job_id': '123',
  }

  def setUp(self):
    self.__mainframe = Mainframe('mqtt://localhost:47688')
    self.__mainframe.connect()
  
  def tearDown(self) -> None:
     assert self.__mainframe is not None
     self.__mainframe.disconnect()
     return super().tearDown()

  # def test_send(self):
  #   info = self.__mainframe.send(self.__job_info, {
  #     'dir': '123',
  #   })

  #   info.wait_for_publish()

  # def test_send_ready(self):
  #   self.__mainframe.notify_ready('123', '123')

# 激活虚拟环境后，执行以下命令：
# python -m unittest oocana/tests/mainframe_test.py
# python -m unittest oocana.tests.mainframe_test.TestMainframe.[单个方法名]
if __name__ == '__main__':
    unittest.main()
