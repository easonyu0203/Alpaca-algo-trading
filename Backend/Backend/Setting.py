

class Setting:
    def __init__(self) -> None:
        
        self._cash_buffer = 2.5 # in percentage
        
    
    @property
    def with_cash_buffer(self):
        return 1 - self._cash_buffer / 100

if __name__ == '__main__':
    setting = Setting()
    print(setting.with_cash_buffer)