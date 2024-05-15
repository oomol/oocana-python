import unittest
import asyncio
from .mainframe import Mainframe
from .data import JobDict
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

  def test_send(self):
    self.__mainframe.send(self.__job_info, {
      'dir': '123',
    })

  def test_resend(self):
      asyncio.run(self.send_after_disconnect())

  async def send_after_disconnect(self):
    self.__mainframe.send(self.__job_info, {
      'dir': '123',
    })
    await asyncio.sleep(10)
    self.__mainframe.send(self.__job_info, {
      'dir': '123',
    })

  def test_send_twice(self):

    self.__mainframe.notify_ready({
       **self.__job_info,
      'dir': '123',
    })
    self.__mainframe.send(self.__job_info, {
      'dir': '123',
    })
    self.__mainframe.send(self.__job_info, {
      'dir': '123',
    })



# 激活虚拟环境后，执行以下命令：
# python -m unittest src/vocana/mainframe_test.py
# python -m unittest src.vocana.mainframe_test.TestMainframe.[单个方法名]
if __name__ == '__main__':
    unittest.main()
