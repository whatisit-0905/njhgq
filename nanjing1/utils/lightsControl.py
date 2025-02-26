


if __name__ == "__main__":
    """
    
    第 1 位	 第 2 位	 第 3-6 位	 第 7 位

    W:写指令 通 道 数： A/B 
             分 别 代 表   CH1/CH2	
    0000-0999 四位亮度值	
    T:  光源亮

    F:  光源灭
    """
    message = "WA0999T"  #T是亮，0123是亮度，W是写，第二位A/B是ch1或者ch2
    ip = "192.168.0.110"
    port = 3205
    
    send_udp_message(message, ip, port)
