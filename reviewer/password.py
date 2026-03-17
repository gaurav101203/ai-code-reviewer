usernames = ["gaurav", "smit", "karan", "aadi"]
user_passwords = ["heugfwdjehi", "dghwiuqhoq", "5454534hfehf", "hdwoioqjqlfm"]
combination = []
for i in range(len(usernames)):
    combination.append(usernames[i] + user_passwords[i])
print(combination)