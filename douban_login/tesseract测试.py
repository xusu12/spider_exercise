from PIL import Image
import tesserocr

image = Image.open("douban_login.jpg")  # 获取图片
# image = Image.open("2.png")  # 获取图片

# 先将原图进行灰度处理  然后再进行二值化处理
# 将图片转化为灰度图像
image = image.convert('L')

# 再将图片进行二值化处理
# 指定二值化的阈值
threshold = 25
table = []
for i in range(256):
    if i < threshold:
        table.append(0)
    else:
        table.append(1)
image = image.point(table, '1')
image.show()

print(tesserocr.image_to_text(image))
