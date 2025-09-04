# f = open('encrypted_text.txt', 'r')

shift1 = int(input("Enter a number "))
shift2 = int(input("Enter a number "))

text = input("Enter text to decrypt ")

# text = f.read()
code = ""
for c in text: 
    ascii = ord(c)
    # for i in range(ascii): 
    if 97 <= ascii <= 109 + shift1*shift2: 
        lowercase_char1 = ascii - shift1*shift2
        if 97 <= lowercase_char1 <= 109: 
            code = code + chr(ascii + (shift1 + shift2))
        else: 
            code = code + c
    elif 110 - (shift1 + shift2) <= ascii <= 122 :
        lowercase_char2 = ascii + (shift1 + shift2)
        if 110 <= lowercase_char2 <= 122:
            code = code + chr(ascii + (shift1*shift2))
        else: 
            code = code + c
    elif 65 + shift1 <= ascii <= 77:
        uppercase_char1 = ascii + shift1
        if 65 <= uppercase_char1 <= 77:
            code = code + chr(ascii)
        else: 
            code = code + c
    elif 78 <= ascii <= 90 - shift2**2:
        uppercase_char2 = ascii - shift2**2 
        if 78 <= uppercase_char2 <= 90:
            code = (code + chr(ascii))
        else: 
            code = code + c
    else:
        everything_else = (ascii)
        code = (code + chr(everything_else))

print("Decrypted Text is: ", code)

# with open("decrypted_text.txt", "w") as f: 
#     f.write(code)