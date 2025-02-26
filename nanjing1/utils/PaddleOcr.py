import paddlehub as hub
from fuzzywuzzy import fuzz
import time
import cv2
import base64

def match_with_options(extracted_value, options):
    if extracted_value == "0":
        return "信息提取失败！"
    best_match = None
    highest_similarity = 0
    for option,value in options.items():
        similarity = fuzz.ratio(extracted_value, option)
        if similarity > highest_similarity:
            highest_similarity = similarity
            best_match = option
    res_dict = options[best_match]
    res_dict["型号"] = best_match
    return res_dict

class MyPaddleOcr:
    def __init__(self) -> None:#初始化OCR模型、型号模型及相关信息、关键词模型
        self.ocr = hub.Module(name="ch_pp-ocrv3", enable_mkldnn=True)
        self.known_models = {
            "LJZW1-35": {"额定电流比(A)": "800/5", "额定容量(VA)": "15"},#type 1
            "JDZXN-10": {"额定电压比(KV)": "10/√3/0.1/√3", "额定容量(VA)": "20/2.5"},#type 2
            "LJZN1-10": {"电流比": "30/1", "二次负荷": "2.5/1"},#type 3
            "JDZXW-35": {"额定电压比(KV)": "35/√3/0.1/√3", "额定容量(VA)": "20/2.5"},#type 4
            "LJW1-10": {"额定电流比(A)": "1200/5", "额定容量(VA)": "15"},#type 5
            "JDZQW-10": {"额定电压比(KV)": "10/0.1", "额定容量(VA)": "20/2.5"},#type 6

            "LMZ(4)D-0.66": {"电流比": "1500/5", "二次负荷": "5VA/3.75VA"},
            "LMZ(3)D-0.66": {"电流比": "600/5", "二次负荷": "5VA/3.75VA"},
            "LMZ2D-0.66": {"电流比": "500/5A", "二次负荷": "5/2.5VA"},
            "LMZ6D-0.66": {"电流比": "75A/5A", "二次负荷": "10/3.75VA"},
            "LZZBJ9-10": {"电流比": "20/5", "二次负荷": "NONE"},
        }
        self.keywords = ['型号']

    def imgOcr(self, path):
        timeNow = time.time()
        if isinstance(path, str):#检查路径是否为str
            img = [cv2.imread(path)]
        else:
            img = [path]
        getObj = self.ocr.recognize_text(images=img)[0]#取第一个返回结果
        textList = getObj['data']
        result = ""#最终结果字符串
        for text in textList:
            result += text['text']
            result += "\n"
        result = self.text_process(result)
        print('文本:', result)
        result = self.extract_values(result)
        print('提取:', result)
        result = self.match(result)
        return result

    def is_chinese_char(self, char):#判断是否为中文字符
        if '\u4e00' <= char <= '\u9fff':
            return True
        return False

    def text_process(self, text=""):
        text = text.replace("：", "").replace(" ", "").replace(":", "")
        text = text.replace("（", "(").replace("）", ")")
        text = text.replace("（", "(").replace("）", ")")
        text = text.replace("\n", "换行")
        result = ''
        prev_is_chinese = False
        for char in text:
            is_chinese = self.is_chinese_char(char)
            if is_chinese and not prev_is_chinese:#在中文和非中文之间＋符号
                result += '***'
            elif not is_chinese and prev_is_chinese:#在中文和非中文之间＋符号
                result += '***'
            result += char
            prev_is_chinese = is_chinese
        print('识别结果:', result)
        return result

    def extract_values(self, formatted_text):
        values = {"电流比": "0", "二次负荷": "0", "型号": "0"}
        for keyword in self.keywords:
            index = formatted_text.find(keyword)
            if index != -1:
                value_start = index + len(keyword)
                value_end = value_start
                
                # 寻找值的结束位置
                while value_end < len(formatted_text) and not self.is_chinese_char(formatted_text[value_end]):
                    value_end += 1
                
                # 确保不会越界
                if value_end > value_start:
                    value = formatted_text[value_start:value_end].strip()
                    if keyword == '型号':
                        values["型号"] = value
        
        return values

    def match(self, extracted_info):
        res = match_with_options(extracted_info['型号'], self.known_models)
        if isinstance(res, str):#检查路径是否为str
            return res
        if isinstance(res, dict):#检查路径是否为dict
            return '\n'.join(f"{k}: {v}" for k, v in res.items())

if __name__ == "__main__":
    OCR = MyPaddleOcr()
    import os
    for file in os.listdir(r"C:\Users\Administrator\MVS\Data\ocr"):
        file_path = os.path.join(r"C:\Users\Administrator\MVS\Data\ocr", file)
        file_path = os.path.join(r"C:\Users\Administrator\MVS\Data\ocr", "Image_20240923144450969.bmp")
        if file_path.endswith('bmp'):
            # file_path = r"six_types\mp"
            img = cv2.imread(file_path)
            img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
            info = OCR.imgOcr(path=img)
            print(info)
            print(file)
            input("wait")

