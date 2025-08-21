name = "jeswin pj"
age = "22"
marks = [80.5,90.7,99.9]
details = {"name":name,"age":age,"marks":marks}
print("data types of each values")
print(type(details["name"]),type(details["age"]),type(details["marks"]))
total_marks = sum(marks)
avg_marks = total_marks / len(marks)
print("marks")
print("total marks : ",total_marks)
print("avrage marks : ",avg_marks)
if avg_marks >=40:
    pased = True
    print("student is passed")
else:
  print("student is failed")
  pased = False
print("individual marks")
for i in range (len(marks)):
   print("sub",i+1,":",marks[i])
set = set(marks)
print(" marks : ",set)
sub=("maths","science","english")
print("subjects (tuple):",sub)
remark=None
print("Remarks : ",remark,type(remark))
print("passed",pased,type(pased))

print("Student Report")
print("**********************")
print(f"Name     : {name}")
print(f"Age      : {age}")
print(f"Marks    : {marks}")
print(f"Total    : {total_marks}")
print(f"Result   : {'Passed' if avg_marks >= 40 else 'Failed'}")
