import bcrypt

password = "@shraddha07".encode()
hashed = bcrypt.hashpw(password, bcrypt.gensalt())
print(hashed.decode())
