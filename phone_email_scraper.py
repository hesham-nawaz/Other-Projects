import re, pyperclip

# Regular Expression for email addresses
e_rex = re.compile(r'''
# some.+_thing@(\d{2,5}))?.com                            

[a-zA-Z0-9_.+]+        # *_____*@_____.___
@        # _____*@*_____.___
[a-zA-Z0-9_.+]+        # _____@*_____.___*

''', re.VERBOSE)


# Regular Expression for phone numbers
p_rex = re.compile(r'''
# DDD-DDD-DDDD, DDD-DDDD, (DDD) DDD-DDDD, DDD-DDDD ext DDDDD, ext., xDDDDD
(
((\d\d\d) | (\(\d\d\d\)))?        # Area Code
(\s|-)        # Dash
\d\d\d        # 1st 3 digits
-        # Dash
\d\d\d\d        # last 4 digits
(((ext(\.)?\s) |x)         # Extension
 (\d){2,5})?     # Extension number
)
''', re.VERBOSE)



# 
text = pyperclip.paste()
# Extract the email/phone from this text
exphone1 = p_rex.findall(text)
exphone = [tup[0] for tup in exphone1]
# Copy the extracted email/phone to the clipboard
exemail = e_rex.findall(text)
results = '\n'.join(exphone) + '\n'.join(exemail)
pyperclip.copy(results)