import random
import string

def generateRandomString(length=8, chars="0123456789"):
    return ''.join([random.choice(chars) for i in range(length)])

random.seed()

entry_format = """<tr><td>{}</td><td>{}</td></tr>"""
entry_num = random.randint(1,10)
entry_buffer = ""
for i in range(entry_num):
    entry_buffer = entry_buffer + entry_format.format(generateRandomString(8), generateRandomString(8))

output_format = """<html>
<head><title>{}</title></head>
<body>
    <table><tr><td>Name</td><td>Age</td></tr>
    {}</table>
</body>
</html>""".format(generateRandomString(16), entry_buffer)
print(output_format)
